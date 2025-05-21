"""Audit routes for token security auditing operations."""
import time
import traceback
from typing import Optional, Dict, Any
from fastapi import APIRouter, Request, HTTPException, status

from app.schemas.audit_response import AuditResponse
from app.services.auditor import audit_token
from app.core.utils.logger import get_logger

# Get logger for this module
logger = get_logger("app.routes.audit")

# Create router
router = APIRouter(
    prefix="",  # Removido o prefixo, será adicionado no main.py
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
    Audit a token contract for security issues.
    
    Args:
        request: FastAPI request object
        token_address: Address of the token to audit
        lp_token: Optional liquidity pool token address
        
    Returns:
        AuditResponse with audit results
        
    Raises:
        HTTPException: If token audit fails or token is invalid
    """
    # Generate a unique request ID for tracking
    request_id = f"audit-{int(time.time())}-{token_address[:8]}"
    
    logger.info(
        f"Starting token audit for {token_address}",
        context={
            "request_id": request_id,
            "token_address": token_address,
            "lp_token": lp_token
        }
    )
    
    # Clean and validate token address
    if not token_address or not isinstance(token_address, str):
        error_msg = "Invalid token address"
        logger.error(
            error_msg,
            context={
                "request_id": request_id,
                "token_address": token_address
            }
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_msg
        )
    
    # Normalize token address
    original_address = token_address
    token_address = token_address.strip().lower()
    if not token_address.startswith('0x'):
        token_address = f'0x{token_address}'
    
    logger.info(
        f"Normalized token address: {original_address} -> {token_address}",
        context={
            "request_id": request_id,
            "original_address": original_address,
            "normalized_address": token_address
        }
    )
    
    # Call the audit service
    try:
        start_time = time.time()
        logger.debug(
            f"Calling audit_token service with {token_address}",
            context={
                "request_id": request_id,
                "token_address": token_address,
                "lp_token": lp_token
            }
        )
        
        result = await audit_token(token_address, lp_token_address=lp_token)
        elapsed_time = time.time() - start_time
        
        logger.info(
            f"Token audit completed for {token_address} in {elapsed_time:.2f}s",
            context={
                "request_id": request_id,
                "token_address": token_address,
                "elapsed_time": f"{elapsed_time:.2f}s"
            }
        )
        return result
    except ValueError as e:
        error_msg = f"Invalid audit request: {str(e)}"
        logger.warning(
            error_msg,
            context={
                "request_id": request_id,
                "token_address": token_address,
                "error": str(e)
            }
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_msg
        )
    except Exception as e:
        error_msg = "An error occurred during the token audit"
        logger.error(
            f"Error during token audit: {str(e)}",
            context={
                "request_id": request_id,
                "token_address": token_address,
                "error": str(e),
                "traceback": traceback.format_exc()
            },
            exc_info=True
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_msg
        )
