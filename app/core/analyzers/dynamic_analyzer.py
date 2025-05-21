from typing import Dict, Any, List, Tuple
from decimal import Decimal
import time
import traceback
from app.core.interfaces.analyzer import Alert
from app.core.utils.logger import get_logger

logger = get_logger(__name__)

def _calculate_tax_and_slippage(expected: float, received: float) -> Tuple[float, float, List[dict]]:
    """
    Calculate tax and slippage based on expected and received amounts.

    Returns:
        Tuple of (tax_percentage, slippage_percentage, alerts)
    """
    alerts = []
    try:
        if not expected or not received or expected <= 0:
            logger.debug("Invalid input for tax calculation", 
                         context={"expected": expected, "received": received})
            return 0.0, 0.0, alerts
        
        tax = max(0, 100 * (1 - (received / expected)))
        slippage = abs(100 * (received - expected) / expected)

        if tax > 10:
            logger.warning("High tax detected", context={"tax_percent": tax, "expected": expected, "received": received})

        if slippage > 5:
            alert_msg = f"This token experiences high slippage (Buy: {slippage:.2f}%, Sell: {slippage:.2f}%)."
            logger.warning(alert_msg)
            alerts.append(Alert(
                title="High Slippage Detected",
                description=alert_msg,
                severity="medium"
            ).dict())

        return round(tax, 2), round(slippage, 2), alerts

    except Exception as e:
        logger.error("Error in tax/slippage calculation", 
                     context={"expected": expected, "received": received, "error": str(e)},
                     exc_info=True)
        return 0.0, 0.0, alerts


def _check_suspicious_patterns(buy_data: dict, sell_data: dict) -> Tuple[Dict[str, Any], List[dict]]:
    """
    Check for suspicious patterns in buy/sell transactions.

    Returns:
        Tuple with (analysis result, alerts)
    """
    alerts = []
    analysis_start = time.time()
    logger.debug("Checking for suspicious patterns")
    
    try:
        buy_success = buy_data.get("success", False)
        sell_success = sell_data.get("success", False)

        is_honeypot = buy_success and not sell_success
        if is_honeypot:
            logger.warning("Potential honeypot detected - buy succeeds but sell fails")

        buy_expected = buy_data.get("expected_output", 0)
        buy_actual = buy_data.get("actual_output", 0)
        buy_tax, buy_slippage, buy_alerts = _calculate_tax_and_slippage(buy_expected, buy_actual)

        sell_expected = sell_data.get("expected_output", 0)
        sell_actual = sell_data.get("actual_output", 0)
        sell_tax, sell_slippage, sell_alerts = _calculate_tax_and_slippage(sell_expected, sell_actual)

        alerts.extend(buy_alerts)
        alerts.extend(sell_alerts)

        high_tax = buy_tax > 10 or sell_tax > 10
        if high_tax:
            logger.warning("High tax detected", context={"buy_tax": buy_tax, "sell_tax": sell_tax})
            alert_msg = f"This token has a high transaction tax (Buy: {buy_tax}%, Sell: {sell_tax}%)."
            alerts.append(Alert(
                title="High Transaction Tax",
                description=alert_msg,
                severity="high"
            ).dict())

        tax_discrepancy = abs(buy_tax - sell_tax) > 10
        high_slippage = buy_slippage > 5 or sell_slippage > 5

        result = {
            "is_honeypot": is_honeypot,
            "high_tax": high_tax,
            "tax_discrepancy": tax_discrepancy,
            "buy_tax": buy_tax,
            "sell_tax": sell_tax,
            "buy_slippage": buy_slippage,
            "sell_slippage": sell_slippage
        }

        logger.debug("Suspicious patterns analysis completed",
                     context={"duration_seconds": time.time() - analysis_start})
        return result, alerts

    except Exception as e:
        logger.error("Error in suspicious patterns analysis",
                     context={"error": str(e)},
                     exc_info=True)
        return {
            "is_honeypot": False,
            "high_tax": False,
            "tax_discrepancy": False,
            "buy_tax": 0.0,
            "sell_tax": 0.0,
            "buy_slippage": 0.0,
            "sell_slippage": 0.0
        }, alerts


def analyze_dynamic(simulation_result: dict) -> Dict[str, Any]:
    """
    Analyze token buy/sell simulation results.
    """
    logger.info("Starting dynamic analysis of token")

    if not isinstance(simulation_result, dict):
        try:
            import json
            simulation_result = json.loads(simulation_result)
        except Exception:
            logger.error("Failed to parse simulation result", context={"raw_result": simulation_result})
            raise ValueError("Invalid simulation result: not a valid JSON dict.")
            
    if not all(k in simulation_result for k in ["buy", "sell"]):
        raise ValueError("Invalid simulation result format. Missing 'buy' or 'sell' data.")


    analysis_start = time.time()
    alerts = []

    try:
        buy_data = simulation_result.get("buy", {})
        sell_data = simulation_result.get("sell", {})

        is_honeypot = (
            buy_data.get("success") is True and 
            sell_data.get("success") is False and
            buy_data.get("error") is None and
            sell_data.get("error") is not None
        )

        if is_honeypot:
            logger.critical("Honeypot detected! Token can be bought but not sold.")
            alerts.append(Alert(
                title="Honeypot Detected",
                description="This token appears to be a honeypot. You can buy but not sell.",
                severity="critical"
            ).dict())

        buy_tax, buy_slippage, buy_alerts = _calculate_tax_and_slippage(
            buy_data.get("expected_amount_out"),
            buy_data.get("amount_out")
        )

        sell_tax, sell_slippage, sell_alerts = _calculate_tax_and_slippage(
            sell_data.get("expected_amount_out"),
            sell_data.get("amount_out")
        )

        alerts.extend(buy_alerts)
        alerts.extend(sell_alerts)

        suspicious, suspicious_alerts = _check_suspicious_patterns(buy_data, sell_data)
        alerts.extend(suspicious_alerts)

        result = {
            "honeypot": is_honeypot,
            "tax": {
                "buy": buy_tax,
                "sell": sell_tax
            },
            "slippage": {
                "buy": buy_slippage,
                "sell": sell_slippage
            },
            "suspicious_patterns": suspicious,
            "alerts": alerts
        }

        logger.info("Dynamic analysis completed", context={
            "honeypot": is_honeypot,
            "buy_tax": buy_tax,
            "sell_tax": sell_tax,
            "total_alerts": len(alerts)
        })

        return result

    except Exception as e:
        error_message = f"Error in dynamic analysis: {str(e)}"
        logger.critical("Dynamic analysis failed", context={
            "error": str(e),
            "error_type": type(e).__name__,
            "duration_seconds": time.time() - analysis_start,
            "traceback": traceback.format_exc()
        }, exc_info=True)

        return {
            "honeypot": True,
            "tax": {
                "buy": 100.0,
                "sell": 100.0
            },
            "slippage": {
                "buy": 0.0,
                "sell": 0.0
            },
            "suspicious_patterns": {
                "is_honeypot": True,
                "high_tax": True,
                "tax_discrepancy": True,
                "buy_tax": 0.0,
                "sell_tax": 0.0,
                "buy_slippage": 0.0,
                "sell_slippage": 0.0
            },
            "alerts": [
                Alert(
                    title="Dynamic Analysis Failed",
                    description=error_message,
                    severity="critical"
                ).dict()
            ]
        }
