import logging
from typing import Dict, Optional, Any

from app.core.utils.logger import get_logger
from app.core.utils.metadata import fetch_token_metadata
from app.core.analyzers.static_analyzer import analyze_static
from app.core.analyzers.dynamic_analyzer import analyze_dynamic
from app.core.analyzers.onchain_analyzer import analyze_onchain
from app.core.utils.scoring import calculate_risk_score
from app.core.interfaces.analyzer import AnalysisResult

logger = get_logger(__name__)

async def analyze_token(token_address: str, lp_token_address: Optional[str] = None) -> Dict[str, Any]:
    """
    Analyzes a BSC token and returns a security report.
    
    Args:
        token_address: BSC token address
        lp_token_address: Liquidity pool address (optional)
        
    Returns:
        Dictionary with analysis results
    """
    logger.info(
        "Starting token analysis",
        context={
            "token_address": token_address,
            "lp_token_address": lp_token_address
        }
    )
    
    # Normalize token address
    if not token_address or not isinstance(token_address, str):
        error_msg = f"Invalid token address: {token_address}"
        logger.error(error_msg)
        raise ValueError(error_msg)
        
    # Clean and format token address
    token_address = token_address.strip().lower()
    if not token_address.startswith('0x'):
        token_address = f'0x{token_address}'
        
    # Validate token address length after normalization
    if len(token_address) != 42:
        error_msg = f"Invalid token address length: {token_address}"
        logger.error(error_msg)
        raise ValueError(error_msg)
    
    try:
        # Fetch metadata
        logger.debug("Fetching token metadata...", context={"token_address": token_address})
        metadata = fetch_token_metadata(token_address)
        
        # Check if metadata fetch failed
        if not metadata or not isinstance(metadata, dict):
            error_msg = "Invalid metadata format returned"
            logger.error(
                error_msg,
                context={
                    "token_address": token_address,
                    "metadata_type": type(metadata).__name__ if metadata else "None"
                }
            )
            from app.schemas.analyze_response import AnalyzeResponse
            return AnalyzeResponse.create_error_response(
                token_address=token_address,
                error=error_msg
            )
            
        if metadata.get("name") == "Error" or "error" in metadata:
            error_msg = metadata.get("error", "Failed to fetch token metadata")
            logger.error(
                f"Metadata fetch failed: {error_msg}",
                context={
                    "token_address": token_address,
                    "error": error_msg,
                    "error_type": metadata.get("error_type", "Unknown")
                }
            )
            from app.schemas.analyze_response import AnalyzeResponse
            return AnalyzeResponse.create_error_response(
                token_address=token_address,
                error=error_msg
            )
        
        source = metadata.get("SourceCode", "")

        # Static Analysis
        logger.debug("Performing static analysis...", context={"token_address": token_address})
        static_alerts = analyze_static(source)
        logger.debug(
            "Static analysis completed",
            context={
                "token_address": token_address,
                "alerts": len(static_alerts.get("issues", []))
            }
        )

        # Dynamic Analysis
        logger.debug("Performing dynamic analysis...")
        dynamic_alerts = {}
        try:
            dynamic_alerts = analyze_dynamic(source)
        except Exception as e:
            logger.warning("Dynamic analysis skipped due to error", context={"error": str(e), "token_address": token_address})
            dynamic_alerts = {
                "honeypot": {
                    "is_honeypot": False,
                    "buy_success": None,
                    "sell_success": None,
                    "high_tax": None,
                    "tax_discrepancy": None,
                    "error": str(e)
                },
                "fees": {
                    "buy": 0.0,
                    "sell": 0.0,
                    "buy_slippage": 0.0,
                    "sell_slippage": 0.0,
                    "buy_mutable": False,
                    "sell_mutable": False
                }
            }
        logger.debug(
            "Dynamic analysis completed",
            context={"is_honeypot": dynamic_alerts.get("honeypot", {}).get("is_honeypot", False)}
        )

        # On-chain Analysis
        logger.debug("Performing on-chain analysis...")
        metadata["lp_info"] = {
            "locked": False,
            "percent_locked": None
        }
        
        if lp_token_address:
            logger.debug(f"Liquidity token provided: {lp_token_address}")
            metadata["lp_info"]["locked"] = True
            metadata["lp_info"]["percent_locked"] = 100

        onchain_alerts = analyze_onchain(metadata)
        logger.debug("On-chain analysis completed")

        # Final Score Calculation
        logger.debug("Calculating risk score...")
        final = calculate_risk_score(static_alerts, dynamic_alerts, onchain_alerts)
        logger.info(
            "Analysis completed successfully",
            context={
                "token_address": token_address,
                "score": final["score"],
                "grade": final["grade"]
            }
        )

        # Prepare score object
        score = {
            "value": final["score"],
            "label": final["grade"]
        }
        
        # Prepare honeypot object
        honeypot = {
            "is_honeypot": dynamic_alerts.get("honeypot", {}).get("is_honeypot", False),
            "buy_success": dynamic_alerts.get("honeypot", {}).get("buy_success", None),
            "sell_success": dynamic_alerts.get("honeypot", {}).get("sell_success", None),
            "high_tax": dynamic_alerts.get("honeypot", {}).get("high_tax", None),
            "tax_discrepancy": dynamic_alerts.get("honeypot", {}).get("tax_discrepancy", None),
            "error": dynamic_alerts.get("honeypot", {}).get("error", None)
        }
        
        # Prepare fees object
        fees = {
            "buy": dynamic_alerts.get("fees", {}).get("buy", 0.0),
            "sell": dynamic_alerts.get("fees", {}).get("sell", 0.0),
            "buy_slippage": dynamic_alerts.get("fees", {}).get("buy_slippage", 0.0),
            "sell_slippage": dynamic_alerts.get("fees", {}).get("sell_slippage", 0.0),
            "buy_mutable": dynamic_alerts.get("fees", {}).get("buy_mutable", False),
            "sell_mutable": dynamic_alerts.get("fees", {}).get("sell_mutable", False)
        }
        
        # Prepare lp_lock object
        lp_lock = {
            "locked": metadata["lp_info"]["locked"],
            "percent_locked": metadata["lp_info"].get("percent_locked")
        }
        
        # Prepare owner object
        owner = {
            "renounced": static_alerts.get("owner", {}).get("renounced", False),
            "address": static_alerts.get("owner", {}).get("address")
        }
        
        # Get top holders
        top_holders = onchain_alerts.get("top_holders", {}).get("holders", [])
        
        # Get risks
        risks = final.get("alerts", [])
        
        # Combine all results using the new from_metadata method
        try:
            from app.schemas.analyze_response import AnalyzeResponse
            result = AnalyzeResponse.from_metadata(
                token_address=token_address,
                metadata=metadata,
                score=score,
                honeypot=honeypot,
                fees=fees,
                lp_lock=lp_lock,
                owner=owner,
                top_holders=top_holders,
                risks=risks
            )
            
            # Verify result is valid
            if not result or not hasattr(result, "token_address"):
                logger.error(
                    "Invalid analysis result format",
                    context={
                        "token_address": token_address,
                        "result_type": type(result).__name__ if result else "None"
                    }
                )
                return AnalyzeResponse.create_error_response(
                    token_address=token_address,
                    error="Failed to create valid analysis response"
                )
        except Exception as format_error:
            logger.error(
                f"Error formatting analysis result: {str(format_error)}",
                context={
                    "token_address": token_address,
                    "error": str(format_error)
                },
                exc_info=True
            )
            return AnalyzeResponse.create_error_response(
                token_address=token_address,
                error=f"Error formatting analysis result: {str(format_error)}"
            )

        logger.debug("Analysis result generated successfully")
        return result

    except Exception as e:
        error_msg = f"Error analyzing token: {str(e)}"
        logger.error(
            error_msg,
            context={
                "token_address": token_address,
                "error_type": type(e).__name__,
                "error_details": str(e)
            },
            exc_info=True
        )
        # Re-raise the exception to be handled by the route
        raise ValueError(error_msg) from e