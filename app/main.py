import sys
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from app.core.utils.logger import get_logger

# Setup logger
logger = get_logger(__name__)

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__) + "/.."))

from app.routes.analyze import router as analyze_router
from app.routes.audit import router as audit_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle application startup and shutdown events."""
    # Startup
    logger.info("Starting BNBGuard API service")
    try:
        yield
    finally:
        # Shutdown
        logger.info("Shutting down BNBGuard API service")

# Exception handlers
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle request validation errors."""
    logger.error(
        "Request validation error",
        context={"path": request.url.path, "errors": exc.errors()}
    )
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": exc.errors()},
    )

async def global_exception_handler(request: Request, exc: Exception):
    """Handle all unhandled exceptions."""
    logger.critical(
        "Unhandled exception",
        context={"path": request.url.path, "error": str(exc)},
        exc_info=True
    )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error"},
    )

# Initialize FastAPI with metadata and lifespan
app = FastAPI(
    title="BNBGuard API",
    version="0.1.0",
    description="Automated risk analysis for BNB Chain tokens",
    lifespan=lifespan
)

# Add exception handlers
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, global_exception_handler)

# Add middleware for request logging
@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(
        "Request received",
        context={
            "method": request.method,
            "url": str(request.url),
            "client": request.client.host if request.client else None
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
        return response
    except Exception as e:
        logger.error(
            "Request failed",
            context={
                "method": request.method,
                "url": str(request.url),
                "error": str(e)
            },
            exc_info=True
        )
        raise

@app.get("/")
async def root():
    """Root endpoint that provides API information."""
    logger.info("Root endpoint accessed")
    return {
        "service": "BNBGuard API",
        "version": "0.1.0",
        "status": "operational",
        "endpoints": [
            {"path": "/analyze", "method": "POST", "description": "Analyze token contract"},
            {"path": "/audit", "method": "POST", "description": "Full token audit"}
        ]
    }

app.include_router(analyze_router)
app.include_router(audit_router)
