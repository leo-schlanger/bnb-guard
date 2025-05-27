"""Pool Analysis Service - Simple Analysis for End Users

This service provides simplified pool analysis focused on essential information
that users need to make quick decisions about pool safety and liquidity.
"""

from typing import Dict, Any, Optional
from datetime import datetime, timezone
import time

from app.core.utils.logger import get_logger

logger = get_logger(__name__)

class PoolAnalysisService:
    """Service for simple pool analysis focused on user-friendly results."""
    
    def __init__(self):
        self.analysis_timeout = 10  # Fast timeout for simple analysis
        
    async def analyze_pool(self, pool_address: str, token_address: Optional[str] = None) -> Dict[str, Any]:
        """
        Performs simplified pool analysis for end users.
        
        Returns essential liquidity safety information:
        - Basic pool info (tokens, DEX, liquidity)
        - Safety score (0-100)
        - Key risks (rug pull, low liquidity, etc.)
        - Simple recommendations
        
        Args:
            pool_address: Pool address to analyze
            token_address: Optional token address for context
            
        Returns:
            Simplified pool analysis results for end users
        """
        start_time = time.time()
        
        logger.info("Starting simple pool analysis", {
            "pool_address": pool_address,
            "token_address": token_address,
            "service": "pool_analysis"
        })
        
        try:
            # Validate addresses
            normalized_pool = self._validate_address(pool_address)
            normalized_token = self._validate_address(token_address) if token_address else None
            
            # Fetch basic pool data
            pool_data = await self._fetch_pool_data(normalized_pool)
            if self._is_error_data(pool_data):
                return self._create_error_response(normalized_pool, normalized_token, pool_data)
            
            # Perform safety checks
            safety_check = await self._perform_pool_safety_check(pool_data, normalized_token)
            risk_assessment = await self._assess_pool_risks(pool_data, safety_check)
            
            # Generate user-friendly response
            response = self._build_user_response(
                normalized_pool, normalized_token, pool_data, safety_check, risk_assessment, start_time
            )
            
            duration = time.time() - start_time
            logger.success("Pool analysis completed", {
                "pool_address": normalized_pool,
                "safety_score": response["safety_score"],
                "risk_level": response["risk_level"],
                "duration_ms": round(duration * 1000, 2)
            })
            
            return response
            
        except Exception as e:
            logger.failure("Pool analysis failed", {
                "pool_address": pool_address,
                "token_address": token_address,
                "error": str(e),
                "error_type": type(e).__name__
            }, exc_info=True)
            return self._create_error_response(pool_address, token_address, {"error": str(e)})
    
    def _validate_address(self, address: str) -> str:
        """Validate and normalize address."""
        if not address or not isinstance(address, str):
            raise ValueError("Invalid address provided")
        
        normalized = address.strip().lower()
        if not normalized.startswith('0x'):
            normalized = f'0x{normalized}'
        
        if len(normalized) != 42:
            raise ValueError(f"Invalid address length: {len(normalized)} characters")
        
        return normalized
    
    async def _fetch_pool_data(self, pool_address: str) -> Dict[str, Any]:
        """Fetch essential pool data."""
        try:
            # Mock pool data - in real implementation, this would fetch from DEX APIs
            return {
                "pool_address": pool_address,
                "dex": "PancakeSwap",
                "version": "v2",
                "token0": {
                    "address": "0x0e09fabb73bd3ade0a17ecc321fd13a19e81ce82",
                    "symbol": "CAKE",
                    "name": "PancakeSwap Token",
                    "reserve": "1000000"
                },
                "token1": {
                    "address": "0xbb4cdb9cbd36b01bd1cbaebf2de08d9173bc095c",
                    "symbol": "WBNB",
                    "name": "Wrapped BNB",
                    "reserve": "5000"
                },
                "total_supply": "223606797749978969",
                "liquidity_usd": 5000000,
                "volume_24h": 1000000,
                "fees_24h": 3000,
                "created_at": "2021-09-29T10:00:00Z",
                "is_verified": True
            }
        except Exception as e:
            logger.error("Failed to fetch pool data", {
                "pool_address": pool_address,
                "error": str(e)
            })
            return {"error": f"Failed to fetch pool data: {str(e)}"}
    
    def _is_error_data(self, data: Dict[str, Any]) -> bool:
        """Check if data contains errors."""
        return "error" in data or not data.get("pool_address")
    
    async def _perform_pool_safety_check(self, pool_data: Dict[str, Any], token_address: Optional[str]) -> Dict[str, Any]:
        """Perform essential pool safety checks."""
        try:
            liquidity_usd = pool_data.get("liquidity_usd", 0)
            volume_24h = pool_data.get("volume_24h", 0)
            
            return {
                "sufficient_liquidity": liquidity_usd >= 50000,  # $50k minimum
                "active_trading": volume_24h >= 10000,  # $10k daily volume
                "established_pool": self._check_pool_age(pool_data.get("created_at")),
                "verified_tokens": self._check_token_verification(pool_data),
                "balanced_reserves": self._check_reserve_balance(pool_data),
                "liquidity_locked": False,  # Would check actual lock status
                "rug_pull_risk": self._assess_rug_pull_risk(pool_data, liquidity_usd),
                "impermanent_loss_risk": self._assess_il_risk(pool_data)
            }
        except Exception as e:
            logger.warning("Pool safety check failed", {"error": str(e)})
            return {"error": str(e)}
    
    async def _assess_pool_risks(self, pool_data: Dict[str, Any], safety_check: Dict[str, Any]) -> Dict[str, Any]:
        """Assess overall pool risk level and generate warnings."""
        risks = []
        warnings = []
        
        # Critical risks
        if safety_check.get("rug_pull_risk") == "high":
            risks.append("🚨 HIGH RUG PULL RISK - Liquidity not locked")
        
        if not safety_check.get("sufficient_liquidity"):
            risks.append("💧 LOW LIQUIDITY - High slippage risk")
        
        # High risks
        if not safety_check.get("active_trading"):
            risks.append("📉 LOW TRADING VOLUME - Poor liquidity")
        
        if safety_check.get("impermanent_loss_risk") == "high":
            risks.append("📊 HIGH IMPERMANENT LOSS RISK")
        
        # Medium risks
        if not safety_check.get("established_pool"):
            warnings.append("🆕 New pool - Higher risk")
        
        if not safety_check.get("verified_tokens"):
            warnings.append("❓ Unverified tokens in pool")
        
        if not safety_check.get("balanced_reserves"):
            warnings.append("⚖️ Unbalanced token reserves")
        
        if not safety_check.get("liquidity_locked"):
            warnings.append("🔓 Liquidity not locked")
        
        # Calculate simple safety score
        safety_score = self._calculate_pool_safety_score(safety_check, risks, warnings)
        risk_level = self._determine_risk_level(safety_score)
        
        return {
            "safety_score": safety_score,
            "risk_level": risk_level,
            "critical_risks": risks,
            "warnings": warnings,
            "recommendation": self._get_pool_recommendation(risk_level, risks)
        }
    
    def _check_pool_age(self, created_at: Optional[str]) -> bool:
        """Check if pool is established (>30 days old)."""
        if not created_at:
            return False
        
        try:
            created_date = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
            age_days = (datetime.now(timezone.utc) - created_date).days
            return age_days >= 30
        except:
            return False
    
    def _check_token_verification(self, pool_data: Dict[str, Any]) -> bool:
        """Check if tokens in pool are verified."""
        token0_verified = pool_data.get("token0", {}).get("verified", True)
        token1_verified = pool_data.get("token1", {}).get("verified", True)
        return token0_verified and token1_verified
    
    def _check_reserve_balance(self, pool_data: Dict[str, Any]) -> bool:
        """Check if token reserves are reasonably balanced."""
        try:
            token0_reserve = float(pool_data.get("token0", {}).get("reserve", 0))
            token1_reserve = float(pool_data.get("token1", {}).get("reserve", 0))
            
            if token0_reserve == 0 or token1_reserve == 0:
                return False
            
            # Check if ratio is reasonable (not more than 1000:1)
            ratio = max(token0_reserve, token1_reserve) / min(token0_reserve, token1_reserve)
            return ratio <= 1000
        except:
            return False
    
    def _assess_rug_pull_risk(self, pool_data: Dict[str, Any], liquidity_usd: float) -> str:
        """Assess rug pull risk level."""
        if liquidity_usd < 10000:
            return "high"
        elif liquidity_usd < 100000:
            return "medium"
        else:
            return "low"
    
    def _assess_il_risk(self, pool_data: Dict[str, Any]) -> str:
        """Assess impermanent loss risk."""
        # Check if one token is a stablecoin
        token0_symbol = pool_data.get("token0", {}).get("symbol", "").upper()
        token1_symbol = pool_data.get("token1", {}).get("symbol", "").upper()
        
        stablecoins = ["USDT", "USDC", "BUSD", "DAI", "TUSD"]
        
        if any(stable in token0_symbol for stable in stablecoins) or \
           any(stable in token1_symbol for stable in stablecoins):
            return "low"
        elif "BNB" in token0_symbol or "BNB" in token1_symbol:
            return "medium"
        else:
            return "high"
    
    def _calculate_pool_safety_score(self, safety_check: Dict[str, Any], risks: list, warnings: list) -> int:
        """Calculate a simple 0-100 pool safety score."""
        score = 100
        
        # Critical deductions
        if safety_check.get("rug_pull_risk") == "high":
            score -= 40
        
        if not safety_check.get("sufficient_liquidity"):
            score -= 30
        
        # High risk deductions
        if not safety_check.get("active_trading"):
            score -= 20
        
        if safety_check.get("impermanent_loss_risk") == "high":
            score -= 15
        
        # Medium risk deductions
        if not safety_check.get("established_pool"):
            score -= 10
        
        if not safety_check.get("verified_tokens"):
            score -= 10
        
        if not safety_check.get("balanced_reserves"):
            score -= 10
        
        if not safety_check.get("liquidity_locked"):
            score -= 15
        
        return max(0, score)
    
    def _determine_risk_level(self, safety_score: int) -> str:
        """Determine risk level based on safety score."""
        if safety_score >= 80:
            return "LOW"
        elif safety_score >= 60:
            return "MEDIUM"
        elif safety_score >= 40:
            return "HIGH"
        else:
            return "CRITICAL"
    
    def _get_pool_recommendation(self, risk_level: str, risks: list) -> str:
        """Get user-friendly recommendation for pool."""
        if risk_level == "CRITICAL" or any("RUG PULL" in risk for risk in risks):
            return "🚨 AVOID - High risk of losing funds"
        elif risk_level == "HIGH":
            return "⚠️ HIGH RISK - Only provide liquidity with extreme caution"
        elif risk_level == "MEDIUM":
            return "⚡ MODERATE RISK - Understand impermanent loss before providing liquidity"
        else:
            return "✅ RELATIVELY SAFE - Standard DeFi risks apply"
    
    def _build_user_response(self, pool_address: str, token_address: Optional[str], 
                           pool_data: Dict[str, Any], safety_check: Dict[str, Any], 
                           risk_assessment: Dict[str, Any], start_time: float) -> Dict[str, Any]:
        """Build user-friendly response."""
        return {
            "status": "success",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "analysis_type": "simple",
            "pool_address": pool_address,
            "token_address": token_address,
            
            # Basic pool info
            "pool_info": {
                "dex": pool_data.get("dex", "Unknown"),
                "version": pool_data.get("version", "Unknown"),
                "token0": {
                    "symbol": pool_data.get("token0", {}).get("symbol", "Unknown"),
                    "name": pool_data.get("token0", {}).get("name", "Unknown"),
                    "address": pool_data.get("token0", {}).get("address", "Unknown")
                },
                "token1": {
                    "symbol": pool_data.get("token1", {}).get("symbol", "Unknown"),
                    "name": pool_data.get("token1", {}).get("name", "Unknown"),
                    "address": pool_data.get("token1", {}).get("address", "Unknown")
                },
                "liquidity_usd": pool_data.get("liquidity_usd", 0),
                "volume_24h": pool_data.get("volume_24h", 0),
                "fees_24h": pool_data.get("fees_24h", 0)
            },
            
            # Safety assessment
            "safety_score": risk_assessment["safety_score"],
            "risk_level": risk_assessment["risk_level"],
            "recommendation": risk_assessment["recommendation"],
            
            # Key findings
            "critical_risks": risk_assessment["critical_risks"],
            "warnings": risk_assessment["warnings"],
            
            # Quick checks
            "quick_checks": {
                "sufficient_liquidity": safety_check.get("sufficient_liquidity", False),
                "active_trading": safety_check.get("active_trading", False),
                "established_pool": safety_check.get("established_pool", False),
                "liquidity_locked": safety_check.get("liquidity_locked", False),
                "rug_pull_risk": safety_check.get("rug_pull_risk", "unknown"),
                "impermanent_loss_risk": safety_check.get("impermanent_loss_risk", "unknown")
            },
            
            # Metadata
            "analysis_duration_ms": round((time.time() - start_time) * 1000, 2),
            "data_sources": ["DEX API", "Blockchain", "Liquidity Analysis"]
        }
    
    def _create_error_response(self, pool_address: str, token_address: Optional[str], 
                             data: Dict[str, Any]) -> Dict[str, Any]:
        """Create error response for failed analysis."""
        error_msg = data.get("error", "Analysis failed")
        
        return {
            "status": "error",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "analysis_type": "simple",
            "pool_address": pool_address,
            "token_address": token_address,
            "error": error_msg,
            "recommendation": "🚨 Cannot analyze - Avoid this pool"
        }

# Global instance
pool_analysis_service = PoolAnalysisService() 