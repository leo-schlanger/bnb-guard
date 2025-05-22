from datetime import datetime, timezone
from typing import Optional, Dict, Any

from app.core.utils.logger import get_logger
from app.core.utils.metadata import fetch_token_metadata
from app.core.analyzers.static_analyzer import analyze_static
from app.core.analyzers.dynamic_analyzer import analyze_dynamic
from app.core.analyzers.onchain_analyzer import analyze_onchain
from app.core.utils.scoring import calculate_risk_score
from app.schemas.audit_response import AuditResponse, AnalysisSection

logger = get_logger(__name__)

async def audit_token(token_address: str, lp_token_address: Optional[str] = None) -> Dict[str, Any]:
    start_time = datetime.now(timezone.utc)
    logger.info("Starting token audit", context={"token_address": token_address, "lp_token_address": lp_token_address})

    try:
        # Normalize token address
        token_address = token_address.strip().lower()
        if not token_address.startswith("0x"):
            token_address = f"0x{token_address}"
        if len(token_address) != 42:
            raise ValueError("Invalid token address format")

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

        # Static analysis
        try:
            static_alerts = analyze_static(source)
        except Exception as e:
            logger.warning("Static analysis failed", context={"error": str(e)})
            static_alerts = {
                "functions": [{
                    "type": "analysis_error",
                    "message": f"Error during static analysis: {str(e)}",
                    "severity": "critical"
                }],
                "owner": {"renounced": False},
                "dangerous_functions_found": [],
                "dangerous_modifiers_found": [],
                "total_dangerous_matches": 0,
                "has_mint": False,
                "has_blacklist": False,
                "has_set_fee": False,
                "has_only_owner": False,
                "has_pause": False
            }

        # Dynamic analysis
        try:
            dynamic_alerts = analyze_dynamic(source)
        except Exception as e:
            logger.warning("Dynamic analysis fallback", context={"error": str(e)})
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

        # On-chain analysis
        metadata["lp_info"] = {
            "locked": False,
            "percent_locked": None
        }
        if lp_token_address:
            metadata["lp_info"]["locked"] = True
            metadata["lp_info"]["percent_locked"] = 100

        onchain_alerts = analyze_onchain(metadata)

        # Score
        score_data = calculate_risk_score(static_alerts, dynamic_alerts, onchain_alerts)

        logger.info("Audit completed", context={
            "token_address": token_address,
            "score": score_data.get("score"),
            "grade": score_data.get("grade")
        })

        # Format response using Pydantic model
        response = AuditResponse(
            status="completed",
            timestamp=start_time.isoformat(),
            token_address=token_address,
            lp_token_address=lp_token_address,
            score=score_data["score"],
            grade=score_data["grade"],
            analysis=AnalysisSection(
                static=static_alerts,
                dynamic=dynamic_alerts,
                onchain=onchain_alerts
            ),
            alerts=score_data.get("alerts", []),
            risks=score_data.get("risks", []),
            score_breakdown=score_data["score_breakdown"]
        )

        return response.model_dump()

    except Exception as e:
        logger.critical("Audit failed", context={
            "token_address": token_address,
            "error_type": type(e).__name__,
            "error": str(e)
        }, exc_info=True)

        return AuditResponse.create_error_response(
            token_address=token_address,
            lp_token_address=lp_token_address,
            error_message=str(e)
        ).model_dump()
