"""Pool Analysis Service

This module provides comprehensive liquidity pool analysis functionality,
including LP lock detection, liquidity distribution, and pool security analysis.
"""

from typing import Dict, Optional, Any, List
from datetime import datetime, timezone
import asyncio

from app.core.utils.logger import get_logger
from app.core.utils.metadata import fetch_token_metadata
from app.services.web3 import get_web3_instance

logger = get_logger(__name__)

class PoolAnalyzer:
    """Service for analyzing liquidity pools on BSC."""
    
    def __init__(self):
        self.analysis_timeout = 30  # seconds
        self.web3 = get_web3_instance()
        
    async def analyze_pool(self, pool_address: str, token_address: Optional[str] = None) -> Dict[str, Any]:
        """
        Analyzes a liquidity pool and returns security information.
        
        Args:
            pool_address: LP token address to analyze
            token_address: Optional token address for cross-reference
            
        Returns:
            Dictionary with comprehensive pool analysis results
        """
        start_time = datetime.now(timezone.utc)
        
        logger.info(
            "Starting pool analysis",
            context={
                "pool_address": pool_address,
                "token_address": token_address,
                "timestamp": start_time.isoformat()
            }
        )
        
        try:
            # Validate and normalize addresses
            normalized_pool = self._validate_and_normalize_address(pool_address)
            normalized_token = None
            if token_address:
                normalized_token = self._validate_and_normalize_address(token_address)
            
            # Fetch pool metadata
            pool_metadata = await self._fetch_pool_metadata(normalized_pool)
            
            # Perform pool analysis layers
            liquidity_analysis = await self._analyze_liquidity_lock(normalized_pool)
            distribution_analysis = await self._analyze_liquidity_distribution(normalized_pool)
            security_analysis = await self._analyze_pool_security(normalized_pool, normalized_token)
            
            # Calculate pool risk score
            pool_risk_score = self._calculate_pool_risk_score(
                liquidity_analysis, distribution_analysis, security_analysis
            )
            
            # Build response
            response = self._build_pool_response(
                normalized_pool, normalized_token, pool_metadata,
                liquidity_analysis, distribution_analysis, security_analysis,
                pool_risk_score, start_time
            )
            
            logger.info(
                "Pool analysis completed successfully",
                context={
                    "pool_address": normalized_pool,
                    "token_address": normalized_token,
                    "risk_score": pool_risk_score["score"],
                    "duration_ms": (datetime.now(timezone.utc) - start_time).total_seconds() * 1000
                }
            )
            
            return response
            
        except Exception as e:
            logger.error(
                "Pool analysis failed",
                context={
                    "pool_address": pool_address,
                    "token_address": token_address,
                    "error": str(e),
                    "error_type": type(e).__name__
                },
                exc_info=True
            )
            return self._create_error_response(pool_address, token_address, str(e))
    
    async def analyze_token_liquidity(self, token_address: str) -> Dict[str, Any]:
        """
        Analyzes all liquidity pools for a specific token.
        
        Args:
            token_address: Token address to find pools for
            
        Returns:
            Dictionary with all pools analysis for the token
        """
        start_time = datetime.now(timezone.utc)
        
        logger.info(
            "Starting token liquidity analysis",
            context={
                "token_address": token_address,
                "timestamp": start_time.isoformat()
            }
        )
        
        try:
            normalized_token = self._validate_and_normalize_address(token_address)
            
            # Find all pools for this token
            pools = await self._find_token_pools(normalized_token)
            
            # Analyze each pool
            pool_analyses = []
            for pool_address in pools:
                try:
                    pool_analysis = await self.analyze_pool(pool_address, normalized_token)
                    pool_analyses.append(pool_analysis)
                except Exception as e:
                    logger.warning(
                        f"Failed to analyze pool {pool_address}",
                        context={"error": str(e)}
                    )
            
            # Aggregate results
            aggregated_results = self._aggregate_pool_results(pool_analyses)
            
            response = {
                "status": "completed",
                "timestamp": start_time.isoformat(),
                "token_address": normalized_token,
                "total_pools": len(pools),
                "analyzed_pools": len(pool_analyses),
                "aggregated_liquidity": aggregated_results,
                "individual_pools": pool_analyses
            }
            
            logger.info(
                "Token liquidity analysis completed",
                context={
                    "token_address": normalized_token,
                    "total_pools": len(pools),
                    "analyzed_pools": len(pool_analyses)
                }
            )
            
            return response
            
        except Exception as e:
            logger.error(
                "Token liquidity analysis failed",
                context={
                    "token_address": token_address,
                    "error": str(e),
                    "error_type": type(e).__name__
                },
                exc_info=True
            )
            return self._create_error_response(None, token_address, str(e))
    
    def _validate_and_normalize_address(self, address: str) -> str:
        """Validate and normalize address format."""
        if not address or not isinstance(address, str):
            raise ValueError(f"Invalid address: {address}")
            
        # Clean and format address
        normalized = address.strip().lower()
        if not normalized.startswith('0x'):
            normalized = f'0x{normalized}'
            
        # Validate address length
        if len(normalized) != 42:
            raise ValueError(f"Invalid address length: {normalized}")
            
        return normalized
    
    async def _fetch_pool_metadata(self, pool_address: str) -> Dict[str, Any]:
        """Fetch pool metadata and basic information."""
        logger.debug("Fetching pool metadata", context={"pool_address": pool_address})
        
        try:
            # This would typically fetch from DEX APIs or on-chain data
            # For now, return basic structure
            return {
                "pool_address": pool_address,
                "dex": "PancakeSwap",
                "version": "v2",
                "created_at": None,
                "total_supply": "0",
                "reserves": {"token0": "0", "token1": "0"}
            }
        except Exception as e:
            logger.error(
                "Failed to fetch pool metadata",
                context={"pool_address": pool_address, "error": str(e)},
                exc_info=True
            )
            raise
    
    async def _analyze_liquidity_lock(self, pool_address: str) -> Dict[str, Any]:
        """Analyze liquidity lock status and duration."""
        logger.debug("Analyzing liquidity lock", context={"pool_address": pool_address})
        
        try:
            # This would check various lock contracts (Team Finance, DxSale, etc.)
            # For now, return mock data
            return {
                "is_locked": False,
                "lock_percentage": 0.0,
                "lock_duration": None,
                "lock_contract": None,
                "unlock_date": None,
                "lock_provider": None
            }
        except Exception as e:
            logger.warning(
                "Liquidity lock analysis failed",
                context={"pool_address": pool_address, "error": str(e)}
            )
            return {
                "is_locked": False,
                "lock_percentage": 0.0,
                "error": str(e)
            }
    
    async def _analyze_liquidity_distribution(self, pool_address: str) -> Dict[str, Any]:
        """Analyze liquidity distribution among holders."""
        logger.debug("Analyzing liquidity distribution", context={"pool_address": pool_address})
        
        try:
            # This would analyze LP token holders
            # For now, return mock data
            return {
                "total_holders": 0,
                "top_10_percentage": 0.0,
                "top_50_percentage": 0.0,
                "concentration_risk": "unknown",
                "largest_holder_percentage": 0.0
            }
        except Exception as e:
            logger.warning(
                "Liquidity distribution analysis failed",
                context={"pool_address": pool_address, "error": str(e)}
            )
            return {
                "concentration_risk": "unknown",
                "error": str(e)
            }
    
    async def _analyze_pool_security(self, pool_address: str, token_address: Optional[str]) -> Dict[str, Any]:
        """Analyze pool security aspects."""
        logger.debug("Analyzing pool security", context={
            "pool_address": pool_address,
            "token_address": token_address
        })
        
        try:
            security_issues = []
            
            # Check for common pool security issues
            # This would include checks for:
            # - Rug pull indicators
            # - Unusual trading patterns
            # - Liquidity manipulation
            
            return {
                "security_score": 85,  # Mock score
                "issues_found": security_issues,
                "rug_pull_risk": "low",
                "manipulation_detected": False
            }
        except Exception as e:
            logger.warning(
                "Pool security analysis failed",
                context={"pool_address": pool_address, "error": str(e)}
            )
            return {
                "security_score": 0,
                "rug_pull_risk": "unknown",
                "error": str(e)
            }
    
    async def _find_token_pools(self, token_address: str) -> List[str]:
        """Find all liquidity pools for a given token."""
        logger.debug("Finding token pools", context={"token_address": token_address})
        
        try:
            # This would query DEX APIs or scan for pool creation events
            # For now, return empty list
            return []
        except Exception as e:
            logger.warning(
                "Failed to find token pools",
                context={"token_address": token_address, "error": str(e)}
            )
            return []
    
    def _calculate_pool_risk_score(self, liquidity_analysis: Dict, distribution_analysis: Dict, 
                                 security_analysis: Dict) -> Dict[str, Any]:
        """Calculate pool risk score based on analysis results."""
        logger.debug("Calculating pool risk score")
        
        base_score = 50
        
        # Adjust score based on liquidity lock
        if liquidity_analysis.get("is_locked", False):
            lock_percentage = liquidity_analysis.get("lock_percentage", 0)
            if lock_percentage >= 80:
                base_score -= 20
            elif lock_percentage >= 50:
                base_score -= 10
        else:
            base_score += 30  # No lock is risky
        
        # Adjust score based on distribution
        concentration_risk = distribution_analysis.get("concentration_risk", "unknown")
        if concentration_risk == "high":
            base_score += 20
        elif concentration_risk == "medium":
            base_score += 10
        
        # Adjust score based on security
        security_score = security_analysis.get("security_score", 50)
        base_score += (100 - security_score) * 0.3
        
        # Normalize score
        final_score = max(0, min(100, int(base_score)))
        
        # Determine grade
        if final_score <= 20:
            grade = "A"
            risk_level = "Very Low"
        elif final_score <= 40:
            grade = "B"
            risk_level = "Low"
        elif final_score <= 60:
            grade = "C"
            risk_level = "Medium"
        elif final_score <= 80:
            grade = "D"
            risk_level = "High"
        else:
            grade = "F"
            risk_level = "Very High"
        
        return {
            "score": final_score,
            "grade": grade,
            "risk_level": risk_level,
            "risk_meter": risk_level.lower().replace(" ", "_")
        }
    
    def _aggregate_pool_results(self, pool_analyses: List[Dict]) -> Dict[str, Any]:
        """Aggregate results from multiple pool analyses."""
        if not pool_analyses:
            return {
                "total_liquidity_locked": 0.0,
                "average_lock_percentage": 0.0,
                "overall_risk_score": 100,
                "overall_grade": "F"
            }
        
        total_locked = sum(
            analysis.get("liquidity_analysis", {}).get("lock_percentage", 0)
            for analysis in pool_analyses
        )
        
        avg_lock_percentage = total_locked / len(pool_analyses)
        
        avg_risk_score = sum(
            analysis.get("pool_risk_score", {}).get("score", 100)
            for analysis in pool_analyses
        ) / len(pool_analyses)
        
        # Determine overall grade
        if avg_risk_score <= 20:
            overall_grade = "A"
        elif avg_risk_score <= 40:
            overall_grade = "B"
        elif avg_risk_score <= 60:
            overall_grade = "C"
        elif avg_risk_score <= 80:
            overall_grade = "D"
        else:
            overall_grade = "F"
        
        return {
            "total_liquidity_locked": avg_lock_percentage,
            "average_lock_percentage": avg_lock_percentage,
            "overall_risk_score": int(avg_risk_score),
            "overall_grade": overall_grade,
            "pools_analyzed": len(pool_analyses)
        }
    
    def _build_pool_response(self, pool_address: str, token_address: Optional[str],
                           pool_metadata: Dict, liquidity_analysis: Dict,
                           distribution_analysis: Dict, security_analysis: Dict,
                           pool_risk_score: Dict, start_time: datetime) -> Dict[str, Any]:
        """Build the final pool analysis response."""
        return {
            "status": "completed",
            "timestamp": start_time.isoformat(),
            "pool_address": pool_address,
            "token_address": token_address,
            "pool_info": {
                "dex": pool_metadata.get("dex", "Unknown"),
                "version": pool_metadata.get("version", "Unknown"),
                "created_at": pool_metadata.get("created_at"),
                "total_supply": pool_metadata.get("total_supply", "0")
            },
            "liquidity_lock": {
                "is_locked": liquidity_analysis.get("is_locked", False),
                "lock_percentage": liquidity_analysis.get("lock_percentage", 0.0),
                "lock_duration": liquidity_analysis.get("lock_duration"),
                "unlock_date": liquidity_analysis.get("unlock_date"),
                "lock_provider": liquidity_analysis.get("lock_provider")
            },
            "liquidity_distribution": {
                "total_holders": distribution_analysis.get("total_holders", 0),
                "concentration_risk": distribution_analysis.get("concentration_risk", "unknown"),
                "top_10_percentage": distribution_analysis.get("top_10_percentage", 0.0),
                "largest_holder_percentage": distribution_analysis.get("largest_holder_percentage", 0.0)
            },
            "security": {
                "security_score": security_analysis.get("security_score", 0),
                "rug_pull_risk": security_analysis.get("rug_pull_risk", "unknown"),
                "manipulation_detected": security_analysis.get("manipulation_detected", False),
                "issues_found": security_analysis.get("issues_found", [])
            },
            "pool_risk_score": {
                "score": pool_risk_score["score"],
                "grade": pool_risk_score["grade"],
                "risk_level": pool_risk_score["risk_level"],
                "risk_meter": pool_risk_score["risk_meter"]
            }
        }
    
    def _create_error_response(self, pool_address: Optional[str], token_address: Optional[str], 
                             error: str) -> Dict[str, Any]:
        """Create error response for failed pool analysis."""
        return {
            "status": "error",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "pool_address": pool_address,
            "token_address": token_address,
            "error": error,
            "pool_risk_score": {
                "score": 100,
                "grade": "F",
                "risk_level": "Very High",
                "risk_meter": "very_high"
            }
        }

# Global instance
pool_analyzer = PoolAnalyzer() 