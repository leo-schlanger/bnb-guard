import json
import time
from decimal import Decimal
from typing import Any, Dict, Optional, Tuple

import requests
from web3 import Web3
from web3.exceptions import (
    BadFunctionCallOutput,
    ContractLogicError,
    Web3Exception,
)

from app.core.interfaces.analyzer import TokenMetadata
from app.core.utils.logger import get_logger
from config import BSCSCAN_API_KEY, BSC_RPC_URL

logger = get_logger(__name__)

def _get_bscscan_abi(contract_address: str) -> Optional[list]:
    """
    Fetch contract ABI from BscScan API.
    
    Args:
        contract_address: The contract address to fetch ABI for
        
    Returns:
        list: The contract ABI or None if not found
    """
    if not BSCSCAN_API_KEY:
        logger.warning("BSCSCAN_API_KEY not configured")
        return None
        
    url = f"https://api.bscscan.com/api"
    params = {
        "module": "contract",
        "action": "getabi",
        "address": contract_address,
        "apikey": BSCSCAN_API_KEY
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if data["status"] == "1" and data["message"] == "OK":
            return json.loads(data["result"])
            
        logger.warning("Failed to fetch ABI from BscScan", context={
            "status": data.get("status"),
            "message": data.get("message"),
            "result": data.get("result")
        })
        return None
        
    except Exception as e:
        logger.warning("Error fetching ABI from BscScan", context={
            "error": str(e),
            "contract_address": contract_address
        })
        return None


def _get_contract_abi(token_address: str = None) -> list:
    """
    Get contract ABI, trying BscScan first, falling back to minimal ABI.
    
    Args:
        token_address: The token contract address (optional)
        
    Returns:
        list: The contract ABI
    """
    # Try to get ABI from BscScan if token address is provided
    if token_address and BSCSCAN_API_KEY:
        abi = _get_bscscan_abi(token_address)
        if abi:
            return abi
    
    # Fallback to minimal ABI
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
    
    # Initialize Web3 with the session
    w3 = Web3(Web3.HTTPProvider(
        BSC_RPC_URL,
        request_kwargs={
            'timeout': web3_timeout,
            'session': session
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
        
        contract = _initialize_contract(
            w3=web3, 
            token_address=token_address, 
            abi=token_abi,
            request_id=request_id
        )
        
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
        
        return result
        
    except Exception as e:
        _handle_metadata_failure(
            token_address=token_address,
            error=e,
            context={
                **log_context,
                "duration_seconds": f"{time.time() - start_time:.4f}"
            },
            request_id=request_id
        )
        
        # Return default values on failure
        return {
            "name": "Unknown",
            "symbol": "UNKNOWN",
            "decimals": 18,
            "totalSupply": 0,
            "rawTotalSupply": "0"
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


def _create_metadata_response(token_address: str, token_details: Dict[str, Any]) -> TokenMetadata:
    """
    Create a standardized metadata response.
    
    Args:
        token_address: The token contract address
        token_details: Dictionary containing token details
        
    Returns:
        TokenMetadata: Standardized token metadata
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
    elif isinstance(error, Web3Exception):
        logger.critical(
            "Blockchain error while fetching token metadata", 
            context=context,
            exc_info=True
        )
    else:
        logger.critical(
            "Unexpected error while fetching token metadata", 
            context=context,
            exc_info=True  # Always include full traceback for unexpected errors
        )
    
    # Log additional context if available
    if hasattr(error, 'args') and error.args:
        logger.debug("Error arguments", context={"error_args": str(error.args)})
        
    # Log request ID for correlation if available
    if request_id:
        logger.debug("Request ID for error correlation", context={"request_id": request_id})


def fetch_token_metadata(token_address: str) -> TokenMetadata:
    """
    Fetch comprehensive token metadata from BscScan and BSC node.
    
    This function retrieves token metadata from multiple sources:
    1. BscScan API for contract source code and ABI
    2. Direct BSC node connection for on-chain data
    
    Args:
        token_address: The token contract address (must be a valid BSC address)
        
    Returns:
        TokenMetadata: A dictionary containing token metadata
        
    Raises:
        ValueError: For invalid inputs or contract errors
        ConnectionError: For network-related errors
        Exception: For any other unexpected errors
    """
    start_time = time.time()
    logger.info(
        "Starting token metadata fetch",
        context={
            "token_address": token_address,
            "start_time": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(start_time))
        }
    )
    
    try:
        # Validate and normalize token address
        token_address = _validate_token_address(token_address)
        
        # Initialize Web3 with retry logic
        web3 = _initialize_web3_with_retry()
        
        # Fetch token metadata
        token_details = _fetch_token_metadata(web3, token_address)
        
        # Create standardized response
        metadata = _create_metadata_response(token_address, token_details)
        
        logger.info(
            "Successfully fetched token metadata",
            context={
                "token_address": token_address,
                "symbol": metadata["symbol"],
                "name": metadata["name"],
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
        
    except Web3Exception as e:
        _handle_metadata_failure(token_address, e, {
            "rpc_url": BSC_RPC_URL,
            "time_elapsed_seconds": f"{time.time() - start_time:.2f}s"
        })
        raise ConnectionError(f"❌ Blockchain error: {str(e)}") from e
        
    except Exception as e:
        _handle_metadata_failure(token_address, e, {
            "time_elapsed_seconds": f"{time.time() - start_time:.2f}s"
        })
        raise Exception(f"❌ Unexpected error: {str(e)}") from e

    # 2. Connect via Web3 to BNB Chain
    web3_start_time = time.time()
    logger.info(
        "Initiating Web3 connection to BSC node",
        context={
            "rpc_url": BSC_RPC_URL,
            "start_time": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(web3_start_time))
        }
    )
    
    try:
        # Initialize Web3 with retry logic
        w3 = _initialize_web3_with_retry()
        
        # Process ABI and contract verification status
        abi = metadata.get("ABI", "[]")
        is_verified = abi != "Contract source code not verified"
        
        # Log ABI processing details
        logger.debug(
            "Processing contract ABI and verification status",
            context={
                "is_verified": is_verified,
                "abi_length": len(abi) if is_verified else 0,
                "contract_name": metadata.get("ContractName", "Unknown"),
                "compiler_version": metadata.get("CompilerVersion", "unknown"),
                "optimization_used": metadata.get("OptimizationUsed"),
                "runs": metadata.get("Runs"),
                "evm_version": metadata.get("EVMVersion")
            }
        )

        # Handle unverified contracts
        if not is_verified:
            warning_msg = "Contract source code is not verified on BscScan"
            logger.warning(
                warning_msg,
                context={
                    "token_address": token_address,
                    "contract_name": metadata.get("ContractName", "Unknown"),
                    "proxy": metadata.get("Proxy") == "1",
                    "implementation": metadata.get("Implementation"),
                    "txn_count": metadata.get("TxnCount"),
                    "balance": metadata.get("Balance")
                }
            )
            
            metadata.update({
                "name": "N/A (Unverified)",
                "symbol": "N/A",
                "totalSupply": 0,
                "decimals": 0,
                "is_verified": False,
                "verification_status": "unverified"
            })
            
            # Additional checks for potential proxy contracts
            if metadata.get("Proxy") == "1":
                implementation = metadata.get("Implementation")
                if implementation:
                    logger.info(
                        "Unverified contract appears to be a proxy",
                        context={
                            "token_address": token_address,
                            "implementation_address": implementation
                        }
                    )
                    metadata["is_proxy"] = True
                    metadata["implementation"] = implementation
            
            return metadata

        # Create contract instance with detailed error handling and logging
        contract_start_time = time.time()
        logger.info(
            "Initializing Web3 contract instance",
            context={
                "token_address": token_address,
                "abi_length": len(abi) if abi else 0,
                "contract_name": metadata.get("ContractName", "Unknown")
            }
        )
        
        try:
            # Initialize contract with retry logic
            contract = _initialize_contract(w3, token_address, abi)
            
            # Fetch token details with individual error handling for each field
            token_details = {}
            
            # Get token details
            logger.info("Fetching token details from contract")
            
            # Get token name with fallback
            token_details["name"] = _safe_contract_call(contract, "name", token_address, "Unknown")
            
            # Get token symbol with fallback
            token_details["symbol"] = _safe_contract_call(contract, "symbol", token_address, "UNKNOWN")
            
            # Get token decimals with fallback (default to 18 if not available)
            token_details["decimals"] = _safe_contract_call(contract, "decimals", token_address, 18)
            
            # Get total supply with fallback
            raw_total_supply = _safe_contract_call(contract, "totalSupply", token_address, 0)
            
            # Calculate normalized supply
            try:
                decimals = token_details["decimals"]
                normalized_supply = float(Decimal(str(raw_total_supply)) / (10 ** decimals))
                token_details["totalSupply"] = normalized_supply
                token_details["rawTotalSupply"] = str(raw_total_supply)  # Keep original as string to avoid precision loss
            except Exception as e:
                logger.error(
                    "Error normalizing total supply",
                    context={
                        "error": str(e),
                        "decimals": token_details["decimals"],
                        "raw_total_supply": str(raw_total_supply)
                    }
                )
                token_details["totalSupply"] = 0
            
            # Log successful fetch
            contract_duration = time.time() - contract_start_time
            logger.info(
                "Successfully fetched token details from contract",
                context={
                    **token_details,
                    "contract_duration_seconds": round(contract_duration, 3),
                    "is_proxy": metadata.get("is_proxy", False),
                    "implementation": metadata.get("implementation")
                }
            )
            
            # Update metadata with token details
            metadata.update({
                "name": token_details["name"],
                "symbol": token_details["symbol"],
                "decimals": token_details["decimals"],
                "totalSupply": token_details["totalSupply"],
                "rawTotalSupply": token_details.get("rawTotalSupply", "0"),
                "is_verified": True,
                "verification_status": "verified"
            })
            
            # Add additional metadata if available
            metadata["contract_created"] = time.strftime("%Y-%m-%d %H:%M:%S")
            metadata["source"] = "bscscan_and_web3"
            
            return metadata
            
        except requests.exceptions.RequestException as e:
            error_msg = f"Network error while interacting with contract: {str(e)}"
            logger.error(
                error_msg,
                context={
                    "token_address": token_address,
                    "error_type": type(e).__name__,
                    "rpc_url": BSC_RPC_URL,
                    "time_since_start": f"{time.time() - start_time:.2f}s"
                },
                exc_info=True
            )
            raise ConnectionError(f"❌ {error_msg}") from e
            
        except web3.exceptions.ContractLogicError as e:
            error_msg = f"Contract logic error: {str(e)}"
            logger.error(
                error_msg,
                context={
                    "token_address": token_address,
                    "error_type": type(e).__name__,
                    "contract_methods": [f for f in dir(contract.functions) if not f.startswith('_')],
                    "abi_methods": [f for f in abi if f.get('type') == 'function']
                },
                exc_info=True
            )
            raise ValueError(f"❌ {error_msg}") from e
            
        except web3.exceptions.BadFunctionCallOutput as e:
            error_msg = f"Bad function call output - contract may not be fully initialized or ABI mismatch: {str(e)}"
            logger.error(
                error_msg,
                context={
                    "token_address": token_address,
                    "error_type": type(e).__name__,
                    "is_proxy": metadata.get("is_proxy", False),
                    "implementation": metadata.get("implementation")
                },
                exc_info=True
            )
            raise ValueError(f"❌ {error_msg}") from e
            
        except web3.exceptions.Web3Exception as e:
            error_msg = f"Web3 error: {str(e)}"
            logger.critical(
                error_msg,
                context={
                    "error_type": type(e).__name__,
                    "rpc_url": BSC_RPC_URL,
                    "token_address": token_address,
                    "time_elapsed_seconds": f"{time.time() - start_time:.2f}s"
                },
                exc_info=True
            )
            raise ConnectionError(f"❌ {error_msg}") from e
                
    finally:
        # Log completion metrics
        total_duration = time.time() - start_time
        success = 'e' not in locals() or not isinstance(e, Exception)
        logger.info(
            "Completed token metadata fetch",
            context={
                "token_address": token_address,
                "total_duration_seconds": round(total_duration, 3),
                "success": success,
                "contract_name": metadata.get("ContractName", "Unknown"),
                "is_verified": metadata.get("is_verified", False),
                "is_proxy": metadata.get("is_proxy", False)
            }
        )
