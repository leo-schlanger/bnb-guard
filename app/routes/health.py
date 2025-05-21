"""
Health check routes for system monitoring.
"""
import os
import sys
import time
import platform
import logging
import psutil
from datetime import datetime, timedelta
from typing import Dict, Any, List
from fastapi import Request

from app.routes.base import BaseRouter
from app.core.utils.logger import get_logger
from app.core.config import settings

# Get logger for this module
logger = get_logger("app.routes.health")

class HealthRouter(BaseRouter):
    """Router for health check endpoints."""
    
    def __init__(self):
        """Initialize health check routes."""
        super().__init__(
            prefix="/health",
            tags=["system"]
        )
        self._setup_routes()
        self._start_time = time.time()
    
    def _setup_routes(self):
        """Define health check routes."""
        self.router.add_api_route(
            path="",
            endpoint=self.basic_health,
            methods=["GET"],
            response_model=Dict[str, Any],
            summary="Basic health check",
            description="Basic health check endpoint that returns service status"
        )
        
        self.router.add_api_route(
            path="/detailed",
            endpoint=self.detailed_health,
            methods=["GET"],
            response_model=Dict[str, Any],
            summary="Detailed health check",
            description="Detailed health check with system information and metrics"
        )
        
        self.router.add_api_route(
            path="/logs",
            endpoint=self.logs_health,
            methods=["GET"],
            response_model=Dict[str, Any],
            summary="Logs health check",
            description="Check logging system status and recent log entries"
        )
    
    async def basic_health(self, request: Request) -> Dict[str, Any]:
        """
        Basic health check endpoint.
        
        Args:
            request: FastAPI request object
            
        Returns:
            Dictionary with basic health status
        """
        context = await self._get_request_context(request)
        logger.info("Basic health check requested", context=context)
        
        uptime = time.time() - self._start_time
        uptime_formatted = str(timedelta(seconds=int(uptime)))
        
        return {
            "status": "ok",
            "service": settings.PROJECT_NAME,
            "version": settings.VERSION,
            "environment": settings.ENV,
            "timestamp": datetime.now().isoformat(),
            "uptime": uptime_formatted
        }
    
    async def detailed_health(self, request: Request) -> Dict[str, Any]:
        """
        Detailed health check with system information.
        
        Args:
            request: FastAPI request object
            
        Returns:
            Dictionary with detailed health information
        """
        context = await self._get_request_context(request)
        logger.info("Detailed health check requested", context=context)
        
        # Basic info
        uptime = time.time() - self._start_time
        uptime_formatted = str(timedelta(seconds=int(uptime)))
        
        # System info
        try:
            cpu_percent = psutil.cpu_percent(interval=0.1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
        except Exception as e:
            logger.warning(f"Error getting system metrics: {str(e)}", context=context)
            cpu_percent = None
            memory = None
            disk = None
        
        # Python info
        python_info = {
            "version": sys.version,
            "platform": platform.platform(),
            "implementation": platform.python_implementation()
        }
        
        # Environment variables (non-sensitive)
        env_vars = {
            "LOG_LEVEL": os.getenv("LOG_LEVEL"),
            "ENV": os.getenv("ENV"),
            "DEBUG": os.getenv("DEBUG")
        }
        
        return {
            "status": "ok",
            "service": settings.PROJECT_NAME,
            "version": settings.VERSION,
            "environment": settings.ENV,
            "timestamp": datetime.now().isoformat(),
            "uptime": uptime_formatted,
            "system": {
                "cpu_percent": cpu_percent,
                "memory": {
                    "total": memory.total if memory else None,
                    "available": memory.available if memory else None,
                    "percent": memory.percent if memory else None
                } if memory else None,
                "disk": {
                    "total": disk.total if disk else None,
                    "free": disk.free if disk else None,
                    "percent": disk.percent if disk else None
                } if disk else None,
                "python": python_info
            },
            "config": {
                "environment": env_vars,
                "settings": {
                    "project_name": settings.PROJECT_NAME,
                    "version": settings.VERSION,
                    "description": settings.DESCRIPTION,
                    "debug": settings.DEBUG,
                    "env": settings.ENV,
                    "log_level": settings.LOG_LEVEL,
                    "max_tokens_per_day": settings.MAX_TOKENS_PER_DAY,
                    "request_timeout": settings.REQUEST_TIMEOUT
                }
            }
        }
    
    async def logs_health(self, request: Request) -> Dict[str, Any]:
        """
        Check logging system status.
        
        Args:
            request: FastAPI request object
            
        Returns:
            Dictionary with logging system status
        """
        context = await self._get_request_context(request)
        logger.info("Logs health check requested", context=context)
        
        # Check logs directory
        logs_dir = "logs"
        log_files = []
        
        if os.path.exists(logs_dir):
            for file in os.listdir(logs_dir):
                if file.endswith(".log"):
                    file_path = os.path.join(logs_dir, file)
                    file_size = os.path.getsize(file_path)
                    file_modified = os.path.getmtime(file_path)
                    
                    # Get last few lines of the log file
                    last_lines = []
                    try:
                        with open(file_path, 'r') as f:
                            lines = f.readlines()
                            last_lines = lines[-5:] if len(lines) >= 5 else lines
                    except Exception as e:
                        logger.warning(f"Error reading log file {file}: {str(e)}", context=context)
                    
                    log_files.append({
                        "name": file,
                        "size_bytes": file_size,
                        "last_modified": datetime.fromtimestamp(file_modified).isoformat(),
                        "last_lines": last_lines
                    })
        
        # Get root logger info
        root_logger = logging.getLogger()
        app_logger = logging.getLogger("app")
        
        logger_info = {
            "root_level": logging.getLevelName(root_logger.level),
            "app_level": logging.getLevelName(app_logger.level),
            "handlers": [
                {
                    "type": type(handler).__name__,
                    "level": logging.getLevelName(handler.level)
                }
                for handler in root_logger.handlers
            ]
        }
        
        # Generate a test log message
        test_log_id = f"health-check-{int(time.time())}"
        logger.debug(f"Test log message from health check", context={"test_id": test_log_id})
        
        return {
            "status": "ok",
            "timestamp": datetime.now().isoformat(),
            "logging": {
                "config": logger_info,
                "log_files": log_files,
                "test_log_id": test_log_id
            }
        }

# Create router instance
router = HealthRouter().router
