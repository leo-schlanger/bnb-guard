"""
Enhanced Dynamic Analyzer with Advanced Honeypot Detection

This module provides comprehensive dynamic analysis including:
- Real PancakeSwap simulation
- Advanced honeypot detection
- Fee analysis
- Trading pattern analysis
"""

from typing import Dict, Any
import time
import traceback
from app.core.utils.logger import get_logger

logger = get_logger(__name__)

def create_alert(title: str, description: str, severity: str) -> Dict[str, Any]:
    """Create an alert dictionary."""
    return {
        "title": title,
        "description": description,
        "severity": severity,
        "type": "security_alert"
    }

def _calculate_tax_and_slippage(expected: float, received: float) -> tuple[float, float, list[dict]]:
    """Calculate tax and slippage from expected vs received amounts."""
    alerts = []
    try:
        if expected is None or received is None:
            logger.debug("Missing input for tax calculation", context={"expected": expected, "received": received})
            return 0.0, 0.0, alerts

        expected = float(expected)
        received = float(received)

        if expected <= 0:
            logger.debug("Expected value must be greater than 0", context={"expected": expected})
            return 0.0, 0.0, alerts

        tax = max(0, 100 * (1 - (received / expected)))
        slippage = abs(100 * (received - expected) / expected)

        if slippage > 5:
            alerts.append(create_alert(
                title="High Slippage Detected",
                description=f"Slippage is unusually high: {slippage:.2f}%",
                severity="medium"
            ))

        return round(tax, 2), round(slippage, 2), alerts

    except Exception as e:
        logger.error("Error calculating tax/slippage", context={"error": str(e)}, exc_info=True)
        return 0.0, 0.0, alerts

async def analyze_dynamic_advanced(token_address: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
    """
    Advanced dynamic analysis using real honeypot detection.
    
    Args:
        token_address: Token contract address
        metadata: Token metadata
        
    Returns:
        Comprehensive dynamic analysis results
    """
    logger.info("Starting advanced dynamic analysis", {
        "token_address": token_address,
        "token_name": metadata.get("name", "Unknown")
    })
    
    try:
        # Import here to avoid circular imports
        from app.core.analyzers.honeypot_detector import honeypot_detector
        
        # Run comprehensive honeypot detection
        honeypot_result = await honeypot_detector.detect_honeypot(token_address, metadata)
        
        # Extract key information
        alerts = []
        
        # Add alerts based on honeypot detection
        if honeypot_result["is_honeypot"]:
            alerts.append(create_alert(
                title="Honeypot Detected",
                description=honeypot_result["recommendation"],
                severity="critical"
            ))
        
        # Add alerts for high taxes
        buy_tax = honeypot_result.get("buy_tax", 0)
        sell_tax = honeypot_result.get("sell_tax", 0)
        
        if buy_tax > 10 or sell_tax > 10:
            alerts.append(create_alert(
                title="High Transaction Tax",
                description=f"High taxes detected: Buy {buy_tax}%, Sell {sell_tax}%",
                severity="high"
            ))
        
        # Add alerts for tax discrepancy
        if abs(buy_tax - sell_tax) > 10:
            alerts.append(create_alert(
                title="Tax Discrepancy Detected",
                description=f"Tax discrepancy between buy ({buy_tax}%) and sell ({sell_tax}%) is suspicious.",
                severity="medium"
            ))
        
        # Add alerts for trading restrictions
        if not honeypot_result.get("can_buy", True):
            alerts.append(create_alert(
                title="Cannot Buy Token",
                description="Token purchase appears to be blocked",
                severity="critical"
            ))
        
        if not honeypot_result.get("can_sell", True):
            alerts.append(create_alert(
                title="Cannot Sell Token",
                description="Token sale appears to be blocked (honeypot behavior)",
                severity="critical"
            ))
        
        # Build comprehensive result
        result = {
            "honeypot": {
                "is_honeypot": honeypot_result["is_honeypot"],
                "confidence": honeypot_result["confidence"],
                "risk_level": honeypot_result["risk_level"],
                "can_buy": honeypot_result.get("can_buy", False),
                "can_sell": honeypot_result.get("can_sell", False),
                "indicators": honeypot_result.get("indicators", []),
                "recommendation": honeypot_result["recommendation"],
                "error": honeypot_result.get("error")
            },
            "fees": {
                "buy": buy_tax,
                "sell": sell_tax,
                "buy_slippage": 0.0,  # Will be calculated from simulation
                "sell_slippage": 0.0,  # Will be calculated from simulation
                "buy_mutable": False,  # Would need contract analysis
                "sell_mutable": False  # Would need contract analysis
            },
            "simulation_details": {
                "buy_tests": honeypot_result.get("simulation_results", {}).get("buy_tests", []),
                "sell_tests": honeypot_result.get("simulation_results", {}).get("sell_tests", []),
                "pattern_analysis": honeypot_result.get("pattern_analysis", {}),
                "liquidity_analysis": honeypot_result.get("liquidity_analysis", {})
            },
            "alerts": alerts,
            "analysis_method": "advanced_honeypot_detection"
        }
        
        logger.info("Advanced dynamic analysis completed", {
            "token_address": token_address,
            "is_honeypot": result["honeypot"]["is_honeypot"],
            "confidence": result["honeypot"]["confidence"],
            "buy_tax": buy_tax,
            "sell_tax": sell_tax,
            "total_alerts": len(alerts)
        })
        
        return result
        
    except Exception as e:
        logger.error("Advanced dynamic analysis failed", {
            "token_address": token_address,
            "error": str(e),
            "error_type": type(e).__name__
        }, exc_info=True)
        
        # Fallback to basic analysis
        return await analyze_dynamic_fallback(token_address, str(e))

async def analyze_dynamic_fallback(token_address: str, error: str) -> Dict[str, Any]:
    """Fallback dynamic analysis when advanced detection fails."""
    logger.warning("Using fallback dynamic analysis", {
        "token_address": token_address,
        "error": error
    })
    
    return {
        "honeypot": {
            "is_honeypot": True,  # Assume worst case
            "confidence": 0,
            "risk_level": "UNKNOWN",
            "can_buy": False,
            "can_sell": False,
            "indicators": ["Analysis failed"],
            "recommendation": "⚠️ UNKNOWN RISK - Analysis failed, proceed with extreme caution",
            "error": error
        },
        "fees": {
            "buy": 100.0,  # Assume high fees
            "sell": 100.0,
            "buy_slippage": 0.0,
            "sell_slippage": 0.0,
            "buy_mutable": False,
            "sell_mutable": False
        },
        "simulation_details": {
            "buy_tests": [],
            "sell_tests": [],
            "pattern_analysis": {},
            "liquidity_analysis": {}
        },
        "alerts": [
            create_alert(
                title="Dynamic Analysis Failed",
                description=f"Analysis failed: {error}",
                severity="critical"
            )
        ],
        "analysis_method": "fallback"
    }

def analyze_dynamic(simulation_result: dict) -> Dict[str, Any]:
    """
    Legacy dynamic analysis for backward compatibility.
    
    This function maintains compatibility with existing code that uses
    simulation results directly.
    """
    logger.info("Starting legacy dynamic analysis")

    if not isinstance(simulation_result, dict):
        try:
            import json
            simulation_result = json.loads(simulation_result)
        except Exception:
            logger.error("Failed to parse simulation result", context={"raw_result": simulation_result})
            raise ValueError("Invalid simulation result: not a valid JSON dict.")

    if not all(k in simulation_result for k in ["buy", "sell"]):
        raise ValueError("Invalid simulation result format. Missing 'buy' or 'sell' data.")

    alerts = []
    analysis_start = time.time()

    try:
        buy_data = simulation_result.get("buy", {})
        sell_data = simulation_result.get("sell", {})

        buy_expected = buy_data.get("expected_amount_out", 0)
        buy_actual = buy_data.get("amount_out", 0)
        buy_tax, buy_slippage, buy_alerts = _calculate_tax_and_slippage(buy_expected, buy_actual)

        sell_expected = sell_data.get("expected_amount_out", 0)
        sell_actual = sell_data.get("amount_out", 0)
        sell_tax, sell_slippage, sell_alerts = _calculate_tax_and_slippage(sell_expected, sell_actual)

        alerts.extend(buy_alerts)
        alerts.extend(sell_alerts)

        buy_success = buy_data.get("success", False)
        sell_success = sell_data.get("success", False)
        sell_error = sell_data.get("error")
        buy_error = buy_data.get("error")

        is_honeypot = (
            buy_success and (
                not sell_success or
                sell_actual == 0 or
                sell_error is not None
            )
        )

        if is_honeypot:
            logger.critical("Honeypot behavior detected")
            alerts.append(create_alert(
                title="Honeypot Detected",
                description="This token appears to be a honeypot. You can buy but not sell (or receive nothing).",
                severity="critical"
            ))

        high_tax = buy_tax > 10 or sell_tax > 10
        tax_discrepancy = abs(buy_tax - sell_tax) > 10
        high_slippage = buy_slippage > 5 or sell_slippage > 5

        if high_tax:
            alerts.append(create_alert(
                title="High Transaction Tax",
                description=f"High taxes detected: Buy {buy_tax}%, Sell {sell_tax}%",
                severity="high"
            ))

        if tax_discrepancy:
            alerts.append(create_alert(
                title="Tax Discrepancy Detected",
                description=f"Tax discrepancy between buy ({buy_tax}%) and sell ({sell_tax}%) is suspicious.",
                severity="medium"
            ))

        result = {
            "honeypot": {
                "is_honeypot": is_honeypot,
                "buy_success": buy_success,
                "sell_success": sell_success,
                "high_tax": high_tax,
                "tax_discrepancy": tax_discrepancy,
                "error": None
            },
            "fees": {
                "buy": buy_tax,
                "sell": sell_tax,
                "buy_slippage": buy_slippage,
                "sell_slippage": sell_slippage,
                "buy_mutable": False,
                "sell_mutable": False
            },
            "alerts": alerts
        }

        logger.info("Legacy dynamic analysis completed", context={
            "honeypot": is_honeypot,
            "buy_tax": buy_tax,
            "sell_tax": sell_tax,
            "total_alerts": len(alerts)
        })

        return result

    except Exception as e:
        error_message = f"Error in dynamic analysis: {str(e)}"
        logger.critical("Legacy dynamic analysis failed", context={
            "error": str(e),
            "error_type": type(e).__name__,
            "duration_seconds": time.time() - analysis_start,
            "traceback": traceback.format_exc()
        }, exc_info=True)

        return {
            "honeypot": {
                "is_honeypot": True,
                "buy_success": None,
                "sell_success": None,
                "high_tax": None,
                "tax_discrepancy": None,
                "error": error_message
            },
            "fees": {
                "buy": 100.0,
                "sell": 100.0,
                "buy_slippage": 0.0,
                "sell_slippage": 0.0,
                "buy_mutable": False,
                "sell_mutable": False
            },
            "alerts": [
                create_alert(
                    title="Dynamic Analysis Failed",
                    description=error_message,
                    severity="critical"
                )
            ]
        }
