"""
Token analysis routes for risk assessment and metrics.
"""

import traceback
import time
from typing import Optional, Dict, Any, Union
from fastapi import APIRouter, Request, HTTPException

from app.schemas.analyze_response import AnalyzeResponse
from app.services.analyzer import analyze_token as analyze_token_service
from app.core.utils.logger import get_logger

logger = get_logger("app.routes.analyze")

router = APIRouter(
    prefix="",  # Can be prefixed in main.py
    tags=["analysis"]
)

logger.info("Analyze router initialized")

@router.get("/{token_address}", response_model=AnalyzeResponse, summary="Analyze a token")
async def analyze_token(
    request: Request,
    token_address: str,
    lp_token: Optional[str] = None
) -> Union[Dict[str, Any], AnalyzeResponse]:
    """
    Perform a comprehensive analysis of a token contract.
    """
    request_id = f"analyze-{int(time.time())}-{token_address[:8]}"
    context = {"request_id": request_id}

    logger.info("Starting token analysis", context={
        "request_id": request_id,
        "token_address": token_address,
        "lp_token": lp_token
    })

    try:
        if not token_address or not isinstance(token_address, str):
            error_msg = "Token address is required"
            logger.error(error_msg, context)
            return AnalyzeResponse.create_error_response(
                token_address=token_address or "0x0",
                error=error_msg
            )

        original_address = token_address
        token_address = token_address.strip().lower()
        if not token_address.startswith("0x"):
            token_address = f"0x{token_address}"

        if len(token_address) != 42:
            raise HTTPException(status_code=400, detail="Invalid token address format")

        logger.info("Normalized token address", context={
            "request_id": request_id,
            "original_address": original_address,
            "normalized_address": token_address
        })

        start_time = time.time()

        try:
            result = await analyze_token_service(token_address=token_address, lp_token_address=lp_token)
            elapsed_time = round(time.time() - start_time, 2)

            if not result:
                error_msg = "Analyzer returned empty result"
                logger.error(error_msg, context | {"elapsed_time": f"{elapsed_time:.2f}s"})
                return AnalyzeResponse.create_error_response(
                    token_address=token_address,
                    error=error_msg
                )

            if isinstance(result, AnalyzeResponse):
                logger.info("Token analysis completed", context | {
                    "token_address": token_address,
                    "analysis_successful": True,
                    "elapsed_time": f"{elapsed_time:.2f}s"
                })
                return result

            # Build response from raw result
            debug_info = result.get("debug_info", {})
            debug_info["execution_time_seconds"] = elapsed_time

            response = AnalyzeResponse.from_metadata(
                token_address=token_address,
                metadata=result,
                score=result.get("score"),
                honeypot=result.get("honeypot"),
                fees=result.get("fees"),
                lp_lock=result.get("lp_lock"),
                owner=result.get("owner"),
                top_holders=result.get("top_holders", []),
                risks=result.get("risks", []),
                alerts=result.get("alerts", []),
                debug_info=debug_info
            )

            logger.info("Token analysis completed", context | {
                "token_address": token_address,
                "analysis_successful": True,
                "elapsed_time": f"{elapsed_time:.2f}s"
            })

            return response

        except Exception as analyze_error:
            elapsed_time = round(time.time() - start_time, 2)
            error_msg = f"Error in analyze_token service: {str(analyze_error)}"
            logger.error(error_msg, context | {
                "token_address": token_address,
                "error": str(analyze_error),
                "elapsed_time": f"{elapsed_time:.2f}s"
            }, exc_info=True)
            return AnalyzeResponse.create_error_response(
                token_address=token_address,
                error=error_msg
            )

    except ValueError as e:
        error_msg = f"Invalid token analysis request: {str(e)}"
        logger.warning(error_msg, context | {
            "token_address": token_address,
            "error_type": type(e).__name__,
            "error": str(e),
            "stack_trace": traceback.format_exc()
        })
        return AnalyzeResponse.create_error_response(
            token_address=token_address,
            error=error_msg
        )

    except HTTPException as http_exc:
        logger.warning(f"HTTP {http_exc.status_code} error", context | {
            "status_code": http_exc.status_code,
            "detail": str(http_exc.detail),
            "stack_trace": traceback.format_exc()
        })
        raise http_exc

    except Exception as e:
        error_msg = f"Unexpected error during token analysis: {str(e)}"
        logger.error(error_msg, context | {
            "token_address": token_address,
            "error_type": type(e).__name__,
            "error": str(e),
            "stack_trace": traceback.format_exc()
        }, exc_info=True)
        return AnalyzeResponse.create_error_response(
            token_address=token_address,
            error=error_msg
        )
