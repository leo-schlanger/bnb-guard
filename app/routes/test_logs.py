"""
Test routes for logging functionality.
"""
import logging
import uuid
from typing import Dict, Any
from fastapi import Request

from app.routes.base import BaseRouter
from app.core.utils.logger import get_logger

# Get logger for this module
logger = get_logger("app.routes.test_logs")

class TestLogRouter(BaseRouter):
    """Router for testing logging functionality."""
    
    def __init__(self):
        """Initialize test routes."""
        super().__init__(
            prefix="/test-log",
            tags=["testing"]
        )
        self._setup_routes()
    
    def _setup_routes(self):
        """Define test routes."""
        self.router.add_api_route(
            path="",
            endpoint=self.test_logs,
            methods=["GET"],
            response_model=Dict[str, Any],
            summary="Test logging",
            description="Test logging functionality with different log levels and context"
        )
    
    async def test_logs(self, request: Request) -> Dict[str, Any]:
        """
        Test logging functionality.
        
        Args:
            request: FastAPI request object
            
        Returns:
            Dictionary with test results
        """
        # Generate a unique request ID for tracing
        request_id = str(uuid.uuid4())
        context = await self._get_request_context(request)
        context["request_id"] = request_id
        
        # Log messages at different levels with context
        logger.debug("This is a DEBUG message", context=context)
        logger.info("This is an INFO message", context=context)
        logger.warning("This is a WARNING message", context=context)
        
        try:
            # Simulate an error
            raise ValueError("This is a simulated error")
        except Exception as e:
            logger.error(
                f"This is an ERROR message: {str(e)}", 
                context=context,
                exc_info=True
            )
        
        # Log a critical message
        logger.critical(
            "This is a CRITICAL message", 
            context=context
        )
        
        # Return test results
        return {
            "success": True,
            "message": "Logging test completed successfully",
            "request_id": request_id,
            "logs_tested": [
                "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"
            ]
        }

# Create router instance
router = TestLogRouter().router
