"""Legacy Analyzer Service

This module provides backward compatibility for the existing analyzer interface
while delegating to the new specialized token and pool analyzers.
"""

from typing import Dict, Optional, Any

from app.core.utils.logger import get_logger
from app.services.token_analyzer import token_analyzer
from app.services.pool_analyzer import pool_analyzer

logger = get_logger(__name__)

async def analyze_token(token_address: str, lp_token_address: Optional[str] = None) -> Dict[str, Any]:
    """
    Legacy function for token analysis - delegates to TokenAnalyzer.
    
    Args:
        token_address: BSC token address
        lp_token_address: Liquidity pool address (optional)
        
    Returns:
        Dictionary with analysis results
    """
    logger.info(
        "Legacy analyze_token called - delegating to TokenAnalyzer",
        context={
            "token_address": token_address,
            "lp_token_address": lp_token_address
        }
    )
    
    try:
        # Use the new TokenAnalyzer
        result = await token_analyzer.analyze_token(token_address)
        
        # If LP token address is provided, also analyze the pool
        if lp_token_address:
            logger.info("LP token provided, analyzing pool as well")
            pool_result = await pool_analyzer.analyze_pool(lp_token_address, token_address)
            
            # Merge pool information into the token analysis result
            if "lp_lock" not in result:
                result["lp_lock"] = {}
            
            result["lp_lock"].update({
                "locked": pool_result.get("liquidity_lock", {}).get("is_locked", False),
                "percent_locked": pool_result.get("liquidity_lock", {}).get("lock_percentage", 0.0),
                "lock_duration": pool_result.get("liquidity_lock", {}).get("lock_duration"),
                "unlock_date": pool_result.get("liquidity_lock", {}).get("unlock_date"),
                "pool_analysis": pool_result
            })
        
        return result
        
    except Exception as e:
        logger.error(
            "Legacy analyze_token failed",
            context={
                "token_address": token_address,
                "lp_token_address": lp_token_address,
                "error": str(e),
                "error_type": type(e).__name__
            },
            exc_info=True
        )
        
        # Return error response in legacy format
        from app.schemas.analyze_response import AnalyzeResponse
        return AnalyzeResponse.create_error_response(
            token_address=token_address,
            error=str(e)
        )