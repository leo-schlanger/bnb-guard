"""Analysis Routes - Simple Analysis for End Users

This module contains API routes for simple analysis functionality,
designed for end users who need quick safety assessments.
"""

from fastapi import APIRouter, HTTPException, Path, Query
from typing import Optional
import time

from app.core.utils.logger import get_logger
from app.services.token_analysis_service import token_analysis_service
from app.services.pool_analysis_service import pool_analysis_service

logger = get_logger(__name__)

router = APIRouter(tags=["analysis"])

# ============================================================================
# TOKEN ANALYSIS ROUTES
# ============================================================================

@router.get("/tokens/{token_address}")
async def analyze_token_simple(
    token_address: str = Path(..., description="Token address to analyze")
):
    """
    Simple token analysis for end users.
    
    Returns essential safety information in a user-friendly format:
    - Basic token info (name, symbol, supply)
    - Safety score (0-100) 
    - Key risks (honeypot, high fees, etc.)
    - Simple recommendations
    
    Perfect for:
    - Wallet integrations
    - Bot commands
    - Quick safety checks
    - Mobile apps
    
    Args:
        token_address: The token address to analyze
        
    Returns:
        Simplified analysis results with safety score and recommendations
    """
    logger.info("Simple token analysis request", {
        "token_address": token_address,
        "endpoint": "/analysis/tokens"
    })
    
    try:
        start_time = time.time()
        result = await token_analysis_service.analyze_token(token_address)
        duration = time.time() - start_time
        
        if result.get("status") == "error":
            error_msg = result.get("error", "Analysis failed")
            logger.warning("Token analysis returned error", {
                "token_address": token_address,
                "error": error_msg
            })
            raise HTTPException(
                status_code=400,
                detail=f"Token analysis failed: {error_msg}"
            )
        
        logger.success("Simple token analysis completed", {
            "token_address": token_address,
            "safety_score": result.get("safety_score"),
            "risk_level": result.get("risk_level"),
            "duration_ms": round(duration * 1000, 2)
        })
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Token analysis endpoint failed", {
            "token_address": token_address,
            "error": str(e),
            "error_type": type(e).__name__
        }, exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error during token analysis: {str(e)}"
        )

@router.get("/tokens/{token_address}/quick")
async def quick_token_check(
    token_address: str = Path(..., description="Token address for quick check")
):
    """
    Ultra-fast token safety check.
    
    Returns only the most critical information:
    - Is it a honeypot?
    - Safety score
    - Risk level
    - Simple recommendation
    
    Optimized for:
    - Real-time trading bots
    - Quick API calls
    - High-frequency checks
    
    Args:
        token_address: The token address to check
        
    Returns:
        Minimal safety information for quick decisions
    """
    logger.info("Quick token check request", {
        "token_address": token_address,
        "endpoint": "/analysis/tokens/quick"
    })
    
    try:
        result = await token_analysis_service.analyze_token(token_address)
        
        if result.get("status") == "error":
            return {
                "status": "error",
                "token_address": token_address,
                "safety_score": 0,
                "risk_level": "CRITICAL",
                "recommendation": "🚨 AVOID - Cannot analyze token",
                "error": result.get("error")
            }
        
        # Return only essential info
        quick_result = {
            "status": "success",
            "token_address": token_address,
            "safety_score": result.get("safety_score", 0),
            "risk_level": result.get("risk_level", "UNKNOWN"),
            "recommendation": result.get("recommendation", "Unknown"),
            "is_honeypot": result.get("quick_checks", {}).get("honeypot", False),
            "high_fees": result.get("quick_checks", {}).get("high_fees", False),
            "analysis_duration_ms": result.get("analysis_duration_ms", 0)
        }
        
        logger.success("Quick token check completed", {
            "token_address": token_address,
            "safety_score": quick_result["safety_score"],
            "risk_level": quick_result["risk_level"]
        })
        
        return quick_result
        
    except Exception as e:
        logger.error("Quick token check failed", {
            "token_address": token_address,
            "error": str(e)
        }, exc_info=True)
        return {
            "status": "error",
            "token_address": token_address,
            "safety_score": 0,
            "risk_level": "CRITICAL",
            "recommendation": "🚨 AVOID - Analysis failed",
            "error": str(e)
        }

# ============================================================================
# POOL ANALYSIS ROUTES
# ============================================================================

@router.get("/pools/{pool_address}")
async def analyze_pool_simple(
    pool_address: str = Path(..., description="Pool address to analyze"),
    token_address: Optional[str] = Query(None, description="Optional token address for context")
):
    """
    Simple pool analysis for end users.
    
    Returns essential liquidity safety information:
    - Basic pool info (tokens, DEX, liquidity)
    - Safety score (0-100)
    - Key risks (rug pull, low liquidity, etc.)
    - Simple recommendations
    
    Perfect for:
    - DeFi apps
    - Liquidity provider tools
    - Pool safety checks
    - Investment decisions
    
    Args:
        pool_address: The pool address to analyze
        token_address: Optional token address for additional context
        
    Returns:
        Simplified pool analysis results with safety score and recommendations
    """
    logger.info("Simple pool analysis request", {
        "pool_address": pool_address,
        "token_address": token_address,
        "endpoint": "/analysis/pools"
    })
    
    try:
        start_time = time.time()
        result = await pool_analysis_service.analyze_pool(pool_address, token_address)
        duration = time.time() - start_time
        
        if result.get("status") == "error":
            error_msg = result.get("error", "Analysis failed")
            logger.warning("Pool analysis returned error", {
                "pool_address": pool_address,
                "error": error_msg
            })
            raise HTTPException(
                status_code=400,
                detail=f"Pool analysis failed: {error_msg}"
            )
        
        logger.success("Simple pool analysis completed", {
            "pool_address": pool_address,
            "safety_score": result.get("safety_score"),
            "risk_level": result.get("risk_level"),
            "duration_ms": round(duration * 1000, 2)
        })
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Pool analysis endpoint failed", {
            "pool_address": pool_address,
            "token_address": token_address,
            "error": str(e),
            "error_type": type(e).__name__
        }, exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error during pool analysis: {str(e)}"
        )

@router.get("/pools/{pool_address}/quick")
async def quick_pool_check(
    pool_address: str = Path(..., description="Pool address for quick check")
):
    """
    Ultra-fast pool safety check.
    
    Returns only the most critical information:
    - Liquidity amount
    - Safety score
    - Risk level
    - Rug pull risk
    - Simple recommendation
    
    Optimized for:
    - DeFi trading bots
    - Quick liquidity checks
    - High-frequency analysis
    
    Args:
        pool_address: The pool address to check
        
    Returns:
        Minimal safety information for quick decisions
    """
    logger.info("Quick pool check request", {
        "pool_address": pool_address,
        "endpoint": "/analysis/pools/quick"
    })
    
    try:
        result = await pool_analysis_service.analyze_pool(pool_address)
        
        if result.get("status") == "error":
            return {
                "status": "error",
                "pool_address": pool_address,
                "safety_score": 0,
                "risk_level": "CRITICAL",
                "recommendation": "🚨 AVOID - Cannot analyze pool",
                "error": result.get("error")
            }
        
        # Return only essential info
        pool_info = result.get("pool_info", {})
        quick_checks = result.get("quick_checks", {})
        
        quick_result = {
            "status": "success",
            "pool_address": pool_address,
            "safety_score": result.get("safety_score", 0),
            "risk_level": result.get("risk_level", "UNKNOWN"),
            "recommendation": result.get("recommendation", "Unknown"),
            "liquidity_usd": pool_info.get("liquidity_usd", 0),
            "sufficient_liquidity": quick_checks.get("sufficient_liquidity", False),
            "liquidity_locked": quick_checks.get("liquidity_locked", False),
            "rug_pull_risk": quick_checks.get("rug_pull_risk", "unknown"),
            "analysis_duration_ms": result.get("analysis_duration_ms", 0)
        }
        
        logger.success("Quick pool check completed", {
            "pool_address": pool_address,
            "safety_score": quick_result["safety_score"],
            "risk_level": quick_result["risk_level"]
        })
        
        return quick_result
        
    except Exception as e:
        logger.error("Quick pool check failed", {
            "pool_address": pool_address,
            "error": str(e)
        }, exc_info=True)
        return {
            "status": "error",
            "pool_address": pool_address,
            "safety_score": 0,
            "risk_level": "CRITICAL",
            "recommendation": "🚨 AVOID - Analysis failed",
            "error": str(e)
        }

# ============================================================================
# BATCH ANALYSIS ROUTES
# ============================================================================

@router.post("/tokens/batch")
async def analyze_tokens_batch(
    token_addresses: list[str]
):
    """
    Batch analysis for multiple tokens.
    
    Analyzes multiple tokens in a single request for efficiency.
    Limited to 10 tokens per request to prevent abuse.
    
    Args:
        token_addresses: List of token addresses to analyze (max 10)
        
    Returns:
        List of analysis results for each token
    """
    if len(token_addresses) > 10:
        raise HTTPException(
            status_code=400,
            detail="Maximum 10 tokens allowed per batch request"
        )
    
    logger.info("Batch token analysis request", {
        "token_count": len(token_addresses),
        "endpoint": "/analysis/tokens/batch"
    })
    
    results = []
    for token_address in token_addresses:
        try:
            result = await token_analysis_service.analyze_token(token_address)
            results.append(result)
        except Exception as e:
            results.append({
                "status": "error",
                "token_address": token_address,
                "error": str(e),
                "safety_score": 0,
                "risk_level": "CRITICAL",
                "recommendation": "🚨 AVOID - Analysis failed"
            })
    
    logger.info("Batch token analysis completed", {
        "token_count": len(token_addresses),
        "successful": len([r for r in results if r.get("status") == "success"]),
        "failed": len([r for r in results if r.get("status") == "error"])
    })
    
    return {
        "status": "completed",
        "total_tokens": len(token_addresses),
        "results": results
    }

@router.post("/pools/batch")
async def analyze_pools_batch(
    pool_addresses: list[str]
):
    """
    Batch analysis for multiple pools.
    
    Analyzes multiple pools in a single request for efficiency.
    Limited to 5 pools per request due to complexity.
    
    Args:
        pool_addresses: List of pool addresses to analyze (max 5)
        
    Returns:
        List of analysis results for each pool
    """
    if len(pool_addresses) > 5:
        raise HTTPException(
            status_code=400,
            detail="Maximum 5 pools allowed per batch request"
        )
    
    logger.info("Batch pool analysis request", {
        "pool_count": len(pool_addresses),
        "endpoint": "/analysis/pools/batch"
    })
    
    results = []
    for pool_address in pool_addresses:
        try:
            result = await pool_analysis_service.analyze_pool(pool_address)
            results.append(result)
        except Exception as e:
            results.append({
                "status": "error",
                "pool_address": pool_address,
                "error": str(e),
                "safety_score": 0,
                "risk_level": "CRITICAL",
                "recommendation": "🚨 AVOID - Analysis failed"
            })
    
    logger.info("Batch pool analysis completed", {
        "pool_count": len(pool_addresses),
        "successful": len([r for r in results if r.get("status") == "success"]),
        "failed": len([r for r in results if r.get("status") == "error"])
    })
    
    return {
        "status": "completed",
        "total_pools": len(pool_addresses),
        "results": results
    }

# ============================================================================
# HEALTH CHECK
# ============================================================================

@router.get("/health")
async def analysis_health():
    """
    Health check for analysis services.
    
    Returns:
        Health status of all analysis services
    """
    return {
        "status": "healthy",
        "services": {
            "token_analysis": "operational",
            "pool_analysis": "operational"
        },
        "version": "1.0.0",
        "features": [
            "simple_token_analysis",
            "simple_pool_analysis", 
            "quick_checks",
            "batch_analysis"
        ]
    } 