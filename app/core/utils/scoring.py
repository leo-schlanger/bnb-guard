from typing import Dict, List, Any, Tuple, Optional
import time
import traceback
from app.core.interfaces.analyzer import Alert
from app.core.utils.logger import get_logger

# Initialize logger
logger = get_logger(__name__)

# Constants
MAX_SCORE = 100
MIN_SCORE = 0

class RiskScoreError(Exception):
    """Custom exception for risk score calculation errors."""
    pass

def calculate_risk_score(
    static_alerts: Dict[str, Any],
    dynamic_alerts: Dict[str, Any],
    onchain_alerts: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Calculate a comprehensive risk score based on static, dynamic, and on-chain analysis.
    
    Args:
        static_alerts: Results from static code analysis
        dynamic_alerts: Results from dynamic analysis (simulations)
        onchain_alerts: Results from on-chain analysis
        
    Returns:
        Dictionary containing the risk score, grade, and detailed risk breakdown
        
    Raises:
        RiskScoreError: If there's an error in the scoring process
    """
    start_time = time.time()
    token_address = static_alerts.get("token_address", "unknown")
    logger.info("Starting risk score calculation", 
               context={
                   "token_address": token_address,
                   "has_static_alerts": bool(static_alerts),
                   "has_dynamic_alerts": bool(dynamic_alerts),
                   "has_onchain_alerts": bool(onchain_alerts)
               })
    
    # Log detailed input data for debugging
    logger.debug("Risk score calculation input data",
                context={
                    "static_alerts_keys": list(static_alerts.keys()),
                    "dynamic_alerts_keys": list(dynamic_alerts.keys()) if isinstance(dynamic_alerts, dict) else str(type(dynamic_alerts)),
                    "onchain_alerts_keys": list(onchain_alerts.keys()) if isinstance(onchain_alerts, dict) else str(type(onchain_alerts))
                })
    
    try:
        score = MAX_SCORE
        alerts = []
        warnings = []
        risks = []
        risk_factors = []
        
        # Track score adjustments for transparency
        score_breakdown = {
            "base_score": score,
            "adjustments": [],
            "final_score": score
        }
        
        def _apply_score_adjustment(amount: int, reason: str, risk_type: str, 
                                 severity: str, details: Optional[Dict] = None):
            """Helper function to apply score adjustments consistently."""
            nonlocal score
            score = max(MIN_SCORE, score + amount)  # Ensure score doesn't go below 0
            
            # Log the adjustment
            adjustment = {
                "amount": amount,
                "reason": reason,
                "type": risk_type,
                "severity": severity
            }
            if details:
                adjustment["details"] = details
                
            score_breakdown["adjustments"].append(adjustment)
            
            # Update final score in breakdown
            score_breakdown["final_score"] = score
            
            return adjustment
        
        # 🎯 Critical Functions Analysis
        dangerous_functions = static_alerts.get("functions", [])
        if dangerous_functions:
            func_names = [f.get('name', 'unknown') for f in dangerous_functions]
            func_severities = [f.get('severity', 'medium') for f in dangerous_functions]
            func_descriptions = [f.get('message', '') for f in dangerous_functions if 'message' in f]
            
            # Log the dangerous functions found
            logger.warning("Dangerous functions detected in contract",
                         context={
                             "count": len(dangerous_functions),
                             "functions": func_names,
                             "severities": func_severities
                         })
            
            # Calculate penalty based on severity of functions
            severity_penalty = {
                'critical': -30,
                'high': -20,
                'medium': -10,
                'low': -5
            }
            
            # Use the highest severity penalty
            max_severity = max(func_severities, key=lambda x: ['low', 'medium', 'high', 'critical'].index(x.lower()))
            penalty = severity_penalty.get(max_severity.lower(), -10)
            
            adjustment = _apply_score_adjustment(
                amount=penalty,
                reason=f"Critical functions detected (severity: {max_severity})",
                risk_type="critical_functions",
                severity=max_severity,
                details={
                    "functions": func_names,
                    "severities": func_severities,
                    "descriptions": func_descriptions,
                    "applied_penalty": penalty
                }
            )
            
            alert_msg = f"{len(dangerous_functions)} critical functions detected (highest severity: {max_severity})"
            alerts.append({
                "type": "critical_functions",
                "severity": max_severity,
                "message": alert_msg,
                "details": {
                    "functions": func_names,
                    "severities": func_severities,
                    "descriptions": func_descriptions
                }
            })
            
            risks.append({
                "type": "critical_functions",
                "description": f"Critical functions found: {', '.join(func_descriptions)}",
                "severity": "high",
                "impact": "high",
                "recommendation": "Review and audit these functions carefully before interacting with the contract."
            })
            
            logger.warning(
                "Critical functions detected in contract",
                context={
                    "token_address": token_address,
                    "functions": func_names,
                    "score_adjustment": adjustment
                }
            )

        # 👑 Owner Analysis
        owner_info = static_alerts.get("owner", {})
        if not owner_info.get("renounced", False):
            owner_address = owner_info.get("address", "unknown")
            adjustment = _apply_score_adjustment(
                amount=-10,
                reason="Ownership not renounced",
                risk_type="ownership",
                severity="high",
                details={"owner_address": owner_address}
            )
            
            alert_msg = f"Contract ownership not renounced (owner: {owner_address})"
            alerts.append({
                "type": "ownership_not_renounced",
                "severity": "high",
                "message": alert_msg,
                "details": {"owner_address": owner_address}
            })
            
            risks.append({
                "type": "ownership",
                "description": "Contract still under owner control",
                "severity": "high",
                "impact": "high",
                "recommendation": "Consider interacting only with contracts that have renounced ownership or where you trust the owner.",
                "owner_address": owner_address
            })
            
            logger.warning(
                "Contract ownership not renounced",
                context={
                    "token_address": token_address,
                    "owner_address": owner_address,
                    "score_adjustment": adjustment
                }
            )
        else:
            logger.debug("Contract ownership is renounced",
                       context={"token_address": token_address})

        # 💸 Fee Analysis
        fees = dynamic_alerts.get("fees", {})
        # 🔒 LP Lock Check
        lp_info = onchain_alerts.get("lp_info", {})
        is_locked = lp_info.get("locked", False)
        locked_percent = lp_info.get("percent_locked", 0)
        unlock_date = lp_info.get("unlock_date")
        
        logger.info("Checking LP lock status",
                   context={
                       "is_locked": is_locked,
                       "locked_percent": locked_percent,
                       "unlock_date": unlock_date
                   })
        
        if not is_locked or locked_percent < 90:  # Consider <90% as not properly locked
            penalty = -20 if not is_locked else -10
            reason = "Liquidity not locked" if not is_locked else f"Only {locked_percent}% of liquidity is locked"
            
            _apply_score_adjustment(
                amount=penalty,
                reason=reason,
                risk_type="lp_not_locked",
                severity="high" if not is_locked else "medium",
                details={
                    "is_locked": is_locked,
                    "locked_percent": locked_percent,
                    "unlock_date": unlock_date,
                    "applied_penalty": penalty
                }
            )
            
            alert_msg = ("Liquidity is not locked, high risk of rug pull" if not is_locked
                       else f"Only {locked_percent}% of liquidity is locked")
            alerts.append({
                "type": "lp_not_locked",
                "severity": "high" if not is_locked else "medium",
                "message": alert_msg,
                "details": {
                    "is_locked": is_locked,
                    "locked_percent": locked_percent,
                    "unlock_date": unlock_date
                }
            })

        # 💸 Fee Analysis
        fees = dynamic_alerts.get("fees", {})
        buy_fee = fees.get("buy", 0)
        sell_fee = fees.get("sell", 0)
        
        # Log fee information
        logger.info("Analyzing transaction fees",
                   context={
                       "buy_fee_percent": buy_fee,
                       "sell_fee_percent": sell_fee,
                       "fee_mutable": fees.get("mutable", False)
                   })
        
        # Penalize high fees
        if buy_fee > 10 or sell_fee > 10:  # More than 10% is high
            penalty = -15
            fee_details = {
                "buy_fee_percent": buy_fee,
                "sell_fee_percent": sell_fee,
                "fee_mutable": fees.get("mutable", False),
                "applied_penalty": penalty
            }
            
            _apply_score_adjustment(
                amount=penalty,
                reason=f"High transaction fees detected (Buy: {buy_fee}%, Sell: {sell_fee}%)",
                risk_type="high_fees",
                severity="high",
                details=fee_details
            )
            
            alerts.append({
                "type": "high_fees",
                "severity": "high",
                "message": f"High transaction fees detected (Buy: {buy_fee}%, Sell: {sell_fee}%)",
                "details": fee_details
            })

        # 🕵️ Honeypot Analysis
        honeypot_info = dynamic_alerts.get("honeypot", {})
        is_honeypot = honeypot_info.get("is_honeypot", False)
        
        if is_honeypot:
            logger.critical("Honeypot detected in token contract",
                          context={
                              "buy_success": honeypot_info.get("buy_success", False),
                              "sell_success": honeypot_info.get("sell_success", False),
                              "high_tax": honeypot_info.get("high_tax", False),
                              "tax_discrepancy": honeypot_info.get("tax_discrepancy", False)
                          })
            
            penalty = -50  # Major penalty for honeypot
            _apply_score_adjustment(
                amount=penalty,
                reason="Token appears to be a honeypot",
                risk_type="honeypot",
                severity="critical",
                details={
                    "buy_success": honeypot_info.get("buy_success", False),
                    "sell_success": honeypot_info.get("sell_success", False),
                    "high_tax": honeypot_info.get("high_tax", False),
                    "tax_discrepancy": honeypot_info.get("tax_discrepancy", False),
                    "applied_penalty": penalty
                }
            )
            
            alerts.append({
                "type": "honeypot",
                "severity": "critical",
                "message": "Token appears to be a honeypot (cannot sell after buying)",
                "details": {
                    "buy_success": honeypot_info.get("buy_success", False),
                    "sell_success": honeypot_info.get("sell_success", False),
                    "high_tax": honeypot_info.get("high_tax", False),
                    "tax_discrepancy": honeypot_info.get("tax_discrepancy", False)
                }
            })

        # 🏆 Final Score and Grade
        score = max(0, min(100, score))  # Ensure score is between 0-100
        
        # Determine grade
        if score >= 90:
            grade = "A"
        elif score >= 80:
            grade = "B"
        elif score >= 65:
            grade = "C"
        elif score >= 50:
            grade = "D"
        else:
            grade = "F"
        
        analysis_duration = time.time() - start_time
        
        # Log final score calculation
        logger.info("Final risk score calculated",
                  context={
                      "final_score": int(round(score)),
                      "grade": grade,
                      "total_alerts": len(alerts),
                      "total_warnings": len(warnings),
                      "total_risks": len(risks),
                      "analysis_duration_seconds": analysis_duration
                  })
        
        # Log detailed score breakdown for debugging
        logger.debug("Score breakdown",
                    context={
                        "base_score": score_breakdown.get("base_score"),
                        "final_score": int(round(score)),
                        "adjustments": [
                            {"reason": adj.get("reason"), "amount": adj.get("amount"), "type": adj.get("type")}
                            for adj in score_breakdown.get("adjustments", [])[:10]  # Limit to first 10 adjustments
                        ]
                    })
        
        # Prepare final response
        result = {
            "score": int(round(score)),
            "grade": grade,
            "alerts": alerts,
            "warnings": warnings,
            "risks": risks,
            "score_breakdown": score_breakdown,
            "analysis_timestamp": time.time(),
            "analysis_duration_seconds": analysis_duration
        }
        
        return result
        
    except Exception as e:
        error_msg = f"Error calculating risk score: {str(e)}"
        logger.critical(
            error_msg,
            context={
                "token_address": token_address,
                "error_type": type(e).__name__,
                "traceback": traceback.format_exc()
            },
            exc_info=True
        )
        raise RiskScoreError(error_msg) from e
