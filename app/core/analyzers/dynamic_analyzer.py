from typing import Dict, Any, List, Optional, Tuple
from decimal import Decimal
import time
import traceback
from app.core.interfaces.analyzer import Alert
from app.core.utils.logger import get_logger

# Initialize logger
logger = get_logger(__name__)

def _calculate_tax_and_slippage(expected: float, received: float) -> Tuple[float, float]:
    """
    Calculate tax and slippage based on expected and received amounts.
    
    Args:
        expected: Expected output amount
        received: Actual output amount received
        
    Returns:
        Tuple of (tax_percentage, slippage_percentage)
    """
    try:
        if not expected or not received or expected <= 0:
            logger.debug("Invalid input for tax calculation", 
                        context={"expected": expected, "received": received})
            return 0.0, 0.0
        
        tax = max(0, 100 * (1 - (received / expected)))
        slippage = abs(100 * (received - expected) / expected)
        
        # Log high values
        if tax > 10:  # Log high taxes
            logger.warning("High tax detected", 
                         context={"tax_percent": tax, "expected": expected, "received": received})
            
        if slippage > 5:  
            if slippage > 5:
                alert_msg = f"This token experiences high slippage (Buy: {slippage}%, Sell: {slippage}%)."
                logger.warning(alert_msg)
                alerts.append(Alert(
                    title="High Slippage Detected",
                    description=alert_msg,
                    severity="medium"
                ).dict())    
        return round(tax, 2), round(slippage, 2)
        
    except Exception as e:
        logger.error(
            "Error in tax/slippage calculation",
            context={"expected": expected, "received": received, "error": str(e)},
            exc_info=True
        )
        return 0.0, 0.0

def _check_suspicious_patterns(buy_data: dict, sell_data: dict) -> Dict[str, Any]:
    """
    Check for suspicious patterns in buy/sell transactions.
    
    Args:
        buy_data: Dictionary containing buy simulation results
        sell_data: Dictionary containing sell simulation results
        
    Returns:
        Dictionary with analysis results
    """
    analysis_start = time.time()
    logger.debug("Checking for suspicious patterns")
    
    try:
        buy_success = buy_data.get("success", False)
        sell_success = sell_data.get("success", False)
        
        # Log transaction status
        logger.debug("Transaction status", 
                    context={"buy_success": buy_success, "sell_success": sell_success})
        
        # Basic honeypot detection - buy works but sell doesn't
        is_honeypot = buy_success and not sell_success
        if is_honeypot:
            logger.warning("Potential honeypot detected - buy succeeds but sell fails")
        
        # Calculate taxes and slippage
        logger.debug("Calculating buy taxes and slippage")
        buy_expected = buy_data.get("expected_output", 0)
        buy_actual = buy_data.get("actual_output", 0)
        buy_tax, buy_slippage = _calculate_tax_and_slippage(buy_expected, buy_actual)
        
        logger.debug("Calculating sell taxes and slippage")
        sell_expected = sell_data.get("expected_output", 0)
        sell_actual = sell_data.get("actual_output", 0)
        sell_tax, sell_slippage = _calculate_tax_and_slippage(sell_expected, sell_actual)
        
        logger.info("Tax and slippage calculation completed", context={
            "buy_tax": buy_tax,
            "buy_slippage": buy_slippage,
            "sell_tax": sell_tax,
            "sell_slippage": sell_slippage
        })    
        
        # Log tax and slippage
        logger.debug("Tax and slippage analysis",
                    context={
                        "buy_tax": buy_tax,
                        "buy_slippage": buy_slippage,
                        "sell_tax": sell_tax,
                        "sell_slippage": sell_slippage
                    })
        
        # Check for high tax (more than 10%)
        high_tax = buy_tax > 10 or sell_tax > 10
        if high_tax:
            logger.warning("High tax detected", context={"buy_tax": buy_tax, "sell_tax": sell_tax})
            alert_msg = f"This token has a high transaction tax (Buy: {buy_tax}%, Sell: {sell_tax}%)."
            logger.warning(alert_msg)
            alerts.append(Alert(
                title="High Transaction Tax",
                description=alert_msg,
                severity="high"
            ).dict())
        
        # Check for large difference between buy and sell taxes
        tax_discrepancy = abs(buy_tax - sell_tax) > 10  # More than 10% difference
        if tax_discrepancy:
            logger.warning("Significant tax discrepancy between buy and sell",
                         context={"buy_tax": buy_tax, "sell_tax": sell_tax})
        
        # Check for high slippage (more than 5%)
        high_slippage = buy_slippage > 5 or sell_slippage > 5
        if high_slippage:
            logger.warning("High slippage detected", 
                          context={"buy_slippage": buy_slippage, "sell_slippage": sell_slippage})
        
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
        return result
        
    except Exception as e:
        logger.error(
            "Error in suspicious patterns analysis",
            context={"error": str(e)},
            exc_info=True
        )
        # Return safe defaults on error
        return {
            "is_honeypot": False,
            "high_tax": False,
            "tax_discrepancy": False,
            "buy_tax": 0.0,
            "sell_tax": 0.0,
            "buy_slippage": 0.0,
            "sell_slippage": 0.0
        }

def analyze_dynamic(simulation_result: dict) -> Dict[str, Any]:
    """
    Analyze token buy/sell simulation results.
    
    Args:
        simulation_result: Dictionary containing simulation results with:
            - buy: Buy simulation data
            - sell: Sell simulation data
            
    Returns:
        Dictionary with dynamic analysis results
    """
    logger.info("Starting dynamic analysis of token")
    logger.debug(f"Simulation result keys: {list(simulation_result.keys())}")
    
    if not simulation_result or not all(k in simulation_result for k in ["buy", "sell"]):
        error_msg = "Invalid simulation result format. Missing 'buy' or 'sell' data."
        logger.error(error_msg, context={"simulation_result_keys": list(simulation_result.keys())})
        raise ValueError(error_msg)
    analysis_start = time.time()
    logger.info("Starting dynamic analysis")
    
    try:
        if not simulation_result:
            logger.warning("Empty simulation result provided")
            return {}
            
        buy_data = simulation_result.get("buy", {})
        sell_data = simulation_result.get("sell", {})
        
        logger.debug(f"Buy data keys: {list(buy_data.keys())}")
        logger.debug(f"Sell data keys: {list(sell_data.keys())}")
        
        # Log basic transaction info if available
        if 'transaction' in buy_data:
            logger.debug(f"Buy transaction: {buy_data['transaction'].get('hash', 'N/A')}")
        if 'transaction' in sell_data:
            logger.debug(f"Sell transaction: {sell_data['transaction'].get('hash', 'N/A')}")
        
        logger.debug("Processing buy/sell data", 
                     context={"has_buy_data": bool(buy_data), "has_sell_data": bool(sell_data)})
        
        # Check for honeypot characteristics
        logger.debug("Checking for honeypot characteristics...")
        is_honeypot = (
            buy_data.get("success") is True and 
            sell_data.get("success") is False and
            buy_data.get("error") is None and
            sell_data.get("error") is not None
        )
        
        if is_honeypot:
            logger.warning("Honeypot detected! Token can be bought but not sold.", 
                          context={"buy_success": buy_data.get("success"), 
                                 "sell_success": sell_data.get("success"),
                                 "sell_error": sell_data.get("error")})
        else:
            logger.debug("No honeypot characteristics detected")    
        
        logger.debug("Transaction success status", 
                     context={"buy_success": buy_data.get("success"), "sell_success": sell_data.get("success")})
        
        # Calculate taxes and slippage
        logger.debug("Calculating buy taxes and slippage")
        buy_tax, buy_slippage = _calculate_tax_and_slippage(
            buy_data.get("expected_amount_out"),
            buy_data.get("amount_out")
        )
        
        logger.debug("Calculating sell taxes and slippage")
        sell_tax, sell_slippage = _calculate_tax_and_slippage(
            sell_data.get("expected_amount_out"),
            sell_data.get("amount_out")
        )
        
        logger.debug("Checking for suspicious patterns...")
        suspicious = _check_suspicious_patterns(buy_data, sell_data)
        if any(suspicious.values()):
            logger.warning("Suspicious patterns detected", context=suspicious)
        else:
            logger.debug("No suspicious patterns detected")
        
        # Check for mutable fees (if there's significant difference between calls)
        # This would normally require call history, so it's static for now
        buy_mutable = False
        sell_mutable = False
        
        # Create alerts based on analysis
        alerts = []
        
        if is_honeypot:
            alert_msg = "This token appears to be a honeypot. You can buy but not sell."
            logger.critical(alert_msg, context={"buy_success": buy_data.get("success"), 
                                             "sell_success": sell_data.get("success")})
            alerts.append(Alert(
                title="Honeypot Detected",
                description=alert_msg,
                severity="critical"
            ).dict())
        
        # Add suspicious pattern alerts
        for pattern, is_suspicious in suspicious.items():
            if is_suspicious:
                alert_msg = f"Suspicious trading pattern detected: {pattern}"
                logger.warning(alert_msg)
                alerts.append(Alert(
                    title=f"Suspicious Pattern: {pattern}",
                    description=alert_msg,
                    severity="high"
                ).dict())
        
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
        error_duration = time.time() - analysis_start
        error_message = f"Error in dynamic analysis: {str(e)}"
        
        logger.critical(
            "Dynamic analysis failed",
            context={
                "error": str(e),
                "error_type": type(e).__name__,
                "duration_seconds": error_duration,
                "traceback": traceback.format_exc()
            },
            exc_info=True
        )
        
        # Return a safe error response
        return {
            "honeypot": True,  # Assume worst case on error
            "tax": {
                "buy": 100.0,  # Assume worst case
                "sell": 100.0,  # Assume worst case
            },
            "slippage": {
                "buy": 0.0,
                "sell": 0.0,
            },
            "suspicious_patterns": {
                "is_honeypot": True,  # Assume worst case
                "high_tax": True,  # Assume worst case
                "tax_discrepancy": True,  # Assume worst case
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
