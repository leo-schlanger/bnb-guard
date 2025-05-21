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
    
    if not token_address or not isinstance(token_address, str) or len(token_address) != 42:
        error_msg = f"Invalid token address: {token_address}"
        logger.error(error_msg)
        raise ValueError(error_msg)
    
    try:
        # 📦 Fetch metadata
        logger.debug("Fetching token metadata...")
        metadata = fetch_token_metadata(token_address)
        source = metadata.get("SourceCode", "")

        # 🧠 Static Analysis
        logger.debug("Performing static analysis...")
        static_alerts = analyze_static(source)
        logger.debug(
            "Static analysis completed",
            context={"alerts": len(static_alerts.get("issues", []))}
        )

        # 🔁 Dynamic Analysis
        logger.debug("Performing dynamic analysis...")
        dynamic_alerts = analyze_dynamic(source)
        logger.debug(
            "Dynamic analysis completed",
            context={"is_honeypot": dynamic_alerts.get("honeypot", {}).get("is_honeypot", False)}
        )

        # 🔗 On-chain Analysis
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

        # 🧮 Final Score Calculation
        logger.debug("Calculating risk score...")
        final = calculate_risk_score(static_alerts, dynamic_alerts, onchain_alerts)
        logger.info(
            "Analysis completed successfully",
            context={
                "token_address": token_address,
                "score": final["risk_score"],
                "grade": final["grade"]
            }
        )

        # Preparar resultado
        result = {
            "token_address": token_address,
            "name": metadata.get("name", "N/A"),
            "symbol": metadata.get("symbol", "N/A"),
            "supply": float(metadata.get("totalSupply", 0)),
            "score": {
                "value": final["risk_score"],
                "label": final["grade"]
            },
            "honeypot": {
                "is_honeypot": dynamic_alerts.get("honeypot", {}).get("is_honeypot", False),
                "buy_success": dynamic_alerts.get("honeypot", {}).get("buy_success", False),
                "sell_success": dynamic_alerts.get("honeypot", {}).get("sell_success", False),
                "high_tax": dynamic_alerts.get("honeypot", {}).get("high_tax", False),
                "tax_discrepancy": dynamic_alerts.get("honeypot", {}).get("tax_discrepancy", False),
                "error": dynamic_alerts.get("honeypot", {}).get("error", "")
            },
            "fees": {
                "buy": dynamic_alerts.get("fees", {}).get("buy", 0.0),
                "sell": dynamic_alerts.get("fees", {}).get("sell", 0.0),
                "buy_slippage": dynamic_alerts.get("fees", {}).get("buy_slippage", 0.0),
                "sell_slippage": dynamic_alerts.get("fees", {}).get("sell_slippage", 0.0),
                "buy_mutable": dynamic_alerts.get("fees", {}).get("buy_mutable", False),
                "sell_mutable": dynamic_alerts.get("fees", {}).get("sell_mutable", False)
            },
            "lp_lock": {
                "locked": metadata["lp_info"]["locked"]
            },
            "owner": {
                "renounced": static_alerts.get("owner", {}).get("renounced", False)
            },
            "top_holders": onchain_alerts.get("top_holders", {}).get("holders", []),
            "risks": final.get("alerts", [])
        }

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