"""
Base router configuration with common dependencies and error handling.
"""
import logging
from fastapi import APIRouter, Depends, Request, HTTPException
from fastapi.responses import JSONResponse
from typing import Optional, Dict, Any, Tuple, Union
import uuid
import traceback

class BaseRouter:
    """Base router with common configurations and utilities."""
    
    def __init__(self, prefix: str, tags: list):
        """Initialize base router with common settings.
        
        Args:
            prefix: URL prefix for all routes in this router
            tags: OpenAPI tags for grouping related routes
        """
        self.router = APIRouter(prefix=prefix, tags=tags)
        # Get logger for the specific router class
        self.logger = logging.getLogger(f"app.routes.{self.__class__.__name__.lower()}")
        self.logger.debug(f"Initialized router: {prefix}")
        
        # Test logging at different levels
        self.logger.debug("Debug message from router")
        self.logger.info("Info message from router")
        self.logger.warning("Warning message from router")
    
    async def _get_request_context(self, request: Request) -> Dict[str, Any]:
        """Generate a context dictionary for request logging.
        
        Args:
            request: FastAPI request object
            
        Returns:
            Dict containing request context information
        """
        return {
            "request_id": str(uuid.uuid4()),
            "method": request.method,
            "url": str(request.url),
            "client": f"{request.client.host}:{request.client.port}",
            "headers": dict(request.headers)
        }
    
    def _create_error_response(
        self, 
        status_code: int, 
        error_type: str, 
        message: str,
        context: Optional[Dict[str, Any]] = None
    ) -> JSONResponse:
        """Create a standardized error response.
        
        Args:
            status_code: HTTP status code
            error_type: Type/category of the error
            message: Human-readable error message
            context: Additional context for the error
            
        Returns:
            FastAPI JSONResponse with error details
        """
        error_data = {
            "error": {
                "type": error_type,
                "message": message,
                "code": status_code
            }
        }
        
        if context:
            error_data["context"] = context
            
        return JSONResponse(
            status_code=status_code,
            content=error_data
        )
    
    def add_api_route(self, *args, **kwargs):
        """Add a route to the router with common configurations."""
        return self.router.add_api_route(*args, **kwargs)
