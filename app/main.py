"""Main application module for BNBGuard API.

This module initializes the FastAPI application, sets up logging,
registers routers, middleware, and exception handlers.
"""

import os
import sys
import logging
import time
import traceback
from datetime import datetime
from pathlib import Path
from contextlib import asynccontextmanager
from typing import Dict, Any

# Add project root to path first
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Import configuration and logging
from app.core.config import settings
from app.core.utils.logger import setup_logging, get_logger

# Setup logging
logger = setup_logging()

# Get log level from environment
log_level = os.getenv('LOG_LEVEL', 'INFO').upper()
logger.level = log_level  # Use property instead of setLevel
logger.info(f"Logging level set to: {log_level}")
logger.info(f"Initializing BNBGuard API (log level: {log_level})")

# Import FastAPI dependencies
from fastapi import FastAPI, Request, status, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi
import uvicorn
from typing import Dict, Any

# Import routers
from app.routes.health import router as health_router
from app.routes.analysis import router as analysis_router
from app.routes.audits import router as audits_router

# Constants
API_PREFIX = "/api/v1"
APP_VERSION = "2.0.0"

# API metadata
tags_metadata = [
    {
        "name": "analysis",
        "description": "Simple analysis for end users - quick safety checks and user-friendly results.",
    },
    {
        "name": "audits", 
        "description": "Comprehensive audits for developers - detailed technical analysis and recommendations.",
    },
    {
        "name": "health",
        "description": "System health monitoring and diagnostics.",
    },
    {
        "name": "root",
        "description": "API information and documentation.",
    },
]

# Application lifecycle management
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle application startup and shutdown events.
    
    Args:
        app: The FastAPI application instance
    """
    # Startup
    logger.info("Starting BNBGuard API service")
    try:
        # Perform startup operations here (e.g., connect to database)
        yield
    finally:
        # Shutdown
        logger.info("Shutting down BNBGuard API service", context={"service": "BNBGuard API"})
        # Perform cleanup operations here (e.g., close database connections)

# Exception handlers
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle request validation errors.
    
    Args:
        request: The incoming request
        exc: The validation exception
        
    Returns:
        JSONResponse with validation error details
    """
    logger.error(
        "Request validation error",
        context={
            "path": str(request.url.path), 
            "method": request.method,
            "errors": str(exc.errors())
        },
    )
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": exc.errors(), "body": exc.body},
    )

async def global_exception_handler(request: Request, exc: Exception):
    """Handle all unhandled exceptions.
    
    Args:
        request: The incoming request
        exc: The unhandled exception
        
    Returns:
        JSONResponse with generic error message
    """
    logger.error(
        "Unhandled exception",
        exc_info=exc,
        context={
            "path": str(request.url.path), 
            "method": request.method,
            "error": str(exc)
        },
    )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error"},
    )

def create_application() -> FastAPI:
    """Create and configure the FastAPI application.
    
    Returns:
        FastAPI: Configured FastAPI application instance
    """
    app = FastAPI(
        title="BNBGuard API",
        description="Automated risk analysis for BNB Chain tokens and pools",
        version=APP_VERSION,
        openapi_tags=tags_metadata,
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan
    )
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # For development; restrict in production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Register exception handlers
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(Exception, global_exception_handler)
    
    return app

# Create the FastAPI application
app = create_application()

# Request/response logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Enhanced middleware to log all incoming requests and responses.
    
    Args:
        request: The incoming request
        call_next: The next middleware or route handler
        
    Returns:
        The response from the route handler
    """
    # Generate request ID for tracking
    request_id = f"{int(datetime.now().timestamp())}-{request.client.host if request.client else 'unknown'}"
    
    # Extract client info
    client_ip = request.client.host if request.client else "unknown"
    user_agent = request.headers.get("user-agent", "unknown")
    
    # Start timing
    start_time = datetime.now()
    
    try:
        # Process the request
        response = await call_next(request)
        process_time = (datetime.now() - start_time).total_seconds()
        
        # Log the API request using the new structured method
        logger.api_request(
            method=request.method,
            url=str(request.url),
            status_code=response.status_code,
            duration=process_time,
            client_ip=client_ip
        )
        
        # Log additional details at debug level
        logger.debug("Request details", {
            "request_id": request_id,
            "user_agent": user_agent[:50] + "..." if len(user_agent) > 50 else user_agent,
            "query_params": dict(request.query_params),
            "path_params": request.path_params
        })
        
        return response
        
    except Exception as e:
        process_time = (datetime.now() - start_time).total_seconds()
        
        # Log request processing failures
        logger.failure("Request processing failed", {
            "request_id": request_id,
            "method": request.method,
            "url": str(request.url),
            "client_ip": client_ip,
            "error": str(e),
            "duration_ms": round(process_time * 1000, 2)
        }, exc_info=True)
        raise

def register_middleware(app: FastAPI) -> None:
    """Register all middleware.
    
    Args:
        app: FastAPI application instance
    """
    app.middleware("http")(log_requests)

def register_routers(app: FastAPI) -> None:
    """Register all API routers.
    
    Args:
        app: FastAPI application instance
    """
    # New API routes
    app.include_router(analysis_router, prefix=f"{API_PREFIX}/analysis")
    app.include_router(audits_router, prefix=f"{API_PREFIX}/audits")
    
    # System routes
    app.include_router(health_router, prefix=f"{API_PREFIX}/health")
    
    # Root endpoint
    @app.get("/", tags=["root"])
    async def root():
        """Root endpoint with API information.
        
        Returns:
            Dictionary with API metadata and links
        """
        logger.info("Root endpoint accessed")
        return {
            "name": "BNBGuard API",
            "version": APP_VERSION,
            "status": "operational",
            "description": "Automated risk analysis for BNB Chain tokens and pools",
            "documentation": {
                "swagger": "/docs",
                "redoc": "/redoc"
            },
            "api_structure": {
                "analysis": {
                    "description": "Simple analysis for end users",
                    "endpoints": [
                        f"{API_PREFIX}/analysis/tokens/{{address}}",
                        f"{API_PREFIX}/analysis/tokens/{{address}}/quick",
                        f"{API_PREFIX}/analysis/pools/{{address}}",
                        f"{API_PREFIX}/analysis/pools/{{address}}/quick"
                    ]
                },
                "audits": {
                    "description": "Comprehensive audits for developers",
                    "endpoints": [
                        f"{API_PREFIX}/audits/tokens/{{address}}",
                        f"{API_PREFIX}/audits/tokens/{{address}}/security",
                        f"{API_PREFIX}/audits/pools/{{address}}",
                        f"{API_PREFIX}/audits/pools/{{address}}/liquidity"
                    ]
                }
            },
            "features": [
                "Simple token analysis",
                "Comprehensive token audits", 
                "Pool liquidity analysis",
                "Pool economic analysis",
                "Batch processing",
                "Comparative analysis",
                "Real-time safety checks"
            ],
            "integrations": [
                "Wallet integrations",
                "Trading bots",
                "DeFi applications",
                "Web applications",
                "AI agents"
            ]
        }

# Register middleware and routers
register_middleware(app)
register_routers(app)

# Test logging endpoint (only in development)
if os.getenv("ENV", "development") == "development":
    @app.get("/test-log", tags=["debug"])
    async def test_log():
        """Test logging at different levels.
        
        This endpoint is for development and testing purposes only.
        
        Returns:
            Dictionary with test results
        """
        results = {
            "debug": "Debug message logged",
            "info": "Info message logged",
            "warning": "Warning message logged",
            "error": "Error message logged",
            "critical": "Critical message logged",
        }
        
        # Log messages at different levels
        logger.debug("This is a debug message")
        logger.info("This is an info message")
        logger.warning("This is a warning message")
        logger.error("This is an error message")
        logger.critical("This is a critical message")
        
        # Log with context
        logger.info(
            "Test log with context",
            extra={
                "context": {
                    "user_id": "test_user",
                    "action": "test_log",
                    "status": "success"
                }
            }
        )
        
        return {
            "status": "success",
            "message": "Test logs generated",
            "results": results,
            "timestamp": datetime.utcnow().isoformat(),
            "log_file": "logs/app.log",
            "log_level": logging.getLevelName(logger.getEffectiveLevel())
        }
