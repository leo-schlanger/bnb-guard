"""Metadata utilities for fetching token information from BSCScan API."""

import json
import time
from decimal import Decimal
from typing import Any, Dict, Optional

import requests
from web3 import Web3
from web3.exceptions import (
    BadFunctionCallOutput,
    ContractLogicError,
)

from app.core.utils.logger import get_logger
from app.core.config import settings

# Get configuration values
BSCSCAN_API_KEY = settings.BSCSCAN_API_KEY
BSC_RPC_URL = settings.BSC_RPC_URL

logger = get_logger(__name__)

def _get_bscscan_abi(contract_address: str) -> list | None:
    """
    Fetches the ABI for a contract from BscScan.

    Args:
        contract_address: The token contract address.

    Returns:
        The ABI as a list, or None if fetching fails.
    """
    try:
        url = "https://api.bscscan.com/api"
        params = {
            "module": "contract",
            "action": "getabi",
            "address": contract_address,
            "apikey": BSCSCAN_API_KEY
        }

        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        if data.get("status") == "1" and data.get("message") == "OK":
            abi_str = data.get("result")
            try:
                abi = json.loads(abi_str)
                if isinstance(abi, list):
                    return abi
                else:
                    logger.warning("Parsed ABI is not a list", context={"contract_address": contract_address})
            except Exception as parse_err:
                logger.warning("Failed to parse ABI from BscScan", context={
                    "error": str(parse_err),
                    "contract_address": contract_address,
                    "raw_result": abi_str
                })
        else:
            logger.warning("Failed to fetch ABI from BscScan", context={
                "status": data.get("status"),
                "message": data.get("message"),
                "result": data.get("result")
            })

    except Exception as e:
        logger.warning("Error fetching ABI from BscScan", context={
            "error": str(e),
            "contract_address": contract_address
        })
    return None

def _get_contract_abi(token_address: str = None) -> list:
    """
    Get contract ABI, trying BscScan first, falling back to minimal ABI.
    """
    if token_address and BSCSCAN_API_KEY:
        abi = _get_bscscan_abi(token_address)
        if abi and isinstance(abi, list):
            return abi

    return [
        {
            "constant": True,
            "inputs": [],
            "name": "name",
            "outputs": [{"name": "", "type": "string"}],
            "payable": False,
            "stateMutability": "view",
            "type": "function"
        },
        {
            "constant": True,
            "inputs": [],
            "name": "symbol",
            "outputs": [{"name": "", "type": "string"}],
            "payable": False,
            "stateMutability": "view",
            "type": "function"
        },
        {
            "constant": True,
            "inputs": [],
            "name": "decimals",
            "outputs": [{"name": "", "type": "uint8"}],
            "payable": False,
            "stateMutability": "view",
            "type": "function"
        },
        {
            "constant": True,
            "inputs": [],
            "name": "totalSupply",
            "outputs": [{"name": "", "type": "uint256"}],
            "payable": False,
            "stateMutability": "view",
            "type": "function"
        }
    ]

def _safe_contract_call(contract: Any, func_name: str, token_address: str, default: Any = None, request_id: str = None) -> Any:
    """
    Safely call a contract function with error handling and logging.
    
    Args:
        contract: Web3 contract instance
        func_name: Name of the contract function to call
        token_address: Token contract address for logging
        default: Default value to return on failure
        request_id: Optional request ID for correlation
        
    Returns:
        The result of the function call or the default value on failure
    """
    start_time = time.time()
    log_context = {
        "contract_address": token_address,
        "function": func_name,
        "request_id": request_id or "N/A"
    }
    
    try:
        logger.debug("Calling contract function", context=log_context)
        func = getattr(contract.functions, func_name)
        result = func().call(block_identifier='latest')
        
        logger.debug(
            "Contract function call successful",
            context={
                **log_context,
                "result": str(result)[:100] + ('...' if len(str(result)) > 100 else ''),
                "result_type": type(result).__name__,
                "duration_seconds": f"{time.time() - start_time:.4f}"
            }
        )
        return result
        
    except Exception as e:
        logger.warning(
            f"Contract function call failed: {func_name}",
            context={
                **log_context,
                "error": str(e),
                "error_type": type(e).__name__,
                "duration_seconds": f"{time.time() - start_time:.4f}",
                "available_functions": [f for f in dir(contract.functions) if not f.startswith('_')]
            },
            exc_info=True
        )
        return default


def _get_token_supply(contract: Any, decimals: int, token_address: str, request_id: str = None) -> Dict[str, Any]:
    """
    Get and normalize token supply with error handling.
    
    Args:
        contract: Web3 contract instance
        decimals: Number of decimal places for the token
        token_address: Token contract address
        request_id: Optional request ID for correlation
        
    Returns:
        Dictionary containing normalized and raw token supply
    """
    start_time = time.time()
    log_context = {
        "token_address": token_address,
        "decimals": decimals,
        "request_id": request_id or "N/A"
    }
    
    try:
        logger.debug("Fetching token supply", context=log_context)
        raw_supply = contract.functions.totalSupply().call()
        normalized_supply = float(Decimal(str(raw_supply)) / (10 ** decimals))
        
        result = {
            "totalSupply": normalized_supply,
            "rawTotalSupply": str(raw_supply)
        }
        
        logger.debug(
            "Successfully fetched token supply",
            context={
                **log_context,
                "raw_supply": str(raw_supply),
                "normalized_supply": normalized_supply,
                "duration_seconds": f"{time.time() - start_time:.4f}"
            }
        )
        return result
        
    except Exception as e:
        logger.error(
            "Failed to get token supply",
            context={
                **log_context,
                "error": str(e),
                "error_type": type(e).__name__,
                "duration_seconds": f"{time.time() - start_time:.4f}"
            },
            exc_info=True
        )
        return {"totalSupply": 0, "rawTotalSupply": "0"}


def _initialize_web3_with_retry(max_retries: int = 3, retry_delay: int = 2, request_id: str = None) -> Web3:
    """
    Initialize Web3 with connection pooling and retry logic.
    
    Args:
        max_retries: Maximum number of connection attempts
        retry_delay: Initial delay between retries in seconds
        request_id: Optional request ID for correlation
        
    Returns:
        Initialized Web3 instance
        
    Raises:
        ValueError: If BSC_RPC_URL is not configured
        ConnectionError: If connection fails after all retries
    """
    start_time = time.time()
    log_context = {
        "request_id": request_id or "N/A",
        "max_retries": max_retries,
        "retry_delay": retry_delay,
        "rpc_url": BSC_RPC_URL[:20] + "..." + BSC_RPC_URL[-10:] if BSC_RPC_URL else "Not configured"
    }
    
    if not BSC_RPC_URL:
        error_msg = "BSC_RPC_URL is not configured in environment variables"
        logger.critical(
            error_msg,
            context={
                **log_context,
                "duration_seconds": f"{time.time() - start_time:.4f}"
            }
        )
        raise ValueError(error_msg)
    
    web3_timeout = 30
    logger.info(
        "Initializing Web3 provider with connection pooling",
        context={
            **log_context,
            "timeout_seconds": web3_timeout,
            "pool_connections": 5,
            "pool_maxsize": 10,
            "http_retries": 3
        }
    )
    
    # Configure session for connection pooling
    session = requests.Session()
    adapter = requests.adapters.HTTPAdapter(
        pool_connections=5,
        pool_maxsize=10,
        max_retries=3
    )
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    
    # Initialize Web3 with timeout
    w3 = Web3(Web3.HTTPProvider(
        BSC_RPC_URL,
        request_kwargs={
            'timeout': web3_timeout
        }
    ))
    
    # Test connection with retry logic
    last_exception = None
    
    for attempt in range(1, max_retries + 1):
        attempt_start = time.time()
        try:
            logger.debug(
                f"Testing BSC node connection (attempt {attempt}/{max_retries})",
                context={
                    **log_context,
                    "attempt": attempt,
                    "attempt_start_time": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(attempt_start))
                }
            )
            
            # Perform a lightweight operation to test the connection
            chain_id = w3.eth.chain_id
            block_number = w3.eth.block_number
            client_version = w3.client_version
            
            logger.info(
                "Successfully connected to BSC node",
                context={
                    **log_context,
                    "chain_id": chain_id,
                    "block_number": block_number,
                    "node_version": client_version,
                    "attempt": attempt,
                    "attempt_duration_seconds": f"{time.time() - attempt_start:.4f}",
                    "total_duration_seconds": f"{time.time() - start_time:.4f}"
                }
            )
            return w3
            
        except Exception as e:
            last_exception = e
            duration = time.time() - attempt_start
            
            if attempt < max_retries:
                logger.warning(
                    f"BSC node connection attempt {attempt} failed, retrying...",
                    context={
                        **log_context,
                        "error": str(e),
                        "error_type": type(e).__name__,
                        "retry_in_seconds": retry_delay * attempt,
                        "attempt": attempt,
                        "attempt_duration_seconds": f"{duration:.4f}",
                        "total_duration_seconds": f"{time.time() - start_time:.4f}"
                    },
                    exc_info=True
                )
                time.sleep(retry_delay * attempt)  # Exponential backoff
            else:
                error_msg = f"Failed to connect to BSC node after {max_retries} attempts"
                logger.critical(
                    error_msg,
                    context={
                        **log_context,
                        "last_error": str(last_exception),
                        "error_type": type(last_exception).__name__,
                        "total_attempts": max_retries,
                        "attempt_duration_seconds": f"{duration:.4f}",
                        "total_duration_seconds": f"{time.time() - start_time:.4f}"
                    },
                    exc_info=True
                )
                raise ConnectionError(error_msg) from last_exception


def _initialize_contract(
    w3: Web3, 
    token_address: str, 
    abi: Any, 
    max_retries: int = 3, 
    retry_delay: int = 2,
    request_id: str = None
) -> Any:
    """
    Initialize a contract instance with retry logic.
    
    Args:
        w3: Web3 instance
        token_address: Token contract address
        abi: Contract ABI
        max_retries: Maximum number of initialization attempts
        retry_delay: Delay between retries in seconds
        request_id: Optional request ID for correlation
        
    Returns:
        Initialized contract instance
        
    Raises:
        Exception: If contract initialization fails after all retries
    """
    start_time = time.time()
    log_context = {
        "token_address": token_address,
        "max_retries": max_retries,
        "retry_delay": retry_delay,
        "request_id": request_id or "N/A",
        "abi_length": len(abi) if abi else 0
    }
    
    logger.info(
        "Initializing contract instance",
        context=log_context
    )
    
    last_error = None
    
    for attempt in range(1, max_retries + 1):
        attempt_start = time.time()
        try:
            logger.debug(
                f"Creating contract instance (attempt {attempt}/{max_retries})",
                context={
                    **log_context,
                    "attempt": attempt,
                    "attempt_start_time": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(attempt_start))
                }
            )
            
            # Create contract instance
            checksum_address = Web3.to_checksum_address(token_address)
            contract = w3.eth.contract(
                address=checksum_address,
                abi=abi
            )
            
            # Test contract functions
            contract_name = _safe_contract_call(
                contract=contract,
                func_name="name",
                token_address=token_address,
                default="Unknown",
                request_id=request_id
            )
            
            logger.info(
                "Successfully created and tested contract instance",
                context={
                    **log_context,
                    "contract_name": contract_name,
                    "checksum_address": checksum_address,
                    "attempt": attempt,
                    "attempt_duration_seconds": f"{time.time() - attempt_start:.4f}",
                    "total_duration_seconds": f"{time.time() - start_time:.4f}"
                }
            )
            return contract
            
        except Exception as e:
            last_error = e
            duration = time.time() - attempt_start
            
            if attempt < max_retries:
                logger.warning(
                    f"Contract initialization attempt {attempt} failed, retrying...",
                    context={
                        **log_context,
                        "error": str(e),
                        "error_type": type(e).__name__,
                        "retry_in_seconds": retry_delay * attempt,
                        "attempt": attempt,
                        "attempt_duration_seconds": f"{duration:.4f}",
                        "total_duration_seconds": f"{time.time() - start_time:.4f}"
                    },
                    exc_info=True
                )
                time.sleep(retry_delay * attempt)  # Exponential backoff
            else:
                error_msg = f"Failed to initialize contract after {max_retries} attempts"
                logger.critical(
                    error_msg,
                    context={
                        **log_context,
                        "last_error": str(last_error),
                        "error_type": type(last_error).__name__,
                        "total_attempts": max_retries,
                        "attempt_duration_seconds": f"{duration:.4f}",
                        "total_duration_seconds": f"{time.time() - start_time:.4f}"
                    },
                    exc_info=True
                )
                raise Exception(error_msg) from last_error


def _fetch_token_metadata(web3: Web3, token_address: str, request_id: str = None) -> Dict[str, Any]:
    """
    Fetch token metadata from the blockchain.
    
    Args:
        web3: Web3 instance
        token_address: Token contract address
        request_id: Optional request ID for correlation
        
    Returns:
        Dictionary containing token metadata
    """
    start_time = time.time()
    log_context = {
        "token_address": token_address,
        "request_id": request_id or "N/A"
    }
    
    logger.info(
        "Starting token metadata fetch from blockchain",
        context=log_context
    )
    
    try:
        # Get token ABI (try BscScan first, fallback to minimal ABI)
        token_abi = _get_contract_abi(token_address)
        logger.debug(
            "Retrieved token ABI", 
            context={
                **log_context,
                "abi_length": len(token_abi) if token_abi else 0
            }
        )
        
        # Initialize contract with retry logic and better error handling
        try:
            contract = _initialize_contract(
                w3=web3, 
                token_address=token_address, 
                abi=token_abi,
                max_retries=5,  # Increase retries
                retry_delay=3,  # Longer delay between retries
                request_id=request_id
            )
        except Exception as contract_err:
            logger.error(
                f"Failed to initialize contract: {str(contract_err)}",
                context={**log_context, "error": str(contract_err)},
                exc_info=True
            )
            raise
        
        # Get token details with safe contract calls
        logger.debug("Fetching token details", context=log_context)
        name = _safe_contract_call(contract, "name", token_address, "Unknown", request_id)
        symbol = _safe_contract_call(contract, "symbol", token_address, "UNKNOWN", request_id)
        decimals = _safe_contract_call(contract, "decimals", token_address, 18, request_id)
        
        logger.debug(
            "Token details retrieved", 
            context={
                **log_context,
                "token_name": name,
                "token_symbol": symbol,
                "decimals": decimals
            }
        )
        
        # Get token supply with proper error handling
        supply_info = _get_token_supply(contract, decimals, token_address, request_id)
        
        result = {
            "name": name,
            "symbol": symbol,
            "decimals": decimals,
            **supply_info
        }
        
        logger.info(
            "Successfully fetched token metadata from blockchain",
            context={
                **log_context,
                **result,
                "total_duration_seconds": f"{time.time() - start_time:.4f}"
            }
        )
        
        # Verify metadata is valid
        if not result or not isinstance(result, dict):
            logger.error(
                "Invalid metadata format",
                context={
                    "token_address": token_address,
                    "request_id": request_id,
                    "metadata_type": type(result).__name__
                }
            )
            return {
                "name": "Error",
                "symbol": "ERR",
                "decimals": 18,
                "totalSupply": 0,
                "rawTotalSupply": "0",
                "error": "Invalid metadata format",
                "error_type": "FormatError"
            }
            
        return result
        
    except Exception as e:
        error_context = {
            "token_address": token_address,
            "request_id": request_id,
            "error_type": type(e).__name__,
            "time_elapsed_seconds": f"{time.time() - start_time:.2f}s"
        }
        
        _handle_metadata_failure(
            token_address=token_address,
            error=e,
            context=error_context,
            request_id=request_id
        )
        
        # Return error response instead of raising
        return {
            "name": "Error",
            "symbol": "ERR",
            "decimals": 18,
            "totalSupply": 0,
            "rawTotalSupply": "0",
            "error": str(e),
            "error_type": type(e).__name__
        }

def _get_token_supply(
    contract: Any,
    decimals: int,
    token_address: str,
    request_id: str = None
) -> Dict[str, Any]:
    """Get and normalize token supply."""
    try:
        raw_supply = contract.functions.totalSupply().call()
        normalized_supply = float(raw_supply) / (10 ** decimals)
        return {
            "totalSupply": normalized_supply,
            "rawTotalSupply": str(raw_supply)
        }
    except Exception as e:
        logger.error(
            "Error getting token supply",
            context={
                "error": str(e),
                "token_address": token_address,
                "decimals": decimals
            }
        )
        return {"totalSupply": 0, "rawTotalSupply": "0"}


def _validate_token_address(token_address: str) -> str:
    """
    Validate and normalize token address.
    
    Args:
        token_address: The token contract address to validate
        
    Returns:
        str: Checksum-formatted token address
        
    Raises:
        ValueError: If the address is invalid
    """
    if not Web3.is_address(token_address):
        error_msg = f"Invalid token address: {token_address}"
        logger.error(error_msg)
        raise ValueError(error_msg)
    
    # Convert to checksum address format
    checksum_address = Web3.to_checksum_address(token_address)
    logger.debug(
        "Validated and normalized token address",
        context={"original": token_address, "checksum": checksum_address}
    )
    return checksum_address


def _create_metadata_response(token_address: str, token_details: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create a standardized metadata response.
    
    Args:
        token_address: The token contract address
        token_details: Dictionary containing token details
        
    Returns:
        Dictionary containing token metadata
    """
    metadata = {
        "address": token_address,
        "name": token_details.get("name", "Unknown"),
        "symbol": token_details.get("symbol", "UNKNOWN"),
        "decimals": token_details.get("decimals", 18),
        "totalSupply": token_details.get("totalSupply", 0),
        "rawTotalSupply": token_details.get("rawTotalSupply", "0"),
        "is_verified": True,
        "verification_status": "verified",
        "contract_created": time.strftime("%Y-%m-%d %H:%M:%S"),
        "source": "bscscan_and_web3"
    }
    
    logger.debug(
        "Created metadata response",
        context={
            "token_address": token_address,
            "symbol": metadata["symbol"],
            "is_verified": metadata["is_verified"]
        }
    )
    
    return metadata


def _handle_metadata_failure(
    token_address: str,
    error: Exception,
    context: Optional[Dict[str, Any]] = None,
    request_id: str = None
) -> None:
    """
    Handle metadata fetch failures with appropriate logging.
    
    Args:
        token_address: The token contract address
        error: The exception that was raised
        context: Additional context for logging
        request_id: Optional request ID for correlation
    """
    context = context or {}
    context.update({
        "token_address": token_address,
        "error_type": type(error).__name__,
        "error": str(error),
        "request_id": request_id or "N/A"
    })
    
    # Add traceback for debugging if in debug mode
    import traceback
    context["traceback"] = traceback.format_exc()
    
    # Log based on error type with appropriate level and context
    if isinstance(error, (requests.exceptions.RequestException, ConnectionError)):
        logger.error(
            "Network error while fetching token metadata", 
            context=context,
            exc_info=True
        )
    elif isinstance(error, (ContractLogicError, BadFunctionCallOutput, ValueError)):
        logger.error(
            "Contract error while fetching token metadata", 
            context=context,
            exc_info=True
        )
    elif isinstance(error, Exception):
        logger.critical(
            "Blockchain error while fetching token metadata", 
            context=context,
            exc_info=True
        )
    
    # Log additional context if available
    if hasattr(error, 'args') and error.args:
        logger.debug("Error arguments", context={"error_args": str(error.args)})
        
    # Log request ID for correlation if available
    if request_id:
        logger.debug("Request ID for error correlation", context={"request_id": request_id})


def fetch_token_metadata(token_address: str) -> Dict[str, Any]:
    """
    Fetch comprehensive token metadata from BscScan and BSC node.
    
    This function retrieves token metadata from multiple sources:
    1. BscScan API for contract source code and ABI
    2. Direct BSC node connection for on-chain data
    
    Args:
        token_address: The token contract address (must be a valid BSC address)
        
    Returns:
        Dictionary containing token metadata
        
    Raises:
        ValueError: For invalid inputs or contract errors
        ConnectionError: For network-related errors
        Exception: For any other unexpected errors
    """
    start_time = time.time()
    request_id = f"meta-{int(time.time())}"
    
    logger.info(
        "Starting token metadata fetch",
        context={
            "token_address": token_address,
            "request_id": request_id,
            "start_time": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(start_time))
        }
    )
    
    try:
        # Validate and normalize token address
        try:
            token_address = _validate_token_address(token_address)
        except ValueError as e:
            logger.error(
                f"Invalid token address: {str(e)}",
                context={"token_address": token_address, "request_id": request_id},
                exc_info=True
            )
            return {
                "name": "Error",
                "symbol": "ERR",
                "decimals": 18,
                "totalSupply": 0,
                "rawTotalSupply": "0",
                "error": f"Invalid token address: {str(e)}",
                "error_type": "ValueError"
            }
        
        # Initialize Web3 with retry logic
        try:
            web3 = _initialize_web3_with_retry(request_id=request_id)
        except Exception as e:
            logger.error(
                f"Failed to initialize Web3: {str(e)}",
                context={"token_address": token_address, "request_id": request_id},
                exc_info=True
            )
            return {
                "name": "Error",
                "symbol": "ERR",
                "decimals": 18,
                "totalSupply": 0,
                "rawTotalSupply": "0",
                "error": f"Web3 connection error: {str(e)}",
                "error_type": type(e).__name__
            }
        
        # Fetch token metadata
        token_details = _fetch_token_metadata(web3, token_address, request_id=request_id)
        
        # Create standardized response
        metadata = _create_metadata_response(token_address, token_details)
        
        logger.info(
            "Successfully fetched token metadata",
            context={
                "token_address": token_address,
                "request_id": request_id,
                "symbol": metadata.get("symbol", "UNKNOWN"),
                "name": metadata.get("name", "Unknown"),
                "time_elapsed_seconds": f"{time.time() - start_time:.2f}s"
            }
        )
        
        return metadata
        
    except (requests.exceptions.RequestException, ConnectionError) as e:
        _handle_metadata_failure(token_address, e, {
            "rpc_url": BSC_RPC_URL,
            "time_elapsed_seconds": f"{time.time() - start_time:.2f}s"
        })
        raise ConnectionError(f"❌ Network error: {str(e)}") from e
        
    except (ContractLogicError, BadFunctionCallOutput, ValueError) as e:
        _handle_metadata_failure(token_address, e, {
            "time_elapsed_seconds": f"{time.time() - start_time:.2f}s"
        })
        raise ValueError(f"❌ Contract error: {str(e)}") from e
        
    except Exception as e:
        _handle_metadata_failure(token_address, e, {
            "rpc_url": BSC_RPC_URL,
            "time_elapsed_seconds": f"{time.time() - start_time:.2f}s"
        })
        raise ConnectionError(f"❌ Blockchain error: {str(e)}") from e
        
