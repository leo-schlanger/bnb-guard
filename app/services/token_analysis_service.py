"""Token Analysis Service - Simple Analysis for End Users

This service provides user-friendly token analysis with essential safety information.
"""

from typing import Dict, Any, List
from datetime import datetime, timezone
import time

from app.core.utils.logger import get_logger
from app.core.utils.metadata import fetch_token_metadata
from app.core.analyzers.static_analyzer import analyze_static
from app.core.analyzers.dynamic_analyzer import analyze_dynamic_advanced, analyze_dynamic_fallback
from app.core.analyzers.onchain_analyzer import analyze_onchain
from app.core.utils.scoring import calculate_risk_score
from app.core.utils.advanced_scoring import advanced_scorer

logger = get_logger(__name__)

class TokenAnalysisService:
    """Service for simple token analysis focused on user-friendly results."""
    
    def __init__(self):
        self.analysis_timeout = 30  # Shorter timeout for quick analysis
        
    async def analyze_token(self, token_address: str) -> Dict[str, Any]:
        """
        Performs simple token analysis for end users.
        
        Returns user-friendly results including:
        - Safety score (0-100)
        - Risk level (LOW/MEDIUM/HIGH/CRITICAL)
        - Quick safety checks
        - Simple recommendation
        
        Args:
            token_address: Token address to analyze
            
        Returns:
            Simple analysis results optimized for end users
        """
        start_time = time.time()
        
        logger.info("Starting simple token analysis", {
            "token_address": token_address,
            "service": "token_analysis"
        })
        
        try:
            # Validate address
            normalized_address = self._validate_address(token_address)
            
            # Fetch metadata
            metadata = await self._fetch_metadata(normalized_address)
            if self._is_error_metadata(metadata):
                return self._create_error_response(normalized_address, metadata)
            
            # Perform essential safety checks
            safety_checks = await self._perform_safety_check(normalized_address, metadata)
            
            # Calculate simple safety score
            safety_score = self._calculate_safety_score(safety_checks)
            risk_level = self._get_risk_level(safety_score)
            recommendation = self._get_recommendation(safety_score, risk_level, safety_checks)
            
            # Build user-friendly response
            response = self._build_analysis_response(
                normalized_address, metadata, safety_checks, 
                safety_score, risk_level, recommendation, start_time
            )
            
            duration = time.time() - start_time
            logger.success("Token analysis completed", {
                "token_address": normalized_address,
                "safety_score": safety_score,
                "risk_level": risk_level,
                "duration_ms": round(duration * 1000, 2)
            })
            
            return response
            
        except Exception as e:
            logger.failure("Token analysis failed", {
                "token_address": token_address,
                "error": str(e),
                "error_type": type(e).__name__
            }, exc_info=True)
            return self._create_error_response(token_address, {"error": str(e)})
    
    async def quick_check(self, token_address: str) -> Dict[str, Any]:
        """
        Ultra-fast safety check for immediate user feedback.
        
        Args:
            token_address: Token address to check
            
        Returns:
            Quick safety assessment
        """
        start_time = time.time()
        
        logger.info("Starting quick token check", {
            "token_address": token_address,
            "service": "token_analysis"
        })
        
        try:
            normalized_address = self._validate_address(token_address)
            
            # Quick metadata fetch
            metadata = await self._fetch_metadata(normalized_address)
            if self._is_error_metadata(metadata):
                return self._create_quick_error_response(normalized_address, metadata)
            
            # Essential checks only
            quick_checks = await self._perform_quick_checks(normalized_address, metadata)
            
            # Simple scoring
            safety_score = self._calculate_quick_score(quick_checks)
            risk_level = self._get_risk_level(safety_score)
            
            response = {
                "status": "success",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "analysis_type": "quick_check",
                "token_address": normalized_address,
                "safety_score": safety_score,
                "risk_level": risk_level,
                "quick_checks": quick_checks,
                "recommendation": self._get_quick_recommendation(safety_score, risk_level),
                "analysis_duration_ms": round((time.time() - start_time) * 1000, 2)
            }
            
            logger.success("Quick check completed", {
                "token_address": normalized_address,
                "safety_score": safety_score,
                "risk_level": risk_level,
                "duration_ms": response["analysis_duration_ms"]
            })
            
            return response
            
        except Exception as e:
            logger.failure("Quick check failed", {
                "token_address": token_address,
                "error": str(e)
            }, exc_info=True)
            return self._create_quick_error_response(token_address, {"error": str(e)})
    
    def _validate_address(self, address: str) -> str:
        """Validate and normalize token address."""
        if not address or not isinstance(address, str):
            raise ValueError("Invalid token address provided")
        
        normalized = address.strip().lower()
        if not normalized.startswith('0x'):
            normalized = f'0x{normalized}'
        
        if len(normalized) != 42:
            raise ValueError(f"Invalid address length: {len(normalized)} characters")
        
        return normalized
    
    async def _fetch_metadata(self, token_address: str) -> Dict[str, Any]:
        """Fetch token metadata."""
        try:
            return fetch_token_metadata(token_address)
        except Exception as e:
            logger.error("Failed to fetch metadata", {
                "token_address": token_address,
                "error": str(e)
            })
            return {"error": f"Failed to fetch token data: {str(e)}"}
    
    def _is_error_metadata(self, metadata: Dict[str, Any]) -> bool:
        """Check if metadata contains errors."""
        return (
            "error" in metadata or
            metadata.get("name") == "Error" or
            not metadata.get("name")
        )
    
    async def _perform_safety_check(self, token_address: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Perform comprehensive safety checks using advanced honeypot detection."""
        try:
            # Quick static analysis for critical issues
            source_code = metadata.get("SourceCode", "")
            static_results = analyze_static(source_code) if source_code else {}
            
            # Advanced honeypot detection
            try:
                dynamic_results = await analyze_dynamic_advanced(token_address, metadata)
            except Exception as e:
                logger.warning("Advanced analysis failed, using fallback", {"error": str(e)})
                dynamic_results = await analyze_dynamic_fallback(token_address, str(e))
            
            # Extract honeypot information
            honeypot_info = dynamic_results.get("honeypot", {})
            
            return {
                "contract_verified": metadata.get("is_verified", False),
                "has_dangerous_functions": len(static_results.get("dangerous_functions_found", [])) > 0,
                "ownership_renounced": static_results.get("owner", {}).get("renounced", False),
                "is_honeypot": honeypot_info.get("is_honeypot", False),
                "honeypot_confidence": honeypot_info.get("confidence", 0),
                "can_buy": honeypot_info.get("can_buy", True),
                "can_sell": honeypot_info.get("can_sell", True),
                "high_fees": self._check_high_fees(dynamic_results),
                "buy_tax": dynamic_results.get("fees", {}).get("buy", 0),
                "sell_tax": dynamic_results.get("fees", {}).get("sell", 0),
                "mint_function": static_results.get("has_mint", False),
                "pause_function": static_results.get("has_pause", False),
                "blacklist_function": static_results.get("has_blacklist", False),
                "honeypot_indicators": honeypot_info.get("indicators", []),
                "honeypot_recommendation": honeypot_info.get("recommendation", ""),
                "analysis_method": dynamic_results.get("analysis_method", "unknown")
            }
        except Exception as e:
            logger.warning("Safety check failed", {"error": str(e)})
            return {"error": str(e)}
    
    async def _perform_quick_checks(self, token_address: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Perform only the most essential checks for quick response."""
        try:
            # Basic contract verification
            contract_verified = metadata.get("is_verified", False)
            
            # Quick honeypot check (simplified)
            try:
                dynamic_results = await analyze_dynamic_advanced(token_address, metadata)
                honeypot_info = dynamic_results.get("honeypot", {})
                
                return {
                    "contract_verified": contract_verified,
                    "is_honeypot": honeypot_info.get("is_honeypot", False),
                    "can_buy": honeypot_info.get("can_buy", True),
                    "can_sell": honeypot_info.get("can_sell", True),
                    "high_fees": dynamic_results.get("fees", {}).get("buy", 0) > 10 or 
                                dynamic_results.get("fees", {}).get("sell", 0) > 10,
                    "honeypot_confidence": honeypot_info.get("confidence", 0)
                }
            except Exception as e:
                logger.warning("Quick honeypot check failed", {"error": str(e)})
                return {
                    "contract_verified": contract_verified,
                    "is_honeypot": True,  # Assume worst case
                    "can_buy": False,
                    "can_sell": False,
                    "high_fees": True,
                    "honeypot_confidence": 0,
                    "error": str(e)
                }
                
        except Exception as e:
            logger.warning("Quick checks failed", {"error": str(e)})
            return {"error": str(e)}
    
    def _check_high_fees(self, dynamic_results: Dict[str, Any]) -> bool:
        """Check if token has high trading fees."""
        fees = dynamic_results.get("fees", {})
        buy_fee = fees.get("buy", 0)
        sell_fee = fees.get("sell", 0)
        return buy_fee > 10 or sell_fee > 10
    
    def _calculate_safety_score(self, safety_checks: Dict[str, Any]) -> int:
        """Calculate safety score using advanced scoring system."""
        if "error" in safety_checks:
            return 0
        
        try:
            # Prepare data for advanced scoring
            static_analysis = {
                "is_verified": safety_checks.get("contract_verified", False),
                "dangerous_functions_found": [],
                "owner": {
                    "renounced": safety_checks.get("ownership_renounced", False),
                    "address": "unknown"
                },
                "has_mint": safety_checks.get("mint_function", False),
                "has_pause": safety_checks.get("pause_function", False),
                "has_blacklist": safety_checks.get("blacklist_function", False)
            }
            
            dynamic_analysis = {
                "honeypot_analysis": {
                    "is_honeypot": safety_checks.get("is_honeypot", False),
                    "confidence": safety_checks.get("honeypot_confidence", 0),
                    "can_buy": safety_checks.get("can_buy", True),
                    "can_sell": safety_checks.get("can_sell", True),
                    "indicators": safety_checks.get("honeypot_indicators", []),
                    "recommendation": safety_checks.get("honeypot_recommendation", "")
                },
                "fee_analysis": {
                    "buy_tax": safety_checks.get("buy_tax", 0),
                    "sell_tax": safety_checks.get("sell_tax", 0)
                },
                "analysis_method": safety_checks.get("analysis_method", "standard")
            }
            
            onchain_analysis = {
                "lp_info": {
                    "locked": False,  # Default conservative
                    "percent_locked": 0
                },
                "holders": {
                    "top_holder_percent": 0
                }
            }
            
            # Use advanced scoring
            breakdown = advanced_scorer.calculate_comprehensive_score(
                static_analysis, dynamic_analysis, onchain_analysis
            )
            
            return int(breakdown.final_score)
            
        except Exception as e:
            logger.warning("Advanced scoring failed, using fallback", {"error": str(e)})
            
            # Fallback to simple scoring
            score = 100
            
            # Major penalties
            if safety_checks.get("is_honeypot", False):
                confidence = safety_checks.get("honeypot_confidence", 0)
                if confidence >= 80:
                    score -= 90
                elif confidence >= 60:
                    score -= 70
                else:
                    score -= 50
            
            if not safety_checks.get("can_sell", True):
                score -= 80
            
            if not safety_checks.get("can_buy", True):
                score -= 60
            
            # Medium penalties
            if safety_checks.get("high_fees", False):
                score -= 20
            
            if safety_checks.get("has_dangerous_functions", False):
                score -= 15
            
            if not safety_checks.get("contract_verified", False):
                score -= 10
            
            # Minor penalties
            if not safety_checks.get("ownership_renounced", False):
                score -= 5
            
            if safety_checks.get("mint_function", False):
                score -= 5
            
            if safety_checks.get("pause_function", False):
                score -= 5
            
            if safety_checks.get("blacklist_function", False):
                score -= 5
            
            return max(0, min(100, score))
    
    def _calculate_quick_score(self, quick_checks: Dict[str, Any]) -> int:
        """Calculate quick safety score."""
        if "error" in quick_checks:
            return 0
        
        score = 100
        
        if quick_checks.get("is_honeypot", False):
            confidence = quick_checks.get("honeypot_confidence", 0)
            if confidence >= 80:
                score -= 90
            elif confidence >= 60:
                score -= 70
            else:
                score -= 50
        
        if not quick_checks.get("can_sell", True):
            score -= 80
        
        if not quick_checks.get("can_buy", True):
            score -= 60
        
        if quick_checks.get("high_fees", False):
            score -= 20
        
        if not quick_checks.get("contract_verified", False):
            score -= 10
        
        return max(0, min(100, score))
    
    def _get_risk_level(self, score: int) -> str:
        """Get risk level based on safety score."""
        if score >= 80:
            return "LOW"
        elif score >= 60:
            return "MEDIUM"
        elif score >= 30:
            return "HIGH"
        else:
            return "CRITICAL"
    
    def _get_recommendation(self, score: int, risk_level: str, safety_checks: Dict[str, Any]) -> str:
        """Get user-friendly recommendation."""
        if safety_checks.get("is_honeypot", False):
            return safety_checks.get("honeypot_recommendation", "🚨 AVOID - Honeypot detected")
        
        if risk_level == "CRITICAL":
            return "🚨 AVOID - Critical security risks detected"
        elif risk_level == "HIGH":
            return "⚠️ HIGH RISK - Exercise extreme caution"
        elif risk_level == "MEDIUM":
            return "⚡ MODERATE RISK - Standard risks apply"
        else:
            return "✅ RELATIVELY SAFE - Standard risks apply"
    
    def _get_quick_recommendation(self, score: int, risk_level: str) -> str:
        """Get quick recommendation."""
        if risk_level == "CRITICAL":
            return "🚨 AVOID - High risk detected"
        elif risk_level == "HIGH":
            return "⚠️ HIGH RISK - Be very careful"
        elif risk_level == "MEDIUM":
            return "⚡ MODERATE RISK - Exercise caution"
        else:
            return "✅ LOOKS SAFE - Standard risks apply"
    
    def _build_analysis_response(self, token_address: str, metadata: Dict[str, Any], 
                               safety_checks: Dict[str, Any], safety_score: int, 
                               risk_level: str, recommendation: str, start_time: float) -> Dict[str, Any]:
        """Build comprehensive analysis response."""
        return {
            "status": "success",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "analysis_type": "simple_analysis",
            "token_address": token_address,
            
            # Core results
            "safety_score": safety_score,
            "risk_level": risk_level,
            "recommendation": recommendation,
            
            # Token information
            "token_info": {
                "name": metadata.get("TokenName", "Unknown"),
                "symbol": metadata.get("TokenSymbol", "Unknown"),
                "decimals": int(metadata.get("Decimals", 18)),
                "total_supply": metadata.get("TotalSupply", "0"),
                "verified": metadata.get("is_verified", False)
            },
            
            # Quick checks
            "quick_checks": {
                "honeypot": safety_checks.get("is_honeypot", False),
                "can_buy": safety_checks.get("can_buy", True),
                "can_sell": safety_checks.get("can_sell", True),
                "high_fees": safety_checks.get("high_fees", False),
                "contract_verified": safety_checks.get("contract_verified", False),
                "ownership_renounced": safety_checks.get("ownership_renounced", False)
            },
            
            # Fee information
            "fees": {
                "buy_tax": safety_checks.get("buy_tax", 0),
                "sell_tax": safety_checks.get("sell_tax", 0)
            },
            
            # Critical risks
            "critical_risks": self._extract_critical_risks(safety_checks),
            
            # Warnings
            "warnings": self._extract_warnings(safety_checks),
            
            # Analysis metadata
            "analysis_duration_ms": round((time.time() - start_time) * 1000, 2),
            "analysis_method": safety_checks.get("analysis_method", "standard")
        }
    
    def _extract_critical_risks(self, safety_checks: Dict[str, Any]) -> List[str]:
        """Extract critical risk indicators."""
        risks = []
        
        if safety_checks.get("is_honeypot", False):
            risks.append("🚨 Honeypot detected - Cannot sell tokens")
        
        if not safety_checks.get("can_sell", True):
            risks.append("🚨 Selling blocked")
        
        if not safety_checks.get("can_buy", True):
            risks.append("🚨 Buying blocked")
        
        return risks
    
    def _extract_warnings(self, safety_checks: Dict[str, Any]) -> List[str]:
        """Extract warning indicators."""
        warnings = []
        
        if safety_checks.get("high_fees", False):
            buy_tax = safety_checks.get("buy_tax", 0)
            sell_tax = safety_checks.get("sell_tax", 0)
            warnings.append(f"⚠️ High fees: Buy {buy_tax}%, Sell {sell_tax}%")
        
        if not safety_checks.get("contract_verified", False):
            warnings.append("🔍 Contract not verified")
        
        if not safety_checks.get("ownership_renounced", False):
            warnings.append("🔓 Ownership not renounced")
        
        if safety_checks.get("mint_function", False):
            warnings.append("🪙 Has mint function")
        
        if safety_checks.get("pause_function", False):
            warnings.append("⏸️ Has pause function")
        
        if safety_checks.get("blacklist_function", False):
            warnings.append("🚫 Has blacklist function")
        
        return warnings
    
    def _create_error_response(self, token_address: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Create error response for failed analysis."""
        error_msg = metadata.get("error", "Analysis failed")
        
        return {
            "status": "error",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "analysis_type": "simple_analysis",
            "token_address": token_address,
            "error": error_msg,
            "safety_score": 0,
            "risk_level": "CRITICAL",
            "recommendation": "🚨 AVOID - Analysis failed, cannot verify safety"
        }
    
    def _create_quick_error_response(self, token_address: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Create error response for failed quick check."""
        error_msg = metadata.get("error", "Quick check failed")
        
        return {
            "status": "error",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "analysis_type": "quick_check",
            "token_address": token_address,
            "error": error_msg,
            "safety_score": 0,
            "risk_level": "CRITICAL",
            "recommendation": "🚨 AVOID - Cannot verify safety"
        }

# Global instance
token_analysis_service = TokenAnalysisService() 