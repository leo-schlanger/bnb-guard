import os
import sys
import logging
from pathlib import Path

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

# Now import other dependencies
try:
    from contextlib import asynccontextmanager
    from fastapi import FastAPI, Request, status
    from fastapi.responses import JSONResponse
    from fastapi.exceptions import RequestValidationError
    logger.debug("Successfully imported FastAPI and dependencies")
except ImportError as e:
    logger.error(f"Failed to import required dependencies: {e}")
    raise

from app.routes.analyze import router as analyze_router
from app.routes.audit import router as audit_router
from app.routes.test_logs import router as test_logs_router
from app.routes.simple_health import router as health_router

# Import all routers
API_PREFIX = "/api/v1"

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
]

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle application startup and shutdown events."""
    # Startup
    logger.info("Starting BNBGuard API service")
    try:
        yield
    finally:
        # Shutdown
        logger.info("Shutting down BNBGuard API service", context={"service": "BNBGuard API"})

# Exception handlers
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle request validation errors."""
    logger.error(
        "Request validation error",
        context={"path": str(request.url.path), "errors": str(exc.errors())},
    )
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": exc.errors(), "body": exc.body},
    )

async def global_exception_handler(request: Request, exc: Exception):
    """Handle all unhandled exceptions."""
    logger.error(
        "Unhandled exception",
        exc_info=exc,
        context={"path": str(request.url.path), "error": str(exc)},
    )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error"},
    )

# Initialize FastAPI with metadata and lifespan
app = FastAPI(
    title="BNBGuard API",
    description="Automated risk analysis for BNB Chain tokens",
    version="1.0.0",
    openapi_tags=tags_metadata,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Add exception handlers
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, global_exception_handler)

# Add middleware for request/response logging
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Middleware to log all incoming requests and responses."""
    logger.info(
        "Request received",
        context={
            "method": request.method,
            "url": str(request.url),
            "client": request.client.host if request.client else "unknown"
        }
    )
    
    # Log detailed request info at debug level
    logger.debug(
        "Request details",
        context={
            "method": request.method,
            "url": str(request.url),
            "headers": dict(request.headers),
            "query_params": dict(request.query_params),
            "path_params": request.path_params,
            "client": request.client.host if request.client else "unknown"
        }
    )
    
    try:
        response = await call_next(request)
        
        logger.info(
            "Request completed",
            context={
                "method": request.method,
                "url": str(request.url),
                "status_code": response.status_code
            }
        )
        
        # Log detailed response info at debug level
        logger.debug(
            "Response details",
            context={
                "method": request.method,
                "url": str(request.url),
                "status_code": response.status_code,
                "response_headers": dict(response.headers)
            }
        )
        
        return response
        
    except Exception as e:
        logger.error(
            "Request processing failed",
            context={
                "method": request.method,
                "url": str(request.url),
                "error": str(e)
            },
            exc_info=True
        )
        raise

# Add the logging middleware after it's defined
app.middleware("http")(log_requests)

# Include all API routers
app.include_router(analyze_router, prefix=API_PREFIX)
app.include_router(audit_router, prefix=API_PREFIX)
app.include_router(test_logs_router, prefix=API_PREFIX)
app.include_router(health_router, prefix=API_PREFIX)

# Legacy health check endpoint - redirects to the new health check API
@app.get("/health", tags=["health"], deprecated=True)
async def health_check():
    """Legacy health check endpoint (deprecated)."""
    logger.info("Legacy health check endpoint accessed")
    return {"status": "ok", "timestamp": datetime.now().isoformat(), "message": "This endpoint is deprecated. Please use /api/v1/health instead."}

# Root endpoint with API information
@app.get("/", tags=["root"])
async def root():
    """Root endpoint with API information."""
    logger.info("Root endpoint accessed")
    return {
        "name": "BNBGuard API",
        "version": "1.0.0",
        "description": "API for analyzing and auditing BSC token contracts",
        "documentation": "/docs",
        "redoc": "/redoc",
        "health": "/health",
        "test_logs": "/test-log"
    }

# Test logging endpoint
@app.get("/test-log", tags=["test"])
async def test_log():
    """Test logging at different levels."""
    test_logger = logging.getLogger("app.test")
    
    # Log messages at different levels
    test_logger.debug("This is a DEBUG message")
    test_logger.info("This is an INFO message")
    test_logger.warning("This is a WARNING message")
    test_logger.error("This is an ERROR message")
    
    # Test exception logging
    try:
        1 / 0
    except Exception as e:
        test_logger.exception("This is an ERROR with exception")
    
    # Also log with the main logger
    logger.info("Test log endpoint was called")
    
    return {
        "status": "Logging test completed",
        "log_file": "logs/app.log",
        "log_level": logging.getLevelName(logger.getEffectiveLevel())
    }
