"""
Health check routes for system monitoring.
"""
import os
import sys
import time
import platform
import requests
import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, List
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from web3 import Web3

# Get logger for this module
import logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(
    prefix="/health",
    tags=["system"]
)

# Store start time
START_TIME = time.time()

# BSC RPC URL
BSC_RPC_URL = os.getenv("BSC_RPC_URL", "https://bsc-dataseed.binance.org")

# BscScan API URL
BSCSCAN_API_URL = "https://api.bscscan.com/api"
BSCSCAN_API_KEY = os.getenv("BSCSCAN_API_KEY")

async def check_external_services() -> List[Dict[str, Any]]:
    """
    Check the status of external services.
    
    Returns:
        List of dictionaries with service status information
    """
    services = []
    
    # Check BSC Node
    try:
        start_time = time.time()
        w3 = Web3(Web3.HTTPProvider(BSC_RPC_URL))
        is_connected = w3.is_connected()
        chain_id = None
        block_number = None
        response_time = time.time() - start_time
        
        if is_connected:
            try:
                chain_id = w3.eth.chain_id
                block_number = w3.eth.block_number
            except Exception as e:
                logger.warning(f"Error getting BSC chain details: {str(e)}")
        
        services.append({
            "name": "BSC Node",
            "url": BSC_RPC_URL,
            "status": "ok" if is_connected else "error",
            "response_time_ms": round(response_time * 1000, 2),
            "details": {
                "connected": is_connected,
                "chain_id": chain_id,
                "block_number": block_number
            }
        })
    except Exception as e:
        logger.error(f"Error connecting to BSC Node: {str(e)}")
        services.append({
            "name": "BSC Node",
            "url": BSC_RPC_URL,
            "status": "error",
            "error": str(e)
        })
    
    # Check BscScan API
    try:
        start_time = time.time()
        params = {
            "module": "proxy",
            "action": "eth_blockNumber",
            "apikey": BSCSCAN_API_KEY
        }
        
        response = requests.get(BSCSCAN_API_URL, params=params, timeout=5)
        response_time = time.time() - start_time
        
        if response.status_code == 200:
            data = response.json()
            status = "ok" if data.get("status") != "0" else "error"
            services.append({
                "name": "BscScan API",
                "url": BSCSCAN_API_URL,
                "status": status,
                "response_time_ms": round(response_time * 1000, 2),
                "details": {
                    "status_code": response.status_code,
                    "api_response": data
                }
            })
        else:
            services.append({
                "name": "BscScan API",
                "url": BSCSCAN_API_URL,
                "status": "error",
                "response_time_ms": round(response_time * 1000, 2),
                "details": {
                    "status_code": response.status_code,
                    "reason": response.reason
                }
            })
    except Exception as e:
        logger.error(f"Error connecting to BscScan API: {str(e)}")
        services.append({
            "name": "BscScan API",
            "url": BSCSCAN_API_URL,
            "status": "error",
            "error": str(e)
        })
    
    return services

@router.get("", summary="Basic health check")
async def basic_health(request: Request) -> Dict[str, Any]:
    """
    Basic health check endpoint.
    
    Args:
        request: FastAPI request object
        
    Returns:
        Dictionary with basic health status
    """
    logger.info("Basic health check requested")
    
    uptime = time.time() - START_TIME
    uptime_formatted = str(timedelta(seconds=int(uptime)))
    
    return {
        "status": "ok",
        "timestamp": datetime.now().isoformat(),
        "uptime": uptime_formatted,
        "environment": os.getenv("ENV", "development")
    }

@router.get("/detailed", summary="Detailed health check")
async def detailed_health(request: Request) -> Dict[str, Any]:
    """
    Detailed health check with system information.
    
    Args:
        request: FastAPI request object
        
    Returns:
        Dictionary with detailed health information
    """
    logger.info("Detailed health check requested")
    
    # Basic info
    uptime = time.time() - START_TIME
    uptime_formatted = str(timedelta(seconds=int(uptime)))
    
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
    
    # Check external services
    external_services = await check_external_services()
    
    # Determine overall status
    overall_status = "ok"
    for service in external_services:
        if service["status"] != "ok":
            overall_status = "degraded"
            break
    
    return {
        "status": overall_status,
        "timestamp": datetime.now().isoformat(),
        "uptime": uptime_formatted,
        "system": {
            "python": python_info
        },
        "config": {
            "environment": env_vars
        },
        "services": external_services
    }

@router.get("/services", summary="External services health check")
async def external_services_health(request: Request) -> Dict[str, Any]:
    """
    Check external services status.
    
    Args:
        request: FastAPI request object
        
    Returns:
        Dictionary with external services status
    """
    logger.info("Services health check requested")
    
    services = await check_external_services()
    
    # Determine overall status
    overall_status = "ok"
    for service in services:
        if service["status"] != "ok":
            overall_status = "degraded"
            break
    
    return {
        "status": overall_status,
        "timestamp": datetime.now().isoformat(),
        "services": services
    }

@router.get("/logs", summary="Logging system health check")
async def logs_health(request: Request) -> Dict[str, Any]:
    """
    Check logging system status.
    
    Args:
        request: FastAPI request object
        
    Returns:
        Dictionary with logging system status
    """
    logger.info("Logs health check requested")
    
    # Test logging at different levels
    logger.debug("Debug test message from health check")
    logger.info("Info test message from health check")
    logger.warning("Warning test message from health check")
    
    return {
        "status": "ok",
        "timestamp": datetime.now().isoformat(),
        "logging": {
            "level": os.getenv("LOG_LEVEL", "INFO"),
            "test_messages": [
                {"level": "DEBUG", "message": "Debug test message from health check"},
                {"level": "INFO", "message": "Info test message from health check"},
                {"level": "WARNING", "message": "Warning test message from health check"}
            ]
        }
    }


