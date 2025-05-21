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
        dynamic_alerts = {}
        try:
            dynamic_alerts = analyze_dynamic(source)
        except Exception as e:
            logger.warning("Dynamic analysis skipped due to error", context={"error": str(e), "token_address": token_address})
            dynamic_alerts = {
                "honeypot": {
                    "is_honeypot": False,
                    "buy_success": None,
                    "sell_success": None,
                    "high_tax": None,
                    "tax_discrepancy": None,
                    "error": str(e)
                },
                "fees": {
                    "buy": 0.0,
                    "sell": 0.0,
                    "buy_slippage": 0.0,
                    "sell_slippage": 0.0,
                    "buy_mutable": False,
                    "sell_mutable": False
                }
            }
        
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
        risk_score = calculate_risk_score(static_results, dynamic_alerts, onchain_results)
        
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
                "dynamic": dynamic_alerts,
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
