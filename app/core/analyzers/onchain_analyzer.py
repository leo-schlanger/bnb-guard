import requests
import time
import traceback
from typing import Dict, Any, List, Optional
from config import BSCSCAN_API_KEY
from app.core.interfaces.analyzer import Alert, TokenMetadata
from app.core.utils.logger import get_logger

# Initialize logger
logger = get_logger(__name__)

# Known locker contracts
KNOWN_LOCKERS = [
    "0x1fE80fC86816B778B529D3C2a3830e44A6519A25",  # PinkLock
    "0x88b8e5f5b052f9b38b3b7f529d6bd0a09c84c3a0",  # Mudra Locker
    "0x407993575c91ce7643a4d4cCACc9A98c36eE1BBE",  # Unicrypt
    "0x17e00383A843A9922bCA3B280C0ADE9f8BA48449"   # Team.Finance
]

# Cache for storing API responses to reduce redundant calls
_API_CACHE = {}

# Cache expiration time in seconds (5 minutes)
_CACHE_EXPIRY = 300

def analyze_onchain(metadata: TokenMetadata) -> Dict[str, Any]:
    """
    Analyze on-chain data for potential risks and suspicious activities.
    
    This function performs a comprehensive analysis of on-chain data including:
    - Deployer information and history
    - Token holder distribution
    - Liquidity pool status and locks
    - Suspicious transactions
    
    Args:
        metadata: Token metadata including holders, deployer info, and LP info
        
    Returns:
        Dictionary containing analysis results and alerts with the following structure:
        {
            "token_address": str,
            "deployer_address": Optional[str],
            "deployer_flagged": bool,
            "top_holder_concentration": Optional[float],
            "lp_locked": bool,
            "lp_percent_locked": Optional[float],
            "lp_info": Dict,
            "alerts": List[Dict],
            "warnings": List[Dict],
            "metadata": Dict
        }
        
    Raises:
        Exception: If there's an error during the analysis
    """
    analysis_start = time.time()
    token_address = metadata.get("token_address", "unknown")
    
    logger.info(
        "Starting on-chain analysis", 
        context={
            "token_address": token_address,
            "metadata_keys": list(metadata.keys())
        }
    )
    
    # Log the start of the analysis with basic metadata
    logger.debug(
        "Analysis metadata details", 
        context={
            "token_address": token_address,
            "deployer_address": metadata.get("deployer_address"),
            "has_lp_info": "lp_info" in metadata,
            "has_holders": "holders" in metadata,
            "has_source_code": bool(metadata.get("source_code")),
            "has_abi": bool(metadata.get("ABI")),
            "has_transactions": bool(metadata.get("transactions", []))
        }
    )
    
    try:
        # Initialize result dictionary with default values
        result = {
            "token_address": token_address,
            "deployer_address": metadata.get("deployer_address"),
            "deployer_token_count": metadata.get("deployer_token_count", 0),
            "deployer_flagged": False,
            "top_holder_concentration": None,
            "lp_locked": False,
            "lp_percent_locked": None,
            "lp_info": {},
            "alerts": [],
            "warnings": [],
            "metadata": {
                "analysis_timestamp": time.time(),
                "version": "1.0.0",
                "analysis_duration": 0
            }
        }
        
        # Copy lp_info from metadata if it exists
        if "lp_info" in metadata and isinstance(metadata["lp_info"], dict):
            logger.debug(
                "Updating LP info from metadata",
                context={"lp_info_keys": list(metadata["lp_info"].keys())}
            )
            result["lp_info"].update(metadata["lp_info"])
            
            # Log LP info details
            lp_info = metadata["lp_info"]
            logger.debug(
                "LP information",
                context={
                    "lp_address": lp_info.get("pair_address"),
                    "token0": lp_info.get("token0", {}).get("symbol"),
                    "token1": lp_info.get("token1", {}).get("symbol"),
                    "reserve0": lp_info.get("reserve0"),
                    "reserve1": lp_info.get("reserve1"),
                    "liquidity": lp_info.get("liquidity")
                }
            )
            
        # Check deployer information
        deployer_address = metadata.get("deployer_address")
        if deployer_address:
            logger.info(
                "Analyzing deployer information",
                context={
                    "deployer_address": deployer_address,
                    "has_deployer_info": bool(metadata.get("deployer_info")),
                    "deployer_first_seen": metadata.get("deployer_first_seen"),
                    "deployer_tx_count": metadata.get("deployer_tx_count")
                }
            )
            
            # Check if deployer is a known contract
            deployer_is_contract = metadata.get("deployer_is_contract", False)
            deployer_token_count = metadata.get("deployer_token_count", 0)
            
            logger.debug(
                "Deployer analysis details", 
                context={
                    "is_contract": deployer_is_contract,
                    "token_balance": deployer_token_count,
                    "is_verified": metadata.get("deployer_is_verified"),
                    "contract_name": metadata.get("deployer_contract_name"),
                    "contract_creator": metadata.get("deployer_creator"),
                    "contract_creation_tx": metadata.get("deployer_creation_tx")
                }
            )
            
            # If deployer is a contract, it might be a token locker or similar
            if deployer_is_contract:
                result["deployer_flagged"] = True
                contract_name = metadata.get("deployer_contract_name", "Unknown Contract")
                alert_msg = f"Token deployer {deployer_address} is a contract address ({contract_name}), not an EOA."
                
                logger.warning(
                    "Deployer is a contract address",
                    context={
                        "deployer_address": deployer_address,
                        "contract_name": contract_name,
                        "contract_creator": metadata.get("deployer_creator"),
                        "creation_tx": metadata.get("deployer_creation_tx")
                    }
                )
                
                result["alerts"].append({
                    "type": "deployer_is_contract",
                    "severity": "medium",
                    "message": alert_msg,
                    "details": {
                        "contract_name": contract_name,
                        "creator": metadata.get("deployer_creator"),
                        "creation_transaction": metadata.get("deployer_creation_tx")
                    }
                })
        
        # 🚨 Detect suspicious deployer
        if deployer_address:
            deployer_lower = deployer_address.lower()
            suspicious_addresses = [
                "0x0000000000000000000000000000000000000000",  # Zero address
                "0x000000000000000000000000000000000000dead",  # Dead address
                "0x0000000000000000000000000000000000000001",  # Another suspicious address
            ]
            
            if deployer_lower in suspicious_addresses:
                alert_msg = f"Suspicious deployer address detected: {deployer_address}"
                
                logger.warning(
                    "Suspicious deployer address detected",
                    context={
                        "deployer_address": deployer_address,
                        "suspicious_type": {
                            "0x0000000000000000000000000000000000000000": "Zero Address",
                            "0x000000000000000000000000000000000000dead": "Dead Address",
                            "0x0000000000000000000000000000000000000001": "Suspicious Address"
                        }.get(deployer_lower, "Unknown Suspicious Address")
                    }
                )
                
                result["alerts"].append({
                    "type": "suspicious_deployer",
                    "severity": "high",
                    "message": alert_msg,
                    "details": {
                        "address_type": {
                            "0x0000000000000000000000000000000000000000": "Zero Address",
                            "0x000000000000000000000000000000000000dead": "Dead Address",
                            "0x0000000000000000000000000000000000000001": "Suspicious Address"
                        }.get(deployer_lower, "Unknown")
                    }
                })
                result["deployer_flagged"] = True
                
                # Log additional context about the suspicious address
                logger.debug(
                    "Suspicious address context",
                    context={
                        "deployer_address": deployer_address,
                        "is_contract": deployer_is_contract,
                        "token_balance": deployer_token_count,
                        "first_seen": metadata.get("deployer_first_seen"),
                        "tx_count": metadata.get("deployer_tx_count")
                    }
                )
            
            deployer_token_count = metadata.get("deployer_token_count", 0)
            logger.debug("Checking deployer history", 
                        context={"token_count": deployer_token_count})
            
            if deployer_token_count > 5:
                result["deployer_flagged"] = True
                alert_msg = f"Deployer created {deployer_token_count} tokens"
                result["alerts"].append({
                    "type": "suspicious_deployer",
                    "severity": "high",
                    "message": alert_msg,
                    "token_count": deployer_token_count
                })
                logger.warning("Suspicious deployer detected", 
                             context={"token_count": deployer_token_count})
        
        # 📊 Holder concentration analysis
        holders = metadata.get("holders", [])
        holder_count = len(holders) if holders else 0
        result["holder_count"] = holder_count
        result["top_holders"] = {
            "top_1_percent": 0.0,
            "top_10_percent": 0.0,
            "top_50_percent": 0.0,
            "holders": []
        }
        
        if holders:
            logger.info(
                "Starting holder distribution analysis",
                context={
                    "total_holders": len(holders),
                    "has_holder_data": bool(holders),
                    "top_holder_addresses": [h.get("address") for h in holders[:3]] if len(holders) > 0 else []
                }
            )
            
            # Calculate top 10 holder concentration
            total_supply = float(metadata.get("total_supply", 1))
            if total_supply > 0:
                top_10_holders = holders[:10]
                top_10_balance = sum(float(h.get("balance", 0)) for h in top_10_holders)
                top_10_percent = (top_10_balance / total_supply) * 100
                result["top_holder_concentration"] = top_10_percent
                
                # Log detailed holder distribution
                logger.debug(
                    "Top holder distribution analysis",
                    context={
                        "total_supply": total_supply,
                        "top_10_balance": top_10_balance,
                        "top_10_percent": top_10_percent,
                        "top_holder_balance": float(top_10_holders[0].get("balance", 0)) if top_10_holders else 0,
                        "top_holder_percent": (float(top_10_holders[0].get("balance", 0)) / total_supply * 100) if top_10_holders else 0,
                        "top_5_holders_percent": (sum(float(h.get("balance", 0)) for h in top_10_holders[:5]) / total_supply * 100) if len(top_10_holders) >= 5 else 0
                    }
                )
                
                # Check for high concentration
                if top_10_percent > 90:
                    alert_msg = f"High holder concentration: Top 10 holders control {top_10_percent:.2f}% of supply"
                    logger.warning(
                        "High holder concentration detected",
                        context={
                            "concentration_percent": round(top_10_percent, 2),
                            "top_holder_percent": round((float(top_10_holders[0].get("balance", 0)) / total_supply * 100), 2) if top_10_holders else 0,
                            "top_5_holders_percent": round((sum(float(h.get("balance", 0)) for h in top_10_holders[:5]) / total_supply * 100), 2) if len(top_10_holders) >= 5 else 0
                        }
                    )
                    
                    result["alerts"].append({
                        "type": "high_holder_concentration",
                        "severity": "high",
                        "message": alert_msg,
                        "details": {
                            "concentration_percent": round(top_10_percent, 2),
                            "top_holder_percent": round((float(top_10_holders[0].get("balance", 0)) / total_supply * 100), 2) if top_10_holders else 0,
                            "top_5_holders_percent": round((sum(float(h.get("balance", 0)) for h in top_10_holders[:5]) / total_supply * 100), 2) if len(top_10_holders) >= 5 else 0,
                            "holder_distribution": [
                                {
                                    "rank": i + 1,
                                    "address": h.get("address"),
                                    "balance": float(h.get("balance", 0)),
                                    "percentage": round((float(h.get("balance", 0)) / total_supply * 100), 4)
                                }
                                for i, h in enumerate(top_10_holders)
                            ]
                        }
                    })
        
        # 🔒 LP lock verification
        lp_info = metadata.get("lp_info", {})
        if lp_info and lp_info.get("pair_address"):
            pair_address = lp_info.get("pair_address")
            logger.info(
                "Starting LP lock verification",
                context={
                    "pair_address": pair_address,
                    "has_lp_info": bool(lp_info),
                    "lp_tokens": [
                        {"symbol": lp_info.get("token0", {}).get("symbol"), "address": lp_info.get("token0", {}).get("address")},
                        {"symbol": lp_info.get("token1", {}).get("symbol"), "address": lp_info.get("token1", {}).get("address")}
                    ] if all(k in lp_info for k in ["token0", "token1"]) else []
                }
            )
            
            try:
                # Check if LP is locked in a known locker
                logger.debug("Checking LP lock status", 
                            context={"pair_address": pair_address})
                
                is_locked = is_lp_locked(pair_address)
                result["lp_locked"] = is_locked
                
                # Log detailed LP information
                lp_details = {
                    "pair_address": pair_address,
                    "is_locked": is_locked,
                    "locker_address": lp_info.get("locker_address"),
                    "reserves": {
                        "token0": lp_info.get("reserve0"),
                        "token1": lp_info.get("reserve1"),
                        "liquidity": lp_info.get("liquidity")
                    },
                    "created_at": lp_info.get("created_at"),
                    "tx_hash": lp_info.get("tx_hash")
                }
                
                logger.debug("LP lock status details", context=lp_details)
                
                if not is_locked:
                    alert_msg = "Liquidity is not locked"
                    logger.warning(
                        alert_msg,
                        context={
                            "pair_address": pair_address,
                            "risk_level": "high",
                            "recommendation": "Liquidity should be locked using a trusted locker contract"
                        }
                    )
                    
                    result["alerts"].append({
                        "type": "liquidity_not_locked",
                        "severity": "high",
                        "message": alert_msg,
                        "details": {
                            "pair_address": pair_address,
                            "tokens": [
                                f"{lp_info.get('token0', {}).get('symbol')} ({lp_info.get('token0', {}).get('address')})",
                                f"{lp_info.get('token1', {}).get('symbol')} ({lp_info.get('token1', {}).get('address')})"
                            ],
                            "reserves": {
                                "token0": lp_info.get("reserve0"),
                                "token1": lp_info.get("reserve1")
                            },
                            "created_at": lp_info.get("created_at"),
                            "tx_hash": lp_info.get("tx_hash")
                        }
                    })
                else:
                    logger.info(
                        "LP is locked",
                        context={
                            "pair_address": pair_address,
                            "locker_address": lp_info.get("locker_address"),
                            "lock_details": lp_info.get("lock_details", {})
                        }
                    )
                    
            except Exception as e:
                error_msg = f"Error checking LP lock status: {str(e)}"
                logger.error(
                    error_msg,
                    context={
                        "pair_address": pair_address,
                        "error": str(e),
                        "traceback": traceback.format_exc()
                    }
                )
                
                result["warnings"].append({
                    "type": "lp_lock_check_failed",
                    "severity": "medium",
                    "message": "Failed to verify LP lock status",
                    "details": {
                        "error": str(e),
                        "pair_address": pair_address,
                        "traceback": traceback.format_exc()
                    }
                })
        
        # Calculate analysis duration and update metadata
        analysis_duration = time.time() - analysis_start
        result["metadata"]["analysis_duration_seconds"] = round(analysis_duration, 2)
        
        # Log completion with summary
        logger.info(
            "On-chain analysis completed",
            context={
                "token_address": token_address,
                "duration_seconds": round(analysis_duration, 2),
                "alerts_count": len(result["alerts"]),
                "warnings_count": len(result["warnings"]),
                "deployer_flagged": result.get("deployer_flagged", False),
                "top_holder_concentration": result.get("top_holder_concentration"),
                "lp_locked": result.get("lp_locked", False),
                "lp_percent_locked": result.get("lp_percent_locked")
            }
        )
        
        # Log detailed analysis summary at debug level
        logger.debug(
            "Detailed on-chain analysis result",
            context={
                "token_address": token_address,
                "analysis_summary": {
                    "deployer_analysis": {
                        "address": result.get("deployer_address"),
                        "is_contract": deployer_is_contract if 'deployer_is_contract' in locals() else None,
                        "token_count": result.get("deployer_token_count"),
                        "is_flagged": result.get("deployer_flagged")
                    },
                    "holder_analysis": {
                        "total_holders": len(holders) if 'holders' in locals() else 0,
                        "top_holder_concentration": result.get("top_holder_concentration")
                    },
                    "liquidity_analysis": {
                        "is_locked": result.get("lp_locked"),
                        "percent_locked": result.get("lp_percent_locked"),
                        "pair_address": lp_info.get("pair_address") if lp_info else None
                    },
                    "alerts_summary": {
                        "total": len(result["alerts"]),
                        "by_severity": {
                            "high": len([a for a in result["alerts"] if a.get("severity") == "high"]),
                            "medium": len([a for a in result["alerts"] if a.get("severity") == "medium"]),
                            "low": len([a for a in result["alerts"] if a.get("severity") == "low"])
                        }
                    }
                }
            }
        )
        
        # Prepare the final result structure
        return {
            "token_address": token_address,
            "alerts": result["alerts"],
            "warnings": result["warnings"],
            "lp_info": result["lp_info"],
            "holder_analysis": {
                "top_holder_concentration": result.get("top_holder_concentration"),
                "holder_count": len(holders) if 'holders' in locals() else 0,
                "top_holders": holders[:10] if 'holders' in locals() and len(holders) > 0 else []
            },
            "deployer_analysis": {
                "address": result.get("deployer_address"),
                "is_contract": deployer_is_contract if 'deployer_is_contract' in locals() else False,
                "token_count": result.get("deployer_token_count", 0),
                "is_flagged": result.get("deployer_flagged", False)
            },
            "metadata": result["metadata"]
        }
    
    except Exception as e:
        error_msg = f"Error in on-chain analysis: {str(e)}"
        logger.error(error_msg, 
                    context={
                        "token_address": token_address,
                        "error_type": type(e).__name__,
                        "traceback": traceback.format_exc()
                    },
                    exc_info=True)
        
        # Log the error to a dedicated error log
        logger.critical("Critical error in on-chain analysis", 
                       context={
                           "token_address": token_address,
                           "error": str(e),
                           "error_type": type(e).__name__
                       })
        
        # Return a safe error response
        # Return a minimal response with error information
        return {
            "onchain_alerts": [{
                "type": "analysis_error",
                "severity": "critical",
                "message": f"Failed to complete on-chain analysis: {str(e)}"
            }],
            "onchain_warnings": [],
            "lp_info": {"locked": False, "percent_locked": None},
            "holder_analysis": {"top_holder_concentration": None, "holder_count": 0},
            "deployer_analysis": {"address": None, "token_count": 0, "is_flagged": False},
            "metadata": {
                "error": str(e),
                "error_type": type(e).__name__,
                "analysis_completed": False,
                "analysis_duration_seconds": time.time() - start_time if 'start_time' in locals() else 0
            }
        }

def get_deployer_address(token_address: str) -> str:
    """
    Retrieve the deployer address of a token contract from BscScan.
    
    This function fetches the deployer address of a given token contract using the
    BscScan API. It includes caching to reduce API calls and improve performance.
    
    Args:
        token_address: The address of the token contract (must be a valid BSC address)
        
    Returns:
        str: The deployer's address in lowercase
        
    Raises:
        ValueError: If the provided token address is invalid
        requests.RequestException: For network-related errors
        LookupError: If the deployer address cannot be found
        Exception: For any other unexpected errors during processing
    """
    start_time = time.time()
    logger.info(
        "Starting deployer address lookup",
        context={"token_address": token_address}
    )
    
    # Input validation
    if not token_address or not isinstance(token_address, str) or not token_address.startswith("0x") or len(token_address) != 42:
        error_msg = "Invalid token address format"
        logger.error(
            error_msg,
            context={"token_address": token_address}
        )
        raise ValueError(error_msg)
    
    token_address = token_address.lower()
    cache_key = f"deployer_{token_address}"
    
    # Check cache first
    if cache_key in _API_CACHE:
        cached_data = _API_CACHE[cache_key]
        cache_age = time.time() - cached_data["timestamp"]
        
        if cache_age < _CACHE_EXPIRY:
            logger.debug(
                "Returning deployer address from cache",
                context={
                    "token_address": token_address,
                    "cache_age_seconds": round(cache_age, 2),
                    "deployer_address": cached_data["data"]
                }
            )
            return cached_data["data"]
    
    logger.info(
        "Fetching deployer address from BscScan API",
        context={
            "token_address": token_address,
            "cache_enabled": True,
            "cache_expiry_seconds": _CACHE_EXPIRY
        }
    )
    
    try:
        # Prepare API request
        url = (
            f"https://api.bscscan.com/api"
            f"?module=contract"
            f"&action=getcontractcreation"
            f"&contractaddresses={token_address}"
            f"&apikey={BSCSCAN_API_KEY}"
        )
        
        # Make the API request with timeout and error handling
        response = requests.get(url, timeout=15)  # Increased timeout for reliability
        response.raise_for_status()  # Raises HTTPError for bad responses
        
        data = response.json()
        
        # Log API response status
        logger.debug(
            "Received response from BscScan API",
            context={
                "token_address": token_address,
                "status": data.get("status"),
                "message": data.get("message"),
                "result_count": len(data.get("result", [])),
                "response_keys": list(data.keys())
            }
        )
        
        # Check for API errors
        if data.get("status") != "1" or not data.get("result"):
            error_msg = data.get("message", "Deployer address not found")
            logger.warning(
                "Failed to retrieve deployer address",
                context={
                    "token_address": token_address,
                    "status": data.get("status"),
                    "message": error_msg,
                    "result_count": len(data.get("result", []))
                }
            )
            raise LookupError(f"Deployer address not found: {error_msg}")
            
        # Extract deployer address from response
        try:
            deployer = data["result"][0]["contractCreator"].lower()
            logger.debug(
                "Successfully extracted deployer address",
                context={
                    "token_address": token_address,
                    "deployer_address": deployer,
                    "response_index": 0
                }
            )
        except (KeyError, IndexError) as e:
            error_msg = f"Unexpected response format from BscScan: {str(e)}"
            logger.error(
                error_msg,
                context={
                    "token_address": token_address,
                    "response_data": data,
                    "error_type": type(e).__name__
                }
            )
            raise LookupError("Could not parse deployer address from API response") from e
        
        # Cache the result
        cache_entry = {
            "data": deployer,
            "timestamp": time.time(),
            "metadata": {
                "source": "bscscan_api",
                "token_address": token_address,
                "cache_timestamp": time.time()
            }
        }
        _API_CACHE[cache_key] = cache_entry
        
        logger.info(
            "Successfully retrieved deployer address",
            context={
                "token_address": token_address,
                "deployer_address": deployer,
                "processing_time_seconds": round(time.time() - start_time, 4),
                "cache_updated": True
            }
        )
        
        return deployer
        
    except requests.RequestException as e:
        error_msg = f"Network error while fetching deployer address: {str(e)}"
        logger.error(
            error_msg,
            context={
                "token_address": token_address,
                "error_type": type(e).__name__,
                "request_url": url if 'url' in locals() else None,
                "response_status": e.response.status_code if hasattr(e, 'response') else None,
                "response_text": e.response.text if hasattr(e, 'response') and e.response else None
            },
            exc_info=True
        )
        raise requests.RequestException(error_msg) from e
        
    except LookupError:
        raise  # Re-raise LookupError as is
        
    except Exception as e:
        error_msg = f"Unexpected error in get_deployer_address: {str(e)}"
        logger.error(
            error_msg,
            context={
                "token_address": token_address,
                "error_type": type(e).__name__,
                "traceback": traceback.format_exc()
            },
            exc_info=True
        )
        raise Exception(error_msg) from e
        
    finally:
        # Log the completion of the operation
        logger.debug(
            "Completed deployer address lookup",
            context={
                "token_address": token_address,
                "duration_seconds": round(time.time() - start_time, 4),
                "timestamp": time.time()
            }
        )
        
    return data["result"][0]["contractCreator"]

def get_holder_distribution(token_address: str) -> List[Dict[str, Any]]:
    """
    Retrieve the top token holders and their distribution from BscScan API.
    
    This function fetches the top token holders and processes the data to provide
    a normalized view of the token distribution. It includes caching to reduce
    API calls and improve performance.
    
    Args:
        token_address: The address of the token contract (must be a valid BSC address)
        
    Returns:
        List[Dict[str, Any]]: A list of dictionaries containing holder information with
                            address, balance, and percentage of total supply
                            
    Raises:
        ValueError: If the provided token address is invalid
        requests.RequestException: For network-related errors
        Exception: For any other unexpected errors during processing
    """
    start_time = time.time()
    logger.info(
        "Starting holder distribution fetch",
        context={"token_address": token_address}
    )
    
    # Input validation
    if not token_address or not isinstance(token_address, str) or not token_address.startswith("0x") or len(token_address) != 42:
        error_msg = "Invalid token address format"
        logger.error(
            error_msg,
            context={"token_address": token_address}
        )
        raise ValueError(error_msg)
    
    token_address = token_address.lower()
    cache_key = f"holders_{token_address}"
    
    # Check cache first
    if cache_key in _API_CACHE:
        cached_data = _API_CACHE[cache_key]
        cache_age = time.time() - cached_data["timestamp"]
        
        if cache_age < _CACHE_EXPIRY:
            logger.debug(
                "Returning holder distribution from cache",
                context={
                    "token_address": token_address,
                    "cache_age_seconds": round(cache_age, 2),
                    "cached_holder_count": len(cached_data["data"])
                }
            )
            return cached_data["data"]
    
    logger.info(
        "Fetching holder distribution from BscScan API",
        context={
            "token_address": token_address,
            "cache_enabled": True,
            "cache_expiry_seconds": _CACHE_EXPIRY
        }
    )
    
    try:
        # Prepare API request
        url = (
            f"https://api.bscscan.com/api"
            f"?module=token"
            f"&action=tokenholderlist"
            f"&contractaddress={token_address}"
            f"&page=1"
            f"&offset=100"  # Get top 100 holders
            f"&apikey={BSCSCAN_API_KEY}"
        )
        
        # Make the API request with timeout and error handling
        response = requests.get(url, timeout=30)  # Increased timeout for reliability
        response.raise_for_status()  # Raises HTTPError for bad responses
        
        data = response.json()
        
        # Log API response status
        logger.debug(
            "Received response from BscScan API",
            context={
                "token_address": token_address,
                "status": data.get("status"),
                "message": data.get("message"),
                "result_count": len(data.get("result", [])),
                "response_keys": list(data.keys())
            }
        )
        
        # Check for API errors
        if data.get("status") != "1" or not data.get("result"):
            error_msg = data.get("message", "Unknown error")
            logger.warning(
                "BscScan API returned an error or no data",
                context={
                    "token_address": token_address,
                    "status": data.get("status"),
                    "message": error_msg,
                    "result_count": len(data.get("result", []))
                }
            )
            return []
        
        # Process and normalize the holder data
        holders = []
        total_supply = sum(float(h.get("value", 0)) for h in data["result"])
        
        if total_supply <= 0:
            logger.warning(
                "Total supply is zero or negative",
                context={
                    "token_address": token_address,
                    "total_supply": total_supply,
                    "result_count": len(data["result"])
                }
            )
            return []
        
        # Process top 50 holders
        skipped_holders = 0
        for holder in data["result"][:50]:
            try:
                balance = float(holder.get("value", 0))
                if balance <= 0:
                    skipped_holders += 1
                    continue
                
                holder_address = holder.get("address", "").lower()
                if not holder_address:
                    logger.warning("Holder address is empty", context={"holder": holder})
                    continue
                    
                holders.append({
                    "address": holder_address,
                    "balance": balance,
                    "percent": (balance / total_supply) * 100,
                    "value_wei": holder.get("value"),
                    "token_address": token_address
                })
            except (ValueError, TypeError) as e:
                logger.warning(
                    "Error processing holder data",
                    context={
                        "holder": holder,
                        "error": str(e),
                        "error_type": type(e).__name__
                    }
                )
                continue
        
        # Cache the result
        cache_entry = {
            "data": holders,
            "timestamp": time.time(),
            "metadata": {
                "source": "bscscan_api",
                "token_address": token_address,
                "holder_count": len(holders),
                "skipped_holders": skipped_holders
            }
        }
        _API_CACHE[cache_key] = cache_entry
        
        # Calculate distribution metrics
        top_holder_percent = holders[0]["percent"] if holders else 0
        top_10_percent = sum(h["percent"] for h in holders[:10])
        
        logger.info(
            "Successfully processed holder distribution",
            context={
                "token_address": token_address,
                "holder_count": len(holders),
                "top_holder_percent": round(top_holder_percent, 2),
                "top_10_holders_percent": round(top_10_percent, 2),
                "skipped_holders": skipped_holders,
                "processing_time_seconds": round(time.time() - start_time, 4),
                "cache_updated": True
            }
        )
        
        return holders
        
    except requests.RequestException as e:
        error_msg = f"Network error while fetching holder distribution: {str(e)}"
        logger.error(
            error_msg,
            context={
                "token_address": token_address,
                "error_type": type(e).__name__,
                "request_url": url if 'url' in locals() else None,
                "response_status": e.response.status_code if hasattr(e, 'response') else None,
                "response_text": e.response.text if hasattr(e, 'response') and e.response else None
            },
            exc_info=True
        )
        raise  # Re-raise to allow calling function to handle
        
    except Exception as e:
        error_msg = f"Unexpected error in get_holder_distribution: {str(e)}"
        logger.error(
            error_msg,
            context={
                "token_address": token_address,
                "error_type": type(e).__name__,
                "traceback": traceback.format_exc()
            },
            exc_info=True
        )
        raise  # Re-raise to allow calling function to handle
        
    finally:
        # Log the completion of the operation
        logger.debug(
            "Completed holder distribution fetch",
            context={
                "token_address": token_address,
                "duration_seconds": round(time.time() - start_time, 4),
                "timestamp": time.time()
            }
        )

def is_lp_locked(lp_token_address: str) -> bool:
    """
    Check if the LP tokens are locked in a known locker contract.
    
    This function verifies if the provided LP token address is locked by:
    1. Checking against a list of known locker contracts
    2. (Future) Querying the token contract for lock information
    3. (Future) Checking common locker registry contracts
    
    Args:
        lp_token_address: The address of the LP token contract
        
    Returns:
        bool: True if LP is locked, False otherwise or on error
        
    Raises:
        ValueError: If the provided LP token address is invalid
    """
    start_time = time.time()
    logger.info(
        "Starting LP lock verification",
        context={"lp_token_address": lp_token_address}
    )
    
    if not lp_token_address:
        logger.warning("No LP token address provided for lock check")
        return False
        
    if not isinstance(lp_token_address, str) or not lp_token_address.startswith("0x") or len(lp_token_address) != 42:
        logger.error("Invalid LP token address format", 
                    context={"lp_token_address": lp_token_address})
        raise ValueError("Invalid LP token address format")
    
    try:
        # Normalize address for comparison
        lp_token_address = lp_token_address.lower()
        
        # Check against known locker contracts
        known_lockers = [x.lower() for x in KNOWN_LOCKERS]
        if lp_token_address in known_lockers:
            locker_name = {
                "0x1fe80fc86816b778b529d3c2a3830e44a6519a25": "PinkLock",
                "0x88b8e5f5b052f9b38b3b7f529d6bd0a09c84c3a0": "Mudra Locker",
                "0x407993575c91ce7643a4d4ccacc9a98c36ee1bbe": "Unicrypt",
                "0x17e00383a843a9922bca3b280c0ade9f8ba48449": "Team.Finance"
            }.get(lp_token_address, "Unknown Locker")
            
            logger.info(
                "LP is locked with a known locker service",
                context={
                    "lp_token_address": lp_token_address,
                    "locker_name": locker_name,
                    "verification_method": "known_lockers_list"
                }
            )
            return True
            
        # TODO: Add more sophisticated verification methods:
        # 1. Check token's balance in known locker contracts
        # 2. Query token's lock events
        # 3. Check token's owner/controller for known locker patterns
        
        logger.info(
            "LP is not locked with a known locker service",
            context={
                "lp_token_address": lp_token_address,
                "verification_method": "known_lockers_list",
                "known_lockers_checked": known_lockers
            }
        )
        return False
        
    except Exception as e:
        error_msg = f"Error checking LP lock status: {str(e)}"
        logger.error(
            error_msg,
            context={
                "lp_token_address": lp_token_address,
                "error_type": type(e).__name__,
                "traceback": traceback.format_exc(),
                "verification_failed": True
            },
            exc_info=True
        )
        # Default to False on error to be safe
        return False
    finally:
        # Log the completion of the check
        duration = time.time() - start_time
        logger.debug(
            "Completed LP lock verification",
            context={
                "lp_token_address": lp_token_address,
                "duration_seconds": round(duration, 4),
                "timestamp": time.time()
            }
        )
