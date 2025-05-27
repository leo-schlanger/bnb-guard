"""
Advanced Token Risk Scoring System

This module provides a sophisticated, multi-dimensional risk scoring system
that evaluates tokens across multiple security vectors with weighted analysis.
"""

import time
import math
from typing import Dict, Any, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum
from app.core.utils.logger import get_logger

logger = get_logger(__name__)

class RiskCategory(Enum):
    """Risk categories for scoring."""
    SECURITY = "security"
    LIQUIDITY = "liquidity"
    OWNERSHIP = "ownership"
    TRADING = "trading"
    TECHNICAL = "technical"
    MARKET = "market"

class SeverityLevel(Enum):
    """Severity levels with numeric weights."""
    CRITICAL = 1.0
    HIGH = 0.7
    MEDIUM = 0.4
    LOW = 0.2
    INFO = 0.1

@dataclass
class RiskFactor:
    """Individual risk factor with detailed information."""
    category: RiskCategory
    severity: SeverityLevel
    weight: float
    score_impact: float
    title: str
    description: str
    recommendation: str
    confidence: float = 1.0
    evidence: Dict[str, Any] = None

@dataclass
class ScoreBreakdown:
    """Detailed score breakdown."""
    base_score: float
    category_scores: Dict[str, float]
    risk_factors: List[RiskFactor]
    final_score: float
    confidence_level: float
    grade: str
    risk_level: str

class AdvancedTokenScorer:
    """Advanced token risk scoring system."""
    
    def __init__(self):
        # Category weights (must sum to 1.0)
        self.category_weights = {
            RiskCategory.SECURITY: 0.35,      # Most important
            RiskCategory.LIQUIDITY: 0.20,     # Very important
            RiskCategory.OWNERSHIP: 0.15,     # Important
            RiskCategory.TRADING: 0.15,       # Important
            RiskCategory.TECHNICAL: 0.10,     # Moderately important
            RiskCategory.MARKET: 0.05         # Least important
        }
        
        # Base score starts at maximum
        self.base_score = 100.0
        
        # Confidence thresholds
        self.confidence_thresholds = {
            "high": 0.8,
            "medium": 0.6,
            "low": 0.4
        }
    
    def calculate_comprehensive_score(self, 
                                    static_analysis: Dict[str, Any],
                                    dynamic_analysis: Dict[str, Any], 
                                    onchain_analysis: Dict[str, Any]) -> ScoreBreakdown:
        """
        Calculate comprehensive risk score using multi-dimensional analysis.
        
        Args:
            static_analysis: Static code analysis results
            dynamic_analysis: Dynamic trading analysis results
            onchain_analysis: On-chain data analysis results
            
        Returns:
            Detailed score breakdown with risk factors
        """
        start_time = time.time()
        
        logger.info("Starting advanced risk scoring", {
            "has_static": bool(static_analysis),
            "has_dynamic": bool(dynamic_analysis),
            "has_onchain": bool(onchain_analysis)
        })
        
        try:
            # Extract risk factors from each analysis type
            risk_factors = []
            
            # Security analysis (from static + dynamic)
            security_factors = self._analyze_security_risks(static_analysis, dynamic_analysis)
            risk_factors.extend(security_factors)
            
            # Liquidity analysis (from onchain + dynamic)
            liquidity_factors = self._analyze_liquidity_risks(onchain_analysis, dynamic_analysis)
            risk_factors.extend(liquidity_factors)
            
            # Ownership analysis (from static + onchain)
            ownership_factors = self._analyze_ownership_risks(static_analysis, onchain_analysis)
            risk_factors.extend(ownership_factors)
            
            # Trading analysis (from dynamic)
            trading_factors = self._analyze_trading_risks(dynamic_analysis)
            risk_factors.extend(trading_factors)
            
            # Technical analysis (from static)
            technical_factors = self._analyze_technical_risks(static_analysis)
            risk_factors.extend(technical_factors)
            
            # Market analysis (from onchain)
            market_factors = self._analyze_market_risks(onchain_analysis)
            risk_factors.extend(market_factors)
            
            # Calculate category scores
            category_scores = self._calculate_category_scores(risk_factors)
            
            # Calculate final weighted score
            final_score = self._calculate_weighted_score(category_scores)
            
            # Calculate overall confidence
            confidence_level = self._calculate_confidence_level(risk_factors, static_analysis, dynamic_analysis)
            
            # Determine grade and risk level
            grade = self._get_grade(final_score)
            risk_level = self._get_risk_level(final_score)
            
            # Create breakdown
            breakdown = ScoreBreakdown(
                base_score=self.base_score,
                category_scores=category_scores,
                risk_factors=risk_factors,
                final_score=final_score,
                confidence_level=confidence_level,
                grade=grade,
                risk_level=risk_level
            )
            
            duration = time.time() - start_time
            logger.info("Advanced risk scoring completed", {
                "final_score": final_score,
                "grade": grade,
                "risk_level": risk_level,
                "confidence": confidence_level,
                "total_factors": len(risk_factors),
                "duration_ms": round(duration * 1000, 2)
            })
            
            return breakdown
            
        except Exception as e:
            logger.error("Advanced scoring failed", {
                "error": str(e),
                "error_type": type(e).__name__
            }, exc_info=True)
            
            # Return conservative score on error
            return self._create_error_breakdown(str(e))
    
    def _analyze_security_risks(self, static_analysis: Dict[str, Any], 
                               dynamic_analysis: Dict[str, Any]) -> List[RiskFactor]:
        """Analyze security-related risks."""
        factors = []
        
        # Honeypot detection (highest priority)
        honeypot_info = dynamic_analysis.get("honeypot_analysis", {})
        if honeypot_info.get("is_honeypot", False):
            confidence = honeypot_info.get("confidence", 0) / 100.0
            severity = SeverityLevel.CRITICAL if confidence >= 0.8 else SeverityLevel.HIGH
            
            factors.append(RiskFactor(
                category=RiskCategory.SECURITY,
                severity=severity,
                weight=1.0,  # Maximum weight for honeypot
                score_impact=80 * confidence,  # Up to 80 points impact
                title="Honeypot Detected",
                description=f"Token appears to be a honeypot (confidence: {confidence*100:.1f}%)",
                recommendation=honeypot_info.get("recommendation", "Avoid trading this token"),
                confidence=confidence,
                evidence={
                    "indicators": honeypot_info.get("indicators", []),
                    "can_buy": honeypot_info.get("can_buy", False),
                    "can_sell": honeypot_info.get("can_sell", False)
                }
            ))
        
        # Trading restrictions
        if not honeypot_info.get("can_sell", True):
            factors.append(RiskFactor(
                category=RiskCategory.SECURITY,
                severity=SeverityLevel.CRITICAL,
                weight=1.0,
                score_impact=70,
                title="Sell Restriction",
                description="Token selling appears to be blocked",
                recommendation="Cannot sell tokens - avoid this token",
                confidence=0.9,
                evidence={"can_sell": False}
            ))
        
        if not honeypot_info.get("can_buy", True):
            factors.append(RiskFactor(
                category=RiskCategory.SECURITY,
                severity=SeverityLevel.HIGH,
                weight=0.2,
                score_impact=20,
                title="Buy Restriction", 
                description="Token buying appears to be blocked",
                recommendation="Cannot buy tokens - check contract status",
                confidence=0.8,
                evidence={"can_buy": False}
            ))
        
        # Dangerous functions from static analysis
        dangerous_functions = static_analysis.get("dangerous_functions_found", [])
        if dangerous_functions:
            severity_map = {"critical": SeverityLevel.CRITICAL, "high": SeverityLevel.HIGH, 
                          "medium": SeverityLevel.MEDIUM, "low": SeverityLevel.LOW}
            
            for func in dangerous_functions[:3]:  # Top 3 most dangerous
                func_severity = severity_map.get(func.get("severity", "medium"), SeverityLevel.MEDIUM)
                
                factors.append(RiskFactor(
                    category=RiskCategory.SECURITY,
                    severity=func_severity,
                    weight=0.1,
                    score_impact=15 * func_severity.value,
                    title=f"Dangerous Function: {func.get('name', 'Unknown')}",
                    description=func.get("message", "Potentially dangerous function detected"),
                    recommendation="Review function implementation carefully",
                    confidence=0.7,
                    evidence={"function": func}
                ))
        
        return factors
    
    def _analyze_liquidity_risks(self, onchain_analysis: Dict[str, Any], 
                                dynamic_analysis: Dict[str, Any]) -> List[RiskFactor]:
        """Analyze liquidity-related risks."""
        factors = []
        
        # LP lock status
        lp_info = onchain_analysis.get("lp_info", {})
        is_locked = lp_info.get("locked", False)
        locked_percent = lp_info.get("percent_locked", 0)
        
        if not is_locked:
            factors.append(RiskFactor(
                category=RiskCategory.LIQUIDITY,
                severity=SeverityLevel.HIGH,
                weight=0.6,
                score_impact=25,
                title="Liquidity Not Locked",
                description="Liquidity pool is not locked - rug pull risk",
                recommendation="High rug pull risk - exercise extreme caution",
                confidence=0.9,
                evidence={"locked": False, "locked_percent": 0}
            ))
        elif locked_percent < 80:
            factors.append(RiskFactor(
                category=RiskCategory.LIQUIDITY,
                severity=SeverityLevel.MEDIUM,
                weight=0.4,
                score_impact=15,
                title="Partial Liquidity Lock",
                description=f"Only {locked_percent}% of liquidity is locked",
                recommendation="Partial rug pull risk - be cautious",
                confidence=0.8,
                evidence={"locked": True, "locked_percent": locked_percent}
            ))
        
        # Liquidity analysis from dynamic
        liquidity_analysis = dynamic_analysis.get("liquidity_analysis", {})
        if not liquidity_analysis.get("has_liquidity", True):
            factors.append(RiskFactor(
                category=RiskCategory.LIQUIDITY,
                severity=SeverityLevel.HIGH,
                weight=0.4,
                score_impact=20,
                title="No Liquidity Pool",
                description="No liquidity pool found for trading",
                recommendation="Cannot trade - no liquidity available",
                confidence=0.9,
                evidence=liquidity_analysis
            ))
        
        return factors
    
    def _analyze_ownership_risks(self, static_analysis: Dict[str, Any], 
                                onchain_analysis: Dict[str, Any]) -> List[RiskFactor]:
        """Analyze ownership-related risks."""
        factors = []
        
        # Ownership renouncement
        owner_info = static_analysis.get("owner", {})
        if not owner_info.get("renounced", False):
            factors.append(RiskFactor(
                category=RiskCategory.OWNERSHIP,
                severity=SeverityLevel.MEDIUM,
                weight=0.5,
                score_impact=12,
                title="Ownership Not Renounced",
                description="Contract owner can still modify contract",
                recommendation="Owner has control - verify owner trustworthiness",
                confidence=0.8,
                evidence={"owner_address": owner_info.get("address", "unknown")}
            ))
        
        # Mint function
        if static_analysis.get("has_mint", False):
            factors.append(RiskFactor(
                category=RiskCategory.OWNERSHIP,
                severity=SeverityLevel.MEDIUM,
                weight=0.3,
                score_impact=10,
                title="Mint Function Present",
                description="Contract can create new tokens",
                recommendation="Inflation risk - check mint controls",
                confidence=0.7,
                evidence={"has_mint": True}
            ))
        
        # Pause function
        if static_analysis.get("has_pause", False):
            factors.append(RiskFactor(
                category=RiskCategory.OWNERSHIP,
                severity=SeverityLevel.MEDIUM,
                weight=0.2,
                score_impact=8,
                title="Pause Function Present",
                description="Contract can be paused by owner",
                recommendation="Trading can be halted - check pause controls",
                confidence=0.7,
                evidence={"has_pause": True}
            ))
        
        return factors
    
    def _analyze_trading_risks(self, dynamic_analysis: Dict[str, Any]) -> List[RiskFactor]:
        """Analyze trading-related risks."""
        factors = []
        
        # Fee analysis
        fee_analysis = dynamic_analysis.get("fee_analysis", {})
        buy_tax = fee_analysis.get("buy_tax", 0)
        sell_tax = fee_analysis.get("sell_tax", 0)
        
        # High fees
        if buy_tax > 20 or sell_tax > 20:
            max_tax = max(buy_tax, sell_tax)
            factors.append(RiskFactor(
                category=RiskCategory.TRADING,
                severity=SeverityLevel.HIGH,
                weight=0.4,
                score_impact=20,
                title="Extremely High Fees",
                description=f"Very high trading fees: Buy {buy_tax}%, Sell {sell_tax}%",
                recommendation="Extremely high fees - avoid trading",
                confidence=0.9,
                evidence={"buy_tax": buy_tax, "sell_tax": sell_tax}
            ))
        elif buy_tax > 10 or sell_tax > 10:
            factors.append(RiskFactor(
                category=RiskCategory.TRADING,
                severity=SeverityLevel.MEDIUM,
                weight=0.3,
                score_impact=12,
                title="High Trading Fees",
                description=f"High trading fees: Buy {buy_tax}%, Sell {sell_tax}%",
                recommendation="High fees reduce profitability",
                confidence=0.8,
                evidence={"buy_tax": buy_tax, "sell_tax": sell_tax}
            ))
        
        # Fee discrepancy
        fee_diff = abs(buy_tax - sell_tax)
        if fee_diff > 15:
            factors.append(RiskFactor(
                category=RiskCategory.TRADING,
                severity=SeverityLevel.MEDIUM,
                weight=0.3,
                score_impact=10,
                title="Large Fee Discrepancy",
                description=f"Large difference between buy ({buy_tax}%) and sell ({sell_tax}%) fees",
                recommendation="Unusual fee structure - investigate further",
                confidence=0.7,
                evidence={"buy_tax": buy_tax, "sell_tax": sell_tax, "difference": fee_diff}
            ))
        
        return factors
    
    def _analyze_technical_risks(self, static_analysis: Dict[str, Any]) -> List[RiskFactor]:
        """Analyze technical implementation risks."""
        factors = []
        
        # Contract verification
        if not static_analysis.get("is_verified", False):
            factors.append(RiskFactor(
                category=RiskCategory.TECHNICAL,
                severity=SeverityLevel.MEDIUM,
                weight=0.4,
                score_impact=8,
                title="Contract Not Verified",
                description="Source code is not verified on blockchain explorer",
                recommendation="Cannot audit code - higher risk",
                confidence=0.9,
                evidence={"verified": False}
            ))
        
        # Blacklist function
        if static_analysis.get("has_blacklist", False):
            factors.append(RiskFactor(
                category=RiskCategory.TECHNICAL,
                severity=SeverityLevel.MEDIUM,
                weight=0.3,
                score_impact=6,
                title="Blacklist Function",
                description="Contract can blacklist addresses",
                recommendation="Addresses can be blocked from trading",
                confidence=0.7,
                evidence={"has_blacklist": True}
            ))
        
        # Proxy contract
        if static_analysis.get("is_proxy", False):
            factors.append(RiskFactor(
                category=RiskCategory.TECHNICAL,
                severity=SeverityLevel.LOW,
                weight=0.3,
                score_impact=4,
                title="Proxy Contract",
                description="Contract uses proxy pattern",
                recommendation="Implementation can be changed - verify upgrade controls",
                confidence=0.6,
                evidence={"is_proxy": True}
            ))
        
        return factors
    
    def _analyze_market_risks(self, onchain_analysis: Dict[str, Any]) -> List[RiskFactor]:
        """Analyze market-related risks."""
        factors = []
        
        # Holder concentration
        holders = onchain_analysis.get("holders", {})
        top_holder_percent = holders.get("top_holder_percent", 0)
        
        if top_holder_percent > 50:
            factors.append(RiskFactor(
                category=RiskCategory.MARKET,
                severity=SeverityLevel.HIGH,
                weight=0.6,
                score_impact=15,
                title="High Holder Concentration",
                description=f"Top holder owns {top_holder_percent}% of supply",
                recommendation="Whale risk - large holder can manipulate price",
                confidence=0.8,
                evidence={"top_holder_percent": top_holder_percent}
            ))
        elif top_holder_percent > 20:
            factors.append(RiskFactor(
                category=RiskCategory.MARKET,
                severity=SeverityLevel.MEDIUM,
                weight=0.4,
                score_impact=8,
                title="Moderate Holder Concentration",
                description=f"Top holder owns {top_holder_percent}% of supply",
                recommendation="Some concentration risk",
                confidence=0.7,
                evidence={"top_holder_percent": top_holder_percent}
            ))
        
        return factors
    
    def _calculate_category_scores(self, risk_factors: List[RiskFactor]) -> Dict[str, float]:
        """Calculate scores for each risk category with improved algorithm."""
        category_scores = {}
        
        for category in RiskCategory:
            category_factors = [f for f in risk_factors if f.category == category]
            
            if not category_factors:
                category_scores[category.value] = 100.0
                continue
            
            # Use multiplicative penalty system for more realistic scoring
            category_score = 100.0
            
            for factor in category_factors:
                # Calculate penalty based on severity, confidence, and weight
                penalty_multiplier = factor.severity.value * factor.confidence * factor.weight
                penalty = factor.score_impact * penalty_multiplier
                
                # Apply penalty with diminishing returns
                penalty_factor = penalty / 100.0
                category_score *= (1.0 - penalty_factor)
            
            # Ensure score doesn't go below 0
            category_score = max(0.0, category_score)
            category_scores[category.value] = round(category_score, 1)
        
        return category_scores
    
    def _calculate_weighted_score(self, category_scores: Dict[str, float]) -> float:
        """Calculate final weighted score across all categories."""
        weighted_sum = 0.0
        
        for category, weight in self.category_weights.items():
            category_score = category_scores.get(category.value, 100.0)
            weighted_sum += category_score * weight
        
        return round(weighted_sum, 1)
    
    def _calculate_confidence_level(self, risk_factors: List[RiskFactor], 
                                   static_analysis: Dict[str, Any],
                                   dynamic_analysis: Dict[str, Any]) -> float:
        """Calculate overall confidence in the analysis."""
        confidence_factors = []
        
        # Base confidence from data availability
        if static_analysis.get("is_verified", False):
            confidence_factors.append(0.9)  # High confidence with verified code
        else:
            confidence_factors.append(0.6)  # Medium confidence without code
        
        # Confidence from dynamic analysis
        if dynamic_analysis.get("analysis_method") == "advanced_honeypot_detection":
            confidence_factors.append(0.9)  # High confidence with advanced analysis
        else:
            confidence_factors.append(0.7)  # Medium confidence with basic analysis
        
        # Confidence from risk factors
        if risk_factors:
            factor_confidences = [f.confidence for f in risk_factors]
            avg_factor_confidence = sum(factor_confidences) / len(factor_confidences)
            confidence_factors.append(avg_factor_confidence)
        
        # Calculate weighted average
        overall_confidence = sum(confidence_factors) / len(confidence_factors)
        return round(overall_confidence, 2)
    
    def _get_grade(self, score: float) -> str:
        """Get letter grade based on score."""
        if score >= 95:
            return "A+"
        elif score >= 90:
            return "A"
        elif score >= 85:
            return "A-"
        elif score >= 80:
            return "B+"
        elif score >= 75:
            return "B"
        elif score >= 70:
            return "B-"
        elif score >= 65:
            return "C+"
        elif score >= 60:
            return "C"
        elif score >= 55:
            return "C-"
        elif score >= 50:
            return "D+"
        elif score >= 45:
            return "D"
        elif score >= 40:
            return "D-"
        else:
            return "F"
    
    def _get_risk_level(self, score: float) -> str:
        """Get risk level based on score."""
        if score >= 85:
            return "VERY_LOW"
        elif score >= 75:
            return "LOW"
        elif score >= 65:
            return "MODERATE"
        elif score >= 50:
            return "HIGH"
        elif score >= 30:
            return "VERY_HIGH"
        else:
            return "CRITICAL"
    
    def _create_error_breakdown(self, error: str) -> ScoreBreakdown:
        """Create conservative breakdown when scoring fails."""
        return ScoreBreakdown(
            base_score=100.0,
            category_scores={cat.value: 0.0 for cat in RiskCategory},
            risk_factors=[RiskFactor(
                category=RiskCategory.TECHNICAL,
                severity=SeverityLevel.CRITICAL,
                weight=1.0,
                score_impact=100.0,
                title="Analysis Failed",
                description=f"Risk analysis failed: {error}",
                recommendation="Cannot assess risk - avoid trading",
                confidence=0.0,
                evidence={"error": error}
            )],
            final_score=0.0,
            confidence_level=0.0,
            grade="F",
            risk_level="CRITICAL"
        )

# Global instance
advanced_scorer = AdvancedTokenScorer() 