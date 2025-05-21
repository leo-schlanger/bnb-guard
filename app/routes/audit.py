"""
Audit routes for token security auditing operations.
"""
from typing import Optional
from fastapi import Request, HTTPException, status

from app.routes.base import BaseRouter
from app.schemas.audit_response import AuditResponse
from app.services.auditor import audit_token

class AuditRouter(BaseRouter):
    """Router for token audit endpoints."""
    
    def __init__(self):
        """Initialize audit routes."""
        super().__init__(prefix="/audit", tags=["audit"])
        self._setup_routes()
    
    def _setup_routes(self):
        """Define audit routes."""
        self.router.add_api_route(
            path="/{token_address}",
            endpoint=self.audit_token,
            methods=["GET"],
            response_model=AuditResponse,
            status_code=status.HTTP_200_OK,
            summary="Audit a token",
            description="Perform comprehensive security audit of a token contract",
            responses={
                200: {"description": "Audit completed successfully"},
                400: {"description": "Invalid token address or parameters"},
                404: {"description": "Token not found"},
                422: {"description": "Validation error"},
                500: {"description": "Internal server error during audit"}
            }
        )
    
    async def audit_token(
        self,
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
            Audit results with security findings and risk assessment
            
        Raises:
            HTTPException: If audit fails or token is invalid
        """
        context = await self._get_request_context(request)
        
        self.logger.info(
            "Starting token audit",
            context={
                **context,
                "token_address": token_address,
                "lp_token": lp_token
            }
        )
        
        try:
            result = await audit_token(token_address, lp_token_address=lp_token)
            
            self.logger.info(
                "Token audit completed",
                context={
                    **context,
                    "token_address": token_address,
                    "audit_successful": True,
                    "risk_score": result.get("risk_score", 0),
                    "risk_level": result.get("risk_level", "unknown")
                }
            )
            
            return result
            
        except ValueError as e:
            self.logger.warning(
                "Invalid audit request",
                context={
                    **context,
                    "token_address": token_address,
                    "error": str(e)
                }
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"error": str(e)}
            )
            
        except Exception as e:
            self.logger.error(
                "Token audit failed",
                context={
                    **context,
                    "token_address": token_address,
                    "error": str(e)
                },
                exc_info=True
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={"error": "Internal server error during token audit"}
            )

# Create router instance
router = AuditRouter().router
