import os
import sys
import traceback
import uuid
from typing import Dict, Any, Optional, Tuple
from datetime import datetime

# Add project root to path
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
sys.path.insert(0, root_dir)

# Import logger first
from app.core.utils.logger import get_logger

# Initialize logger
logger = get_logger(__name__)

# Generate a unique audit ID for this session
audit_id = f"audit_{uuid.uuid4().hex[:8]}"

def _import_required_modules():
    """
    Imports all required modules for the audit process.
    
    Raises:
        ImportError: If any required module cannot be imported
    """
    MODULES = {
        'fetch_token_metadata': 'app.core.utils.metadata',
        'analyze_static': 'app.core.analyzers.static_analyzer',
        'analyze_dynamic': 'app.core.analyzers.dynamic_analyzer',
        'analyze_onchain': 'app.core.analyzers.onchain_analyzer',
        'calculate_risk_score': 'app.core.utils.scoring',
        'AnalysisResult': 'app.core.interfaces.analyzer'
    }
    
    failed_imports = []
    
    logger.info(
        "Importing required modules",
        context={"total_modules": len(MODULES)}
    )
    
    for name, module_path in MODULES.items():
        try:
            if '.' in module_path:
                from importlib import import_module
                module = import_module(module_path)
                globals()[name] = getattr(module, name.split('.')[-1])
            else:
                exec(f'from {module_path} import {name}')
                
            logger.debug(
                f"Successfully imported module: {name}",
                context={"module": module_path}
            )
                
        except ImportError as e:
            logger.error(
                f"Failed to import module: {name}",
                context={
                    "module": module_path,
                    "error": str(e)
                },
                exc_info=True
            )
            failed_imports.append((name, module_path, str(e)))
    
    if failed_imports:
        error_msg = "Failed to import required modules:\n"
        for name, path, error in failed_imports:
            error_msg += f"- {name} ({path}): {error}\n"
            
        logger.critical(
            "Required modules not found",
            context={
                "failed_modules": [{"name": name, "module": path} for name, path, _ in failed_imports],
                "errors": [error for _, _, error in failed_imports]
            }
        )
        raise ImportError(error_msg)
    
    logger.info(
        "All modules imported successfully",
        context={"total_modules": len(MODULES)}
    )

# Import required modules
_import_required_modules()

async def audit_token(token_address: str, lp_token_address: Optional[str] = None) -> Dict[str, Any]:
    """
    Performs a comprehensive audit of a token contract.
    
    This function orchestrates the entire audit process, including:
    - Token metadata fetching
    - Static code analysis
    - Dynamic behavior analysis
    - On-chain analysis
    - Risk score calculation
    
    Args:
        token_address: Address of the token contract to audit
        lp_token_address: Optional liquidity pool token address
        
    Returns:
        Dictionary containing the audit results
    """
    start_time = datetime.utcnow()
    request_id = f"{audit_id}_{start_time.strftime('%Y%m%d_%H%M%S')}"
    
    logger.info(
        "Iniciando auditoria de token",
        context={
            "request_id": request_id,
            "token_address": token_address,
            "lp_token_address": lp_token_address
        }
    )
    
    try:
        # 1. Buscar metadados do token
        logger.debug(
            "Buscando metadados do token",
            context={"request_id": request_id}
        )
        metadata = fetch_token_metadata(token_address)
        
        # 2. Executar análise estática
        logger.debug(
            "Executando análise estática",
            context={"request_id": request_id}
        )
        static_results = analyze_static(metadata)
        
        # 3. Executar análise dinâmica
        logger.debug(
            "Executando análise dinâmica",
            context={"request_id": request_id}
        )
        dynamic_results = analyze_dynamic(metadata)
        
        # 4. Executar análise on-chain
        logger.debug(
            "Executando análise on-chain",
            context={
                "request_id": request_id,
                "has_lp_token": lp_token_address is not None
            }
        )
        onchain_results = analyze_onchain(token_address, lp_token_address)
        
        # 5. Calcular pontuação de risco
        logger.debug(
            "Calculando pontuação de risco",
            context={"request_id": request_id}
        )
        risk_score = calculate_risk_score(static_results, dynamic_results, onchain_results)
        
        # 6. Preparar resultados finais
        end_time = datetime.utcnow()
        duration = (end_time - start_time).total_seconds()
        
        results = {
            "audit_id": request_id,
            "token_address": token_address,
            "lp_token_address": lp_token_address,
            "timestamp": start_time.isoformat(),
            "duration_seconds": duration,
            "status": "completed",
            "risk_score": risk_score,
            "analysis": {
                "static": static_results,
                "dynamic": dynamic_results,
                "onchain": onchain_results
            }
        }
        
        logger.info(
            "Auditoria concluída com sucesso",
            context={
                "request_id": request_id,
                "token_address": token_address,
                "duracao_segundos": duration,
                "pontuacao_risco": risk_score.get("score"),
                "nivel_risco": risk_score.get("level")
            }
        )
        
        return results
        
    except Exception as e:
        error_id = f"err_{uuid.uuid4().hex[:8]}"
        error_msg = f"Erro durante a auditoria: {str(e)}"
        stack_trace = traceback.format_exc()
        
        logger.critical(
            error_msg,
            context={
                "request_id": request_id,
                "error_id": error_id,
                "tipo_erro": e.__class__.__name__,
                "mensagem": str(e),
                "token_address": token_address
            },
            exc_info=True
        )
        
        return {
            "audit_id": request_id,
            "token_address": token_address,
            "lp_token_address": lp_token_address,
            "timestamp": datetime.utcnow().isoformat(),
            "status": "erro",
            "erro": {
                "id": error_id,
                "tipo": e.__class__.__name__,
                "mensagem": str(e)
            }
        }
        
        # 4. Calculate Risk Score
        logger.info("Calculating risk score", context={"request_id": request_id})
        try:
            # Get analysis results
            analysis_results = {
                "static": static_results,
                "dynamic": dynamic_results,
                "onchain": onchain_results
            }
            
            logger.debug(
                "Gathering analysis results for risk calculation",
                context={
                    "request_id": request_id,
                    "static_alerts": len(static_results.get("alerts", [])),
                    "has_dynamic_analysis": bool(dynamic_results),
                    "onchain_alerts": len(onchain_results.get("alerts", []))
                }
            )
            
            risk_result = calculate_risk_score(
                static_results, 
                dynamic_results,
                onchain_results
            )
            
            # Store risk assessment results
            risk_score = risk_result.get("score", 0)
            risk_level = risk_result.get("grade", "F")
            
            results.update({
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
                    "request_id": request_id,
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
                context={
                    "request_id": request_id,
                    "token_address": token_address
                },
                exc_info=True
            )
            # Set default risk values
            results.update({
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
        logger.debug("Generating audit summary", context={"request_id": request_id})
        try:
            # Calculate total alerts across all analysis types
            total_alerts = sum(
                len(analysis.get("alerts", [])) 
                for analysis in results["analysis"].values()
                if isinstance(analysis, dict)
            )
            
            # Check for critical issues
            has_critical_issues = any(
                alert.get("severity") == "critical"
                for analysis in results["analysis"].values()
                if isinstance(analysis, dict)
                for alert in analysis.get("alerts", [])
            )
            
            # Calculate audit duration
            audit_duration = (datetime.utcnow() - start_time).total_seconds()
            
            results["summary"] = {
                "has_critical_issues": has_critical_issues,
                "total_alerts": total_alerts,
                "audit_duration_seconds": audit_duration,
                "analysis_types_completed": [
                    analysis_type 
                    for analysis_type, result in results["analysis"].items()
                    if isinstance(result, dict)
                ]
            }
            
            logger.info(
                "Audit summary generated",
                context={
                    "request_id": request_id,
                    "has_critical_issues": has_critical_issues,
                    "total_alerts": total_alerts,
                    "audit_duration_seconds": round(audit_duration, 2)
                }
            )
            
        except Exception as e:
            error_msg = f"Error generating audit summary: {str(e)}"
            logger.error(
                error_msg,
                context={
                    "request_id": request_id,
                    "token_address": token_address
                },
                exc_info=True
            )
            results["summary"] = {
                "error": error_msg,
                "has_critical_issues": True,
                "total_alerts": 0,
                "audit_duration_seconds": (datetime.utcnow() - start_time).total_seconds()
            }
        
        # Final audit completion log
        audit_duration = results["summary"]["audit_duration_seconds"]
        logger.info(
            "Token audit completed successfully",
            context={
                "request_id": request_id,
                "token_address": token_address,
                "risk_score": results.get("risk_score"),
                "risk_level": results.get("risk_level"),
                "total_alerts": results["summary"].get("total_alerts", 0),
                "has_critical_issues": results["summary"].get("has_critical_issues", True),
                "duration_seconds": round(audit_duration, 2),
                "timestamp": datetime.utcnow().isoformat()
            }
        )
        
        return results
        
    except Exception as e:
        audit_duration = (datetime.utcnow() - start_time).total_seconds()
        error_id = f"err_{uuid.uuid4().hex[:8]}"
        error_msg = f"Critical error during token audit: {str(e)}"
        
        logger.critical(
            "Token audit failed",
            context={
                "request_id": request_id,
                "error_id": error_id,
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
            "audit_id": request_id,
            "token_address": token_address,
            "lp_token_address": lp_token_address,
            "timestamp": datetime.utcnow().isoformat(),
            "status": "error",
            "error": {
                "id": error_id,
                "type": type(e).__name__,
                "message": str(e),
                "traceback": traceback.format_exc()
            },
            "audit_duration_seconds": audit_duration
        }
        
        # Include any partial analysis results if available
        if 'results' in locals():
            error_response["analysis"] = results.get("analysis", {})
        
        return error_response
