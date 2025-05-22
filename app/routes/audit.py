"""Audit routes for token security auditing operations."""

import time
import traceback
from typing import Optional
from fastapi import APIRouter, Request, HTTPException, status

from app.schemas.audit_response import AuditResponse
from app.services.auditor import audit_token as audit_token_service
from app.core.utils.logger import get_logger

# Logger and Router
logger = get_logger("app.routes.audit")

router = APIRouter(
    prefix="",  # Defined in main.py
    tags=["audit"]
)

logger.info("Audit router initialized")


@router.get("/{token_address}", response_model=AuditResponse, summary="Audit a token")
async def audit_token(
    request: Request,
    token_address: str,
    lp_token: Optional[str] = None
) -> AuditResponse:
    """
    Audit a token smart contract using static, dynamic, and on-chain analysis.
    """
    request_id = f"audit-{int(time.time())}-{token_address[:8]}"
    
    logger.info(
        "Starting token audit",
        context={
            "request_id": request_id,
            "token_address": token_address,
            "lp_token": lp_token
        }
    )

    # Validate and normalize address
    if not token_address or not isinstance(token_address, str):
        msg = "Invalid token address format"
        logger.error(msg, context={"request_id": request_id})
        raise HTTPException(status_code=400, detail=msg)

    normalized_address = token_address.strip().lower()
    if not normalized_address.startswith("0x"):
        normalized_address = f"0x{normalized_address}"

    logger.debug(
        f"Normalized address: {token_address} -> {normalized_address}",
        context={"request_id": request_id}
    )

    try:
        start_time = time.time()
        result = await audit_token_service(normalized_address, lp_token_address=lp_token)
        elapsed = time.time() - start_time

        logger.info(
            "Audit completed successfully",
            context={
                "request_id": request_id,
                "token_address": normalized_address,
                "elapsed_time": f"{elapsed:.2f}s"
            }
        )

        return result

    except ValueError as e:
        logger.warning(
            "Validation error during audit",
            context={"request_id": request_id, "error": str(e)}
        )
        raise HTTPException(status_code=400, detail=f"Validation error: {str(e)}")

    except Exception as e:
        logger.critical(
            "Unhandled error during audit",
            context={
                "request_id": request_id,
                "error_type": type(e).__name__,
                "token_address": normalized_address,
                "traceback": traceback.format_exc()
            },
            exc_info=True
        )
        raise HTTPException(
            status_code=500,
            detail="Internal server error during audit"
        )
