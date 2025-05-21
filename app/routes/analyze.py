"""
Analysis routes for token analysis operations.
"""
"""Token analysis routes for risk assessment and metrics."""

import traceback
import time
from typing import Optional, Dict, Any, Union
from fastapi import APIRouter, Request, HTTPException

from app.schemas.analyze_response import AnalyzeResponse
from app.services.analyzer import analyze_token as analyze_token_service
from app.core.utils.logger import get_logger

# Get logger for this module
logger = get_logger("app.routes.analyze")

# Create router
router = APIRouter(
    prefix="",  # Removido o prefixo, será adicionado no main.py
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
    Perform comprehensive analysis of a token contract.
    
    Args:
        request: FastAPI request object
        token_address: Address of the token to analyze
        lp_token: Optional liquidity pool token address
        
    Returns:
        AnalyzeResponse with analysis results
        
    Raises:
        HTTPException: If token analysis fails or token is invalid
    """
    # Generate a unique request ID for tracking
    request_id = f"analyze-{int(time.time())}-{token_address[:8]}"
    # Create context for logging
    context = {"request_id": request_id}
    
    logger.info(
        f"Starting token analysis for {token_address}",
        context={
            "request_id": request_id,
            "token_address": token_address,
            "lp_token": lp_token
        }
    )
        
    try:
        # Clean and validate token address
        if not token_address or not isinstance(token_address, str):
            error_msg = "Token address is required"
            logger.error(error_msg, context={"request_id": request_id})
            return AnalyzeResponse.create_error_response(
                token_address=token_address or "0x0",
                error=error_msg
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
            
        logger.debug("Calling analyze_token service", context={
            "request_id": request_id,
            "token_address": token_address
        })
            
        # Call the async analyze_token function
        start_time = time.time()
        logger.info(
            f"Calling analyze_token service with token_address={token_address}, lp_token={lp_token}",
            context={
                "request_id": request_id,
                "token_address": token_address,
                "lp_token": lp_token,
                "start_time": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(start_time))
            }
        )
        
        try:
            result = await analyze_token_service(token_address=token_address, lp_token_address=lp_token)
            elapsed_time = time.time() - start_time
            
            # Verify result is valid
            if not result:
                error_msg = "Analyzer returned empty result"
                logger.error(
                    error_msg,
                    context={
                        "request_id": request_id,
                        "token_address": token_address,
                        "elapsed_time": f"{elapsed_time:.2f}s"
                    }
                )
                return AnalyzeResponse.create_error_response(
                    token_address=token_address,
                    error=error_msg
                )
            
            # If result is already an AnalyzeResponse, return it
            if isinstance(result, AnalyzeResponse):
                logger.info(
                    f"Token analysis completed for {token_address}",
                    context={
                        "request_id": request_id,
                        "token_address": token_address,
                        "analysis_successful": True,
                        "elapsed_time": f"{elapsed_time:.2f}s"
                    }
                )
                return result
                
            # Otherwise, create an AnalyzeResponse from the result
            try:
                response = AnalyzeResponse.from_metadata(
                    token_address=token_address,
                    metadata=result
                )
                
                logger.info(
                    f"Token analysis completed for {token_address}",
                    context={
                        "request_id": request_id,
                        "token_address": token_address,
                        "analysis_successful": True,
                        "elapsed_time": f"{elapsed_time:.2f}s"
                    }
                )
                
                return response
            except Exception as format_error:
                error_msg = f"Error formatting analysis result: {str(format_error)}"
                logger.error(
                    error_msg,
                    context={
                        "request_id": request_id,
                        "token_address": token_address,
                        "error": str(format_error)
                    },
                    exc_info=True
                )
                return AnalyzeResponse.create_error_response(
                    token_address=token_address,
                    error=error_msg
                )
                
        except Exception as analyze_error:
            elapsed_time = time.time() - start_time
            error_msg = f"Error in analyze_token service: {str(analyze_error)}"
            logger.error(
                error_msg,
                context={
                    "request_id": request_id,
                    "token_address": token_address,
                    "error": str(analyze_error),
                    "elapsed_time": f"{elapsed_time:.2f}s"
                },
                exc_info=True
            )
            return AnalyzeResponse.create_error_response(
                token_address=token_address,
                error=error_msg
            )
    except ValueError as e:
        error_msg = f"Invalid token analysis request: {str(e)}"
        logger.warning(
            error_msg,
            context={
                "request_id": request_id,
                "token_address": token_address,
                "error_type": type(e).__name__,
                "error": str(e),
                "stack_trace": traceback.format_exc()
            }
        )
        return AnalyzeResponse.create_error_response(
            token_address=token_address,
            error=error_msg
        )
        
    except HTTPException as http_exc:
        # Log and re-raise HTTP exceptions
        logger.warning(
            f"HTTP {http_exc.status_code} error: {str(http_exc.detail)}",
            context={
                "request_id": request_id,
                "status_code": http_exc.status_code,
                "detail": str(http_exc.detail),
                "stack_trace": traceback.format_exc()
            }
        )
        raise http_exc
        
    except Exception as e:
        error_msg = f"Unexpected error during token analysis: {str(e)}"
        logger.error(
            error_msg,
            context={
                "request_id": request_id,
                "token_address": token_address,
                "error_type": type(e).__name__,
                "error": str(e),
                "stack_trace": traceback.format_exc()
            },
            exc_info=True
        )
        return AnalyzeResponse.create_error_response(
            token_address=token_address,
            error=error_msg
        )


