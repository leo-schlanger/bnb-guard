"""
Analysis routes for token analysis operations.
"""
import logging
import traceback
from typing import Optional, Dict, Any, Union
from fastapi import Request, HTTPException, status, Depends

from app.routes.base import BaseRouter
from app.schemas.analyze_response import AnalyzeResponse, Severity
from app.services.analyzer import analyze_token

# Get logger for this module
logger = logging.getLogger("app.routes.analyze")

class AnalyzeRouter(BaseRouter):
    """Router for token analysis endpoints."""
    
    def __init__(self):
        """Initialize analysis routes."""
        super().__init__(
            prefix="/analyze",
            tags=["analysis"]
        )
        self._setup_routes()
    
    def _setup_routes(self):
        """Define analysis routes."""
        self.router.add_api_route(
            path="/{token_address}",
            endpoint=self.analyze_token,
            methods=["GET"],
            response_model=AnalyzeResponse,
            status_code=status.HTTP_200_OK,
            summary="Analyze a token",
            description="Perform comprehensive analysis of a token contract",
            responses={
                200: {"description": "Analysis completed successfully"},
                400: {"description": "Invalid token address"},
                404: {"description": "Token not found"},
                422: {"description": "Validation error"},
                500: {"description": "Internal server error"}
            }
        )
    
    async def analyze_token(
        self,
        request: Request,
        token_address: str,
        lp_token: Optional[str] = None
    ) -> Union[Dict[str, Any], AnalyzeResponse]:
        """
        Analyze a token contract.
        
        Args:
            request: FastAPI request object
            token_address: Address of the token to analyze
            lp_token: Optional liquidity pool token address
            
        Raises:
            HTTPException: If token analysis fails or token is invalid
        """
        context = await self._get_request_context(request)
        request_id = context.get("request_id", "unknown")
        
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
                    token_address=token_address,
                    error=error_msg
                )
                
            token_address = token_address.strip().lower()
            if not token_address.startswith('0x'):
                token_address = f'0x{token_address}'
                
            logger.debug("Calling analyze_token service", context={
                "request_id": request_id,
                "token_address": token_address
            })
            
            # Call the async analyze_token function
            result = await analyze_token(token_address, lp_token_address=lp_token)
            
            logger.info(
                f"Token analysis completed for {token_address}",
                context={
                    "request_id": request_id,
                    "token_address": token_address,
                    "analysis_successful": True
                }
            )
            
            return result
            
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

# Create router instance
router = AnalyzeRouter().router
