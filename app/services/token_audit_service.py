"""Token Audit Service - Detailed Analysis for Developers

This service provides comprehensive token auditing with detailed technical information
for developers, security researchers, and advanced users.
"""

from typing import Dict, Any, List
from datetime import datetime, timezone
import time

from app.core.utils.logger import get_logger
from app.core.utils.metadata import fetch_token_metadata
from app.core.analyzers.static_analyzer import analyze_static
from app.core.analyzers.dynamic_analyzer import analyze_dynamic
from app.core.analyzers.onchain_analyzer import analyze_onchain
from app.core.utils.scoring import calculate_risk_score
from app.core.utils.advanced_scoring import advanced_scorer

logger = get_logger(__name__)

class TokenAuditService:
    """Service for comprehensive token auditing with detailed technical analysis."""
    
    def __init__(self):
        self.audit_timeout = 60  # Longer timeout for comprehensive audit
        
    async def audit_token(self, token_address: str) -> Dict[str, Any]:
        """
        Performs comprehensive token audit for developers and security researchers.
        
        Returns detailed technical analysis including:
        - Complete contract analysis
        - Security vulnerabilities
        - Code quality assessment
        - Detailed recommendations
        - Improvement suggestions
        
        Args:
            token_address: Token address to audit
            
        Returns:
            Comprehensive audit results with technical details
        """
        start_time = time.time()
        
        logger.info("Starting comprehensive token audit", {
            "token_address": token_address,
            "service": "token_audit"
        })
        
        try:
            # Validate address
            normalized_address = self._validate_address(token_address)
            
            # Fetch comprehensive metadata
            metadata = await self._fetch_comprehensive_metadata(normalized_address)
            if self._is_error_metadata(metadata):
                return self._create_error_response(normalized_address, metadata)
            
            # Perform comprehensive analysis
            static_analysis = await self._perform_static_analysis(metadata)
            dynamic_analysis = await self._perform_dynamic_analysis(normalized_address, metadata)
            onchain_analysis = await self._perform_onchain_analysis(metadata)
            security_assessment = await self._assess_security(static_analysis, dynamic_analysis, onchain_analysis)
            
            # Generate improvement recommendations
            recommendations = self._generate_recommendations(static_analysis, dynamic_analysis, onchain_analysis)
            
            # Build comprehensive response
            response = self._build_audit_response(
                normalized_address, metadata, static_analysis, dynamic_analysis, 
                onchain_analysis, security_assessment, recommendations, start_time
            )
            
            duration = time.time() - start_time
            logger.success("Token audit completed", {
                "token_address": normalized_address,
                "security_score": response["security_assessment"]["overall_score"],
                "vulnerabilities_found": len(response["vulnerabilities"]),
                "duration_ms": round(duration * 1000, 2)
            })
            
            return response
            
        except Exception as e:
            logger.failure("Token audit failed", {
                "token_address": token_address,
                "error": str(e),
                "error_type": type(e).__name__
            }, exc_info=True)
            return self._create_error_response(token_address, {"error": str(e)})
    
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
    
    async def _fetch_comprehensive_metadata(self, token_address: str) -> Dict[str, Any]:
        """Fetch comprehensive token metadata including source code."""
        try:
            metadata = fetch_token_metadata(token_address)
            
            # Add additional metadata for audit
            metadata["audit_timestamp"] = datetime.now(timezone.utc).isoformat()
            metadata["audit_version"] = "1.0.0"
            
            return metadata
        except Exception as e:
            logger.error("Failed to fetch comprehensive metadata", {
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
    
    async def _perform_static_analysis(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Perform comprehensive static code analysis."""
        logger.debug("Performing comprehensive static analysis")
        
        try:
            source_code = metadata.get("SourceCode", "")
            if not source_code:
                return {
                    "status": "no_source",
                    "message": "Source code not available for analysis",
                    "verified": False,
                    "functions": [],
                    "vulnerabilities": [],
                    "code_quality": {"score": 0, "issues": ["Source code not verified"]}
                }
            
            # Perform detailed static analysis
            static_results = analyze_static(source_code)
            
            # Add code quality assessment
            code_quality = self._assess_code_quality(source_code, static_results)
            static_results["code_quality"] = code_quality
            
            # Add vulnerability classification
            vulnerabilities = self._classify_vulnerabilities(static_results)
            static_results["vulnerabilities"] = vulnerabilities
            
            return static_results
            
        except Exception as e:
            logger.warning("Static analysis failed", {"error": str(e)})
            return {
                "status": "error",
                "error": str(e),
                "functions": [],
                "vulnerabilities": [],
                "code_quality": {"score": 0, "issues": [f"Analysis failed: {str(e)}"]}
            }
    
    async def _perform_dynamic_analysis(self, token_address: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Perform comprehensive dynamic analysis using advanced honeypot detection."""
        logger.debug("Performing comprehensive dynamic analysis")
        
        try:
            # Import here to avoid circular imports
            from app.core.analyzers.dynamic_analyzer import analyze_dynamic_advanced, analyze_dynamic_fallback
            
            # Use advanced honeypot detection
            try:
                dynamic_results = await analyze_dynamic_advanced(token_address, metadata)
            except Exception as e:
                logger.warning("Advanced analysis failed, using fallback", {"error": str(e)})
                dynamic_results = await analyze_dynamic_fallback(token_address, str(e))
            
            # Add comprehensive analysis details
            honeypot_info = dynamic_results.get("honeypot", {})
            simulation_details = dynamic_results.get("simulation_details", {})
            
            # Enhanced result with audit-specific information
            enhanced_result = {
                "honeypot_analysis": {
                    "is_honeypot": honeypot_info.get("is_honeypot", False),
                    "confidence": honeypot_info.get("confidence", 0),
                    "risk_level": honeypot_info.get("risk_level", "UNKNOWN"),
                    "can_buy": honeypot_info.get("can_buy", False),
                    "can_sell": honeypot_info.get("can_sell", False),
                    "indicators": honeypot_info.get("indicators", []),
                    "recommendation": honeypot_info.get("recommendation", "")
                },
                "fee_analysis": {
                    "buy_tax": dynamic_results.get("fees", {}).get("buy", 0),
                    "sell_tax": dynamic_results.get("fees", {}).get("sell", 0),
                    "buy_slippage": dynamic_results.get("fees", {}).get("buy_slippage", 0),
                    "sell_slippage": dynamic_results.get("fees", {}).get("sell_slippage", 0),
                    "fee_mutable": dynamic_results.get("fees", {}).get("buy_mutable", False) or 
                                  dynamic_results.get("fees", {}).get("sell_mutable", False)
                },
                "trading_simulation": {
                    "buy_tests": simulation_details.get("buy_tests", []),
                    "sell_tests": simulation_details.get("sell_tests", []),
                    "total_tests": len(simulation_details.get("buy_tests", [])) + len(simulation_details.get("sell_tests", [])),
                    "success_rate": self._calculate_success_rate(simulation_details)
                },
                "pattern_analysis": simulation_details.get("pattern_analysis", {}),
                "liquidity_analysis": simulation_details.get("liquidity_analysis", {}),
                "alerts": dynamic_results.get("alerts", []),
                "analysis_method": dynamic_results.get("analysis_method", "advanced")
            }
            
            return enhanced_result
            
        except Exception as e:
            logger.warning("Dynamic analysis failed", {"error": str(e)})
            return {
                "honeypot_analysis": {
                    "is_honeypot": True,  # Assume worst case
                    "confidence": 0,
                    "risk_level": "UNKNOWN",
                    "can_buy": False,
                    "can_sell": False,
                    "indicators": ["Analysis failed"],
                    "recommendation": "⚠️ UNKNOWN RISK - Analysis failed"
                },
                "fee_analysis": {
                    "buy_tax": 100.0,
                    "sell_tax": 100.0,
                    "buy_slippage": 0.0,
                    "sell_slippage": 0.0,
                    "fee_mutable": False
                },
                "trading_simulation": {
                    "buy_tests": [],
                    "sell_tests": [],
                    "total_tests": 0,
                    "success_rate": 0.0
                },
                "pattern_analysis": {},
                "liquidity_analysis": {},
                "alerts": [{"title": "Analysis Failed", "description": str(e), "severity": "critical"}],
                "analysis_method": "fallback",
                "error": str(e)
            }
    
    async def _perform_onchain_analysis(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Perform comprehensive on-chain analysis."""
        logger.debug("Performing comprehensive on-chain analysis")
        
        try:
            # Add LP info for on-chain analysis
            metadata["lp_info"] = {
                "locked": False,
                "percent_locked": None,
                "lock_duration": None,
                "unlock_date": None
            }
            
            onchain_results = analyze_onchain(metadata)
            
            # Add holder analysis
            holder_analysis = self._analyze_holders(metadata)
            onchain_results["holder_analysis"] = holder_analysis
            
            # Add liquidity analysis
            liquidity_analysis = self._analyze_liquidity(metadata)
            onchain_results["liquidity_analysis"] = liquidity_analysis
            
            return onchain_results
            
        except Exception as e:
            logger.warning("On-chain analysis failed", {"error": str(e)})
            return {
                "status": "error",
                "error": str(e),
                "holders": {"distribution": "unknown"},
                "liquidity": {"locked": False},
                "holder_analysis": {"issues": [f"Analysis failed: {str(e)}"]},
                "liquidity_analysis": {"issues": [f"Analysis failed: {str(e)}"]}
            }
    
    async def _assess_security(self, static_analysis: Dict[str, Any], 
                             dynamic_analysis: Dict[str, Any], 
                             onchain_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Perform comprehensive security assessment using advanced scoring."""
        try:
            # Use advanced scoring system
            breakdown = advanced_scorer.calculate_comprehensive_score(
                static_analysis, dynamic_analysis, onchain_analysis
            )
            
            # Extract detailed information from breakdown
            security_score = int(breakdown.final_score)
            risk_factors = breakdown.risk_factors
            
            # Organize issues by severity
            critical_issues = []
            high_issues = []
            medium_issues = []
            low_issues = []
            
            for factor in risk_factors:
                issue = {
                    "type": factor.title.lower().replace(" ", "_"),
                    "title": factor.title,
                    "description": factor.description,
                    "severity": factor.severity.name.lower(),
                    "category": factor.category.value,
                    "impact": f"Score impact: -{factor.score_impact:.1f}",
                    "recommendation": factor.recommendation,
                    "confidence": f"{factor.confidence*100:.1f}%",
                    "evidence": factor.evidence or {}
                }
                
                if factor.severity.name == "CRITICAL":
                    critical_issues.append(issue)
                elif factor.severity.name == "HIGH":
                    high_issues.append(issue)
                elif factor.severity.name == "MEDIUM":
                    medium_issues.append(issue)
                else:
                    low_issues.append(issue)
            
            total_issues = len(critical_issues) + len(high_issues) + len(medium_issues) + len(low_issues)
            
            return {
                "overall_score": security_score,
                "risk_score": security_score,  # For backward compatibility
                "critical_issues": critical_issues,
                "high_issues": high_issues,
                "medium_issues": medium_issues,
                "low_issues": low_issues,
                "total_issues": total_issues,
                "security_grade": breakdown.grade,
                "risk_level": breakdown.risk_level,
                "confidence_level": breakdown.confidence_level,
                "category_scores": breakdown.category_scores,
                "advanced_analysis": True
            }
            
        except Exception as e:
            logger.warning("Advanced security assessment failed, using fallback", {"error": str(e)})
            
            # Fallback to legacy scoring
            risk_score = calculate_risk_score(static_analysis, dynamic_analysis, onchain_analysis)
        
        # Classify security issues by severity
        critical_issues = []
        high_issues = []
        medium_issues = []
        low_issues = []
        
        # Analyze static analysis results
        if static_analysis.get("vulnerabilities"):
            for vuln in static_analysis["vulnerabilities"]:
                severity = vuln.get("severity", "medium")
                if severity == "critical":
                    critical_issues.append(vuln)
                elif severity == "high":
                    high_issues.append(vuln)
                elif severity == "medium":
                    medium_issues.append(vuln)
                else:
                    low_issues.append(vuln)
        
        # Analyze dynamic analysis results
        honeypot_analysis = dynamic_analysis.get("honeypot_analysis", {})
        if honeypot_analysis.get("is_honeypot"):
            confidence = honeypot_analysis.get("confidence", 0)
            severity = "critical" if confidence >= 80 else "high" if confidence >= 60 else "medium"
            
            critical_issues.append({
                "type": "honeypot",
                "description": f"Token appears to be a honeypot (confidence: {confidence}%)",
                "severity": severity,
                "impact": "Users cannot sell tokens",
                "indicators": honeypot_analysis.get("indicators", []),
                "recommendation": honeypot_analysis.get("recommendation", "")
            })
        
        # Check for trading restrictions
        if not honeypot_analysis.get("can_sell", True):
            critical_issues.append({
                "type": "sell_restriction",
                "description": "Token selling appears to be blocked",
                "severity": "critical",
                "impact": "Users cannot sell their tokens"
            })
        
        if not honeypot_analysis.get("can_buy", True):
            high_issues.append({
                "type": "buy_restriction", 
                "description": "Token buying appears to be blocked",
                "severity": "high",
                "impact": "Users cannot purchase tokens"
            })
        
        # Check for high fees
        fee_analysis = dynamic_analysis.get("fee_analysis", {})
        buy_tax = fee_analysis.get("buy_tax", 0)
        sell_tax = fee_analysis.get("sell_tax", 0)
        
        if buy_tax > 20 or sell_tax > 20:
            critical_issues.append({
                "type": "excessive_fees",
                "description": f"Extremely high trading fees: Buy {buy_tax}%, Sell {sell_tax}%",
                "severity": "critical",
                "impact": "Users lose significant value in fees"
            })
        elif buy_tax > 10 or sell_tax > 10:
            high_issues.append({
                "type": "high_fees",
                "description": f"High trading fees: Buy {buy_tax}%, Sell {sell_tax}%",
                "severity": "high",
                "impact": "Users pay high transaction costs"
            })
        
        # Calculate overall security score
        total_issues = len(critical_issues) + len(high_issues) + len(medium_issues) + len(low_issues)
        security_score = max(0, 100 - (len(critical_issues) * 25 + len(high_issues) * 15 + 
                                     len(medium_issues) * 10 + len(low_issues) * 5))
        
        return {
            "overall_score": security_score,
            "risk_score": risk_score,
            "critical_issues": critical_issues,
            "high_issues": high_issues,
            "medium_issues": medium_issues,
            "low_issues": low_issues,
            "total_issues": total_issues,
            "security_grade": self._get_security_grade(security_score)
        }
    
    def _generate_recommendations(self, static_analysis: Dict[str, Any], 
                                dynamic_analysis: Dict[str, Any], 
                                onchain_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate detailed improvement recommendations."""
        recommendations = []
        
        # Static analysis recommendations
        if static_analysis.get("owner", {}).get("renounced") == False:
            recommendations.append({
                "category": "ownership",
                "priority": "high",
                "title": "Renounce Contract Ownership",
                "description": "Consider renouncing contract ownership to increase trust",
                "implementation": "Call renounceOwnership() function",
                "impact": "Increases decentralization and user trust"
            })
        
        if static_analysis.get("has_mint"):
            recommendations.append({
                "category": "tokenomics",
                "priority": "medium",
                "title": "Remove Mint Function",
                "description": "Mint function allows unlimited token creation",
                "implementation": "Remove mint function or add strict controls",
                "impact": "Prevents inflation and maintains token value"
            })
        
        if static_analysis.get("has_pause"):
            recommendations.append({
                "category": "functionality",
                "priority": "medium",
                "title": "Remove Pause Function",
                "description": "Pause function can halt all trading",
                "implementation": "Remove pause functionality or add timelock",
                "impact": "Ensures continuous trading availability"
            })
        
        # Dynamic analysis recommendations
        fees = dynamic_analysis.get("fees", {})
        if fees.get("buy", 0) > 5 or fees.get("sell", 0) > 5:
            recommendations.append({
                "category": "fees",
                "priority": "medium",
                "title": "Reduce Trading Fees",
                "description": f"Current fees: Buy {fees.get('buy', 0)}%, Sell {fees.get('sell', 0)}%",
                "implementation": "Lower fee percentages in contract",
                "impact": "Improves user experience and trading volume"
            })
        
        # On-chain analysis recommendations
        if not onchain_analysis.get("liquidity", {}).get("locked"):
            recommendations.append({
                "category": "liquidity",
                "priority": "high",
                "title": "Lock Liquidity",
                "description": "Liquidity is not locked, creating rug pull risk",
                "implementation": "Use a liquidity locker service",
                "impact": "Prevents rug pulls and increases investor confidence"
            })
        
        return recommendations
    
    def _assess_code_quality(self, source_code: str, static_results: Dict[str, Any]) -> Dict[str, Any]:
        """Assess code quality and best practices."""
        issues = []
        score = 100
        
        # Check for common issues
        if "pragma solidity" not in source_code.lower():
            issues.append("Missing pragma solidity directive")
            score -= 10
        
        if len(static_results.get("dangerous_functions_found", [])) > 0:
            issues.append("Contains dangerous functions")
            score -= 20
        
        if "import" not in source_code.lower():
            issues.append("No imports found - possible inline code")
            score -= 5
        
        # Check for documentation
        if "/**" not in source_code and "//" not in source_code:
            issues.append("Lack of code documentation")
            score -= 10
        
        return {
            "score": max(0, score),
            "issues": issues,
            "best_practices": {
                "has_documentation": "/**" in source_code or "//" in source_code,
                "uses_imports": "import" in source_code.lower(),
                "has_pragma": "pragma solidity" in source_code.lower()
            }
        }
    
    def _classify_vulnerabilities(self, static_results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Classify found vulnerabilities by type and severity."""
        vulnerabilities = []
        
        dangerous_functions = static_results.get("dangerous_functions_found", [])
        for func in dangerous_functions:
            vulnerabilities.append({
                "type": "dangerous_function",
                "name": func,
                "severity": "high",
                "description": f"Dangerous function '{func}' found in contract",
                "recommendation": f"Review and secure the '{func}' function"
            })
        
        if static_results.get("has_mint"):
            vulnerabilities.append({
                "type": "mint_function",
                "severity": "medium",
                "description": "Contract has mint function that can create new tokens",
                "recommendation": "Consider removing or adding strict controls to mint function"
            })
        
        if static_results.get("has_blacklist"):
            vulnerabilities.append({
                "type": "blacklist_function",
                "severity": "medium",
                "description": "Contract can blacklist addresses",
                "recommendation": "Ensure blacklist function has proper governance"
            })
        
        return vulnerabilities
    
    def _aggregate_dynamic_results(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Aggregate multiple dynamic analysis results."""
        if not results:
            return {"status": "no_results"}
        
        # Create a new result dict to avoid circular references
        base_result = results[0].copy() if results else {}
        base_result["scenarios_tested"] = len(results)
        # Don't include all scenarios to avoid potential circular references
        base_result["scenarios_summary"] = {
            "total_tested": len(results),
            "successful_scenarios": sum(1 for r in results if r.get("status") == "success")
        }
        
        return base_result
    
    def _analyze_trading_patterns(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze trading patterns across different scenarios."""
        patterns = {
            "consistent_fees": True,
            "scalable_trading": True,
            "issues": []
        }
        
        if len(results) > 1:
            # Check fee consistency
            fees = [r.get("fees", {}) for r in results]
            buy_fees = [f.get("buy", 0) for f in fees]
            sell_fees = [f.get("sell", 0) for f in fees]
            
            if len(set(buy_fees)) > 1 or len(set(sell_fees)) > 1:
                patterns["consistent_fees"] = False
                patterns["issues"].append("Trading fees vary by transaction size")
        
        return patterns
    
    def _calculate_success_rate(self, simulation_details: Dict[str, Any]) -> float:
        """Calculate success rate from simulation details."""
        buy_tests = simulation_details.get("buy_tests", [])
        sell_tests = simulation_details.get("sell_tests", [])
        
        total_tests = len(buy_tests) + len(sell_tests)
        if total_tests == 0:
            return 0.0
        
        successful_tests = (
            sum(1 for test in buy_tests if test.get("success", False)) +
            sum(1 for test in sell_tests if test.get("success", False))
        )
        
        return round((successful_tests / total_tests) * 100, 2)
    
    def _analyze_holders(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze token holder distribution."""
        # This would typically fetch real holder data
        return {
            "total_holders": "Unknown",
            "top_10_concentration": "Unknown",
            "distribution_score": 50,
            "issues": ["Holder data not available for analysis"]
        }
    
    def _analyze_liquidity(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze liquidity metrics."""
        lp_info = metadata.get("lp_info", {})
        
        return {
            "locked": lp_info.get("locked", False),
            "lock_percentage": lp_info.get("percent_locked"),
            "lock_duration": lp_info.get("lock_duration"),
            "unlock_date": lp_info.get("unlock_date"),
            "liquidity_score": 30 if not lp_info.get("locked") else 80,
            "recommendations": ["Lock liquidity to prevent rug pulls"] if not lp_info.get("locked") else []
        }
    
    def _get_security_grade(self, score: int) -> str:
        """Get security grade based on score."""
        if score >= 90:
            return "A+"
        elif score >= 80:
            return "A"
        elif score >= 70:
            return "B"
        elif score >= 60:
            return "C"
        elif score >= 50:
            return "D"
        else:
            return "F"
    
    def _build_audit_response(self, token_address: str, metadata: Dict[str, Any], 
                            static_analysis: Dict[str, Any], dynamic_analysis: Dict[str, Any],
                            onchain_analysis: Dict[str, Any], security_assessment: Dict[str, Any],
                            recommendations: List[Dict[str, Any]], start_time: float) -> Dict[str, Any]:
        """Build comprehensive audit response."""
        return {
            "status": "success",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "analysis_type": "comprehensive_audit",
            "token_address": token_address,
            
            # Token information
            "token_info": {
                "name": metadata.get("TokenName", "Unknown"),
                "symbol": metadata.get("TokenSymbol", "Unknown"),
                "decimals": int(metadata.get("Decimals", 18)),
                "total_supply": metadata.get("TotalSupply", "0"),
                "contract_creator": metadata.get("ContractCreator", "Unknown"),
                "verified": metadata.get("is_verified", False),
                "creation_date": metadata.get("contract_created"),
                "compiler_version": metadata.get("CompilerVersion", "Unknown")
            },
            
            # Security assessment
            "security_assessment": security_assessment,
            
            # Detailed analysis results
            "static_analysis": static_analysis,
            "dynamic_analysis": dynamic_analysis,
            "onchain_analysis": onchain_analysis,
            
            # Vulnerabilities summary
            "vulnerabilities": [
                *security_assessment.get("critical_issues", []),
                *security_assessment.get("high_issues", []),
                *security_assessment.get("medium_issues", []),
                *security_assessment.get("low_issues", [])
            ],
            
            # Improvement recommendations
            "recommendations": recommendations,
            
            # Audit metadata
            "audit_info": {
                "duration_ms": round((time.time() - start_time) * 1000, 2),
                "audit_version": "1.0.0",
                "data_sources": ["BSC", "Contract Analysis", "Simulation", "On-chain Data"],
                "analysis_depth": "comprehensive",
                "confidence_level": "high" if metadata.get("is_verified") else "medium"
            }
        }
    
    def _create_error_response(self, token_address: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Create error response for failed audit."""
        error_msg = metadata.get("error", "Audit failed")
        
        return {
            "status": "error",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "analysis_type": "comprehensive_audit",
            "token_address": token_address,
            "error": error_msg,
            "recommendations": [{
                "category": "general",
                "priority": "critical",
                "title": "Cannot Complete Audit",
                "description": f"Audit failed: {error_msg}",
                "implementation": "Verify token address and try again",
                "impact": "Unable to assess token security"
            }]
        }

# Global instance
token_audit_service = TokenAuditService() 