"""Main application module for BNBGuard API.

This module initializes the FastAPI application, sets up logging,
registers routers, middleware, and exception handlers.
"""

import os
import sys
import logging
from datetime import datetime
from pathlib import Path
from contextlib import asynccontextmanager

# Add project root to path first
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Import and setup logging first
from app.core.logging_config import setup_logging
logger = setup_logging()

# Get log level from environment
log_level = os.getenv('LOG_LEVEL', 'INFO').upper()
logger.setLevel(log_level)
logger.info(f"Logging level set to: {log_level}")
logger.info(f"Initializing BNBGuard API (log level: {log_level})")

# Import FastAPI dependencies
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware

# Import routers
from app.routes.analyze import router as analyze_router
from app.routes.audit import router as audit_router
from app.routes.health import router as health_router

# Constants
API_PREFIX = "/api/v1"
APP_VERSION = "1.0.0"

# API metadata
tags_metadata = [
    {
        "name": "analysis",
        "description": "Token analysis operations for risk assessment and metrics.",
    },
    {
        "name": "audit",
        "description": "Comprehensive security audits for token contracts.",
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

# Initialize FastAPI application
app = FastAPI(
    title="BNBGuard API",
    description="Automated risk analysis for BNB Chain tokens",
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

# Request/response logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Middleware to log all incoming requests and responses.
    
    Args:
        request: The incoming request
        call_next: The next middleware or route handler
        
    Returns:
        The response from the route handler
    """
    # Generate request ID for tracking
    request_id = f"{int(datetime.now().timestamp())}-{request.client.host if request.client else 'unknown'}"
    
    # Log incoming request
    logger.info(
        "Request received",
        context={
            "request_id": request_id,
            "method": request.method,
            "url": str(request.url),
            "client": request.client.host if request.client else "unknown"
        }
    )
    
    # Log detailed request info at debug level
    logger.debug(
        "Request details",
        context={
            "request_id": request_id,
            "method": request.method,
            "url": str(request.url),
            "headers": dict(request.headers),
            "query_params": dict(request.query_params),
            "path_params": request.path_params,
            "client": request.client.host if request.client else "unknown"
        }
    )
    
    try:
        # Process the request
        start_time = datetime.now()
        response = await call_next(request)
        process_time = (datetime.now() - start_time).total_seconds() * 1000
        
        # Log completed request
        logger.info(
            "Request completed",
            context={
                "request_id": request_id,
                "method": request.method,
                "url": str(request.url),
                "status_code": response.status_code,
                "process_time_ms": round(process_time, 2)
            }
        )
        
        # Log detailed response info at debug level
        logger.debug(
            "Response details",
            context={
                "request_id": request_id,
                "method": request.method,
                "url": str(request.url),
                "status_code": response.status_code,
                "response_headers": dict(response.headers)
            }
        )
        
        return response
        
    except Exception as e:
        # Log request processing failures
        logger.error(
            "Request processing failed",
            context={
                "request_id": request_id,
                "method": request.method,
                "url": str(request.url),
                "error": str(e)
            },
            exc_info=True
        )
        raise

# Register middleware
app.middleware("http")(log_requests)

# Register API routers
app.include_router(analyze_router, prefix=API_PREFIX)
app.include_router(audit_router, prefix=API_PREFIX)
app.include_router(health_router, prefix=API_PREFIX)

# Root endpoint with API information
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
        "description": "API for analyzing and auditing BSC token contracts",
        "endpoints": {
            "documentation": "/docs",
            "redoc": "/redoc",
            "health": f"{API_PREFIX}/health",
            "analyze": f"{API_PREFIX}/analyze/{{token_address}}",
            "audit": f"{API_PREFIX}/audit/{{token_address}}"
        }
    }

# Test logging endpoint
@app.get("/test-log", tags=["test"], include_in_schema=False)
async def test_log():
    """Test logging at different levels.
    
    This endpoint is for development and testing purposes only.
    
    Returns:
        Dictionary with test results
    """
    request_id = f"test-log-{int(datetime.now().timestamp())}"
    test_logger = logging.getLogger("app.test")
    
    # Log messages at different levels
    test_logger.debug("This is a DEBUG message", extra={"context": {"request_id": request_id}})
    test_logger.info("This is an INFO message", extra={"context": {"request_id": request_id}})
    test_logger.warning("This is a WARNING message", extra={"context": {"request_id": request_id}})
    test_logger.error("This is an ERROR message", extra={"context": {"request_id": request_id}})
    
    # Test exception logging
    try:
        1 / 0
    except Exception as e:
        test_logger.exception(
            "This is an ERROR with exception", 
            extra={"context": {"request_id": request_id}}
        )
    
    # Also log with the main logger
    logger.info("Test log endpoint was called", context={"request_id": request_id})
    
    return {
        "status": "Logging test completed",
        "log_file": "logs/app.log",
        "log_level": logging.getLevelName(logger.getEffectiveLevel()),
        "request_id": request_id
    }
