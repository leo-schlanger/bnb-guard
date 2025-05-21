import os
import sys
import traceback
from typing import Dict, Any, Optional, Tuple
from datetime import datetime

# Add project root to path
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
sys.path.insert(0, root_dir)

# Import logger first
from app.core.utils.logger import get_logger

# Initialize logger
logger = get_logger(__name__)

# Try to import required modules
MODULES = {
    'fetch_token_metadata': 'app.core.utils.metadata',
    'analyze_static': 'app.core.analyzers.static_analyzer',
    'analyze_dynamic': 'app.core.analyzers.dynamic_analyzer',
    'analyze_onchain': 'app.core.analyzers.onchain_analyzer',
    'calculate_risk_score': 'app.core.utils.scoring',
    'AnalysisResult': 'app.core.interfaces.analyzer'
}

# Import all required modules
for name, module_path in MODULES.items():
    try:
        if '.' in module_path:
            from importlib import import_module
            module = import_module(module_path)
            globals()[name] = getattr(module, name.split('.')[-1])
        else:
            exec(f'from {module_path} import {name}')
        logger.debug(f"Successfully imported {name} from {module_path}")
    except ImportError as e:
        logger.critical(
            f"Failed to import {name} from {module_path}",
            context={"error": str(e)},
            exc_info=True
        )
        raise ImportError(f"Failed to import {name} from {module_path}: {e}") from e

logger.info("All required modules imported successfully")

async def audit_token(token_address: str, lp_token_address: str = None) -> Dict[str, Any]:
    """
    Perform a comprehensive audit of a token contract.
    
    This function orchestrates the entire audit process, including:
    - Metadata fetching
    - Static analysis
    - Dynamic analysis (if simulation data is available)
    - On-chain analysis
    - Risk score calculation
    
    Args:
        token_address: The address of the token contract to audit
        lp_token_address: Optional address of the LP token contract
        
    Returns:
        Dictionary containing the audit results with the following structure:
        {
            "token_address": str,
            "lp_token_address": Optional[str],
            "audit_timestamp": str (ISO format),
            "token_name": str,
            "token_symbol": str,
            "token_decimals": int,
            "total_supply": float,
            "analysis": {
                "static": Dict,
                "dynamic": Dict,
                "onchain": Dict
            },
            "risk_score": float,
            "risk_level": str,
            "risk_details": Dict,
            "summary": Dict
        }
        
    Raises:
        Exception: If any critical error occurs during the audit process
    """
    audit_start = datetime.utcnow()
    logger.info(
        "Starting token audit process",
        context={
            "token_address": token_address,
            "lp_token_address": lp_token_address,
            "start_time": audit_start.isoformat()
        }
    )
    
    # Initialize response structure
    response = {
        "token_address": token_address,
        "lp_token_address": lp_token_address,
        "audit_timestamp": audit_start.isoformat(),
        "analysis": {}
    }
    
    try:
        # 0. Fetch Token Metadata
        logger.info("Starting metadata fetch")
        try:
            metadata = fetch_token_metadata(token_address)
            logger.info(
                "Successfully fetched token metadata",
                context={
                    "name": metadata.get("name"),
                    "symbol": metadata.get("symbol"),
                    "decimals": metadata.get("decimals"),
                    "total_supply": metadata.get("total_supply")
                }
            )
            
            # Store metadata in response
            response.update({
                "token_name": metadata.get("name"),
                "token_symbol": metadata.get("symbol"),
                "token_decimals": metadata.get("decimals"),
                "total_supply": metadata.get("total_supply")
            })
            
        except Exception as e:
            error_msg = f"Failed to fetch token metadata: {str(e)}"
            logger.critical(
                error_msg,
                context={"token_address": token_address},
                exc_info=True
            )
            raise Exception(f"❌ {error_msg}") from e
        
        # 1. Static Analysis
        logger.info("Starting static analysis")
        try:
            source_code = metadata.get("source_code", "")
            source_code_length = len(source_code) if source_code else 0
            
            logger.debug(
                "Analyzing token source code",
                context={
                    "source_code_length": source_code_length,
                    "has_source_code": bool(source_code)
                }
            )
            
            static_result = analyze_static(source_code)
            alerts = static_result.get("alerts", [])
            alert_count = len(alerts)
            
            # Categorize alerts by severity
            severity_counts = {}
            for alert in alerts:
                severity = alert.get("severity", "unknown")
                severity_counts[severity] = severity_counts.get(severity, 0) + 1
            
            logger.info(
                "Static analysis completed",
                context={
                    "total_alerts": alert_count,
                    "severity_counts": severity_counts,
                    "has_critical_issues": any(a.get("severity") == "critical" for a in alerts)
                }
            )
            
            response["analysis"]["static"] = static_result
            
        except Exception as e:
            error_msg = f"Static analysis failed: {str(e)}"
            logger.error(
                error_msg,
                context={"token_address": token_address},
                exc_info=True
            )
            response["analysis"]["static"] = {
                "error": error_msg,
                "alerts": []
            }
        
        # 2. Dynamic Analysis (if simulation data is available)
        if "simulation" in metadata:
            logger.info("Starting dynamic analysis")
            try:
                simulation_data = metadata["simulation"]
                logger.debug(
                    "Processing simulation data for dynamic analysis",
                    context={
                        "simulation_type": type(simulation_data).__name__,
                        "simulation_keys": list(simulation_data.keys()) if hasattr(simulation_data, 'keys') else "N/A"
                    }
                )
                
                dynamic_result = analyze_dynamic(simulation_data)
                
                # Log key metrics from dynamic analysis
                logger.info(
                    "Dynamic analysis completed",
                    context={
                        "is_honeypot": dynamic_result.get("is_honeypot", False),
                        "buy_tax": dynamic_result.get("buy_tax", 0),
                        "sell_tax": dynamic_result.get("sell_tax", 0),
                        "simulation_successful": dynamic_result.get("simulation_successful", False),
                        "execution_reverted": dynamic_result.get("execution_reverted", False),
                        "error_message": dynamic_result.get("error_message", "None")
                    }
                )
                
                response["analysis"]["dynamic"] = dynamic_result
                
            except Exception as e:
                error_msg = f"Dynamic analysis failed: {str(e)}"
                logger.error(
                    error_msg,
                    context={"token_address": token_address},
                    exc_info=True
                )
                response["analysis"]["dynamic"] = {
                    "error": error_msg,
                    "is_honeypot": False,
                    "buy_tax": 0,
                    "sell_tax": 0
                }
        else:
            logger.warning(
                "Skipping dynamic analysis - no simulation data available",
                context={"token_address": token_address}
            )
            response["analysis"]["dynamic"] = {
                "error": "No simulation data available",
                "is_honeypot": False,
                "buy_tax": 0,
                "sell_tax": 0
            }
        
        # 3. On-chain Analysis
        logger.info("Starting on-chain analysis")
        try:
            logger.debug(
                "Preparing for on-chain analysis",
                context={
                    "token_address": token_address,
                    "has_metadata": bool(metadata)
                }
            )
            
            onchain_result = analyze_onchain(metadata)
            alerts = onchain_result.get("alerts", [])
            alert_count = len(alerts)
            
            # Log key metrics from on-chain analysis
            logger.info(
                "On-chain analysis completed",
                context={
                    "total_alerts": alert_count,
                    "top_holder_concentration": onchain_result.get("top_holder_concentration"),
                    "liquidity_pool_exists": onchain_result.get("liquidity_pool_exists", False),
                    "contract_verified": onchain_result.get("contract_verified", False),
                    "token_age_days": onchain_result.get("token_age_days", 0)
                }
            )
            
            response["analysis"]["onchain"] = onchain_result
            
        except Exception as e:
            error_msg = f"On-chain analysis failed: {str(e)}"
            logger.error(
                error_msg,
                context={"token_address": token_address},
                exc_info=True
            )
            response["analysis"]["onchain"] = {
                "error": error_msg,
                "alerts": [],
                "top_holder_concentration": 0,
                "liquidity_pool_exists": False,
                "contract_verified": False,
                "token_age_days": 0
            }
        
        # 4. Calculate Risk Score
        logger.info("Calculating risk score")
        try:
            logger.debug(
                "Gathering analysis results for risk calculation",
                context={
                    "static_alerts": len(static_result.get("alerts", [])),
                    "has_dynamic_analysis": bool(response["analysis"].get("dynamic")),
                    "onchain_alerts": len(onchain_result.get("alerts", []))
                }
            )
            
            risk_result = calculate_risk_score(
                static_result, 
                response["analysis"].get("dynamic", {}),
                onchain_result
            )
            
            # Store risk assessment results
            risk_score = risk_result.get("score", 0)
            risk_level = risk_result.get("grade", "F")
            
            response.update({
                "risk_score": risk_score,
                "risk_level": risk_level,
                "risk_details": {
                    "alerts": risk_result.get("alerts", []),
                    "warnings": risk_result.get("warnings", []),
                    "risks": risk_result.get("risks", []),
                    "score_breakdown": risk_result.get("score_breakdown", {})
                }
            })
            
            logger.info(
                "Risk assessment completed",
                context={
                    "score": risk_score,
                    "level": risk_level,
                    "alerts_count": len(risk_result.get("alerts", [])),
                    "warnings_count": len(risk_result.get("warnings", [])),
                    "risks_count": len(risk_result.get("risks", []))
                }
            )
            
        except Exception as e:
            error_msg = f"Risk calculation failed: {str(e)}"
            logger.error(
                error_msg,
                context={"token_address": token_address},
                exc_info=True
            )
            # Set default risk values
            response.update({
                "risk_score": 0,
                "risk_level": "F",
                "risk_details": {
                    "error": error_msg,
                    "alerts": [],
                    "warnings": [],
                    "risks": [],
                    "score_breakdown": {}
                }
            })
        
        # 5. Generate Summary
        logger.debug("Generating audit summary")
        try:
            # Calculate total alerts across all analysis types
            total_alerts = sum(
                len(analysis.get("alerts", [])) 
                for analysis in response["analysis"].values()
                if isinstance(analysis, dict)
            )
            
            # Check for critical issues
            has_critical_issues = any(
                alert.get("severity") == "critical"
                for analysis in response["analysis"].values()
                if isinstance(analysis, dict)
                for alert in analysis.get("alerts", [])
            )
            
            # Calculate audit duration
            audit_duration = (datetime.utcnow() - audit_start).total_seconds()
            
            response["summary"] = {
                "has_critical_issues": has_critical_issues,
                "total_alerts": total_alerts,
                "audit_duration_seconds": audit_duration,
                "analysis_types_completed": [
                    analysis_type 
                    for analysis_type, result in response["analysis"].items()
                    if isinstance(result, dict)
                ]
            }
            
            logger.info(
                "Audit summary generated",
                context={
                    "has_critical_issues": has_critical_issues,
                    "total_alerts": total_alerts,
                    "audit_duration_seconds": round(audit_duration, 2)
                }
            )
            
        except Exception as e:
            error_msg = f"Error generating audit summary: {str(e)}"
            logger.error(
                error_msg,
                context={"token_address": token_address},
                exc_info=True
            )
            response["summary"] = {
                "error": error_msg,
                "has_critical_issues": True,
                "total_alerts": 0,
                "audit_duration_seconds": (datetime.utcnow() - audit_start).total_seconds()
            }
        
        # Final audit completion log
        audit_duration = response["summary"]["audit_duration_seconds"]
        logger.info(
            "Token audit completed successfully",
            context={
                "token": f"{response.get('token_name')} ({response.get('token_symbol')})",
                "token_address": token_address,
                "risk_score": response.get("risk_score"),
                "risk_level": response.get("risk_level"),
                "total_alerts": response["summary"].get("total_alerts", 0),
                "has_critical_issues": response["summary"].get("has_critical_issues", True),
                "duration_seconds": round(audit_duration, 2),
                "timestamp": datetime.utcnow().isoformat()
            }
        )
        
        return response
        
    except Exception as e:
        audit_duration = (datetime.utcnow() - audit_start).total_seconds()
        error_msg = f"Critical error during token audit: {str(e)}"
        
        logger.critical(
            "Token audit failed",
            context={
                "token_address": token_address,
                "error_type": type(e).__name__,
                "error_message": str(e),
                "duration_seconds": round(audit_duration, 2),
                "traceback": traceback.format_exc()
            },
            exc_info=True
        )
        
        # Return error response with as much info as possible
        error_response = {
            "token_address": token_address,
            "error": error_msg,
            "error_type": type(e).__name__,
            "audit_timestamp": datetime.utcnow().isoformat(),
            "audit_duration_seconds": audit_duration,
            "analysis": {}
        }
        
        # Include any partial analysis results if available
        if 'analysis' in locals():
            error_response["analysis"] = locals().get('analysis', {})
        
        return error_response
