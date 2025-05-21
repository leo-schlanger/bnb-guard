"""
Script para depurar problemas de logging na aplicação.
"""
import os
import logging
import sys
from pathlib import Path

# Adicionar diretório raiz ao path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Configurar logging básico para depuração
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)

# Logger para este script
logger = logging.getLogger("debug_logs")

def check_log_files():
    """Verificar arquivos de log existentes."""
    logger.info("Verificando arquivos de log...")
    
    # Verificar diretório de logs
    log_dir = Path("logs")
    if not log_dir.exists():
        logger.warning(f"Diretório de logs não existe: {log_dir.absolute()}")
        logger.info("Criando diretório de logs...")
        log_dir.mkdir(exist_ok=True)
    else:
        logger.info(f"Diretório de logs encontrado: {log_dir.absolute()}")
    
    # Listar arquivos de log
    log_files = list(log_dir.glob("*.log"))
    logger.info(f"Encontrados {len(log_files)} arquivos de log:")
    for log_file in log_files:
        file_size = log_file.stat().st_size
        logger.info(f"  - {log_file.name} ({file_size} bytes)")
        
        # Verificar conteúdo do arquivo
        if file_size > 0:
            with open(log_file, "r") as f:
                lines = f.readlines()
                logger.info(f"    Contém {len(lines)} linhas")
                
                # Mostrar primeiras e últimas linhas
                if len(lines) > 0:
                    logger.info(f"    Primeira linha: {lines[0].strip()}")
                    logger.info(f"    Última linha: {lines[-1].strip()}")
                    
                    # Verificar linhas relacionadas à análise
                    analyze_lines = [line for line in lines if "analyze" in line.lower()]
                    logger.info(f"    Linhas contendo 'analyze': {len(analyze_lines)}")
                    
                    if analyze_lines:
                        logger.info(f"    Primeira linha de análise: {analyze_lines[0].strip()}")
                        logger.info(f"    Última linha de análise: {analyze_lines[-1].strip()}")

def check_logger_config():
    """Verificar configuração do logger."""
    logger.info("Verificando configuração do logger...")
    
    # Verificar loggers configurados
    root_logger = logging.getLogger()
    logger.info(f"Logger raiz: nível={logging.getLevelName(root_logger.level)}")
    
    # Verificar handlers
    logger.info(f"Handlers do logger raiz: {len(root_logger.handlers)}")
    for i, handler in enumerate(root_logger.handlers):
        logger.info(f"  - Handler {i+1}: {type(handler).__name__}")
        if hasattr(handler, 'baseFilename'):
            logger.info(f"    Arquivo: {handler.baseFilename}")
        if hasattr(handler, 'level'):
            logger.info(f"    Nível: {logging.getLevelName(handler.level)}")
    
    # Verificar loggers específicos
    app_logger = logging.getLogger("app")
    logger.info(f"Logger 'app': nível={logging.getLevelName(app_logger.level)}")
    
    analyze_logger = logging.getLogger("app.routes.analyze")
    logger.info(f"Logger 'app.routes.analyze': nível={logging.getLevelName(analyze_logger.level)}")
    
    # Testar logging
    logger.info("Testando mensagens de log em diferentes loggers...")
    
    test_logger = logging.getLogger("app.test")
    test_logger.debug("Esta é uma mensagem de DEBUG de teste")
    test_logger.info("Esta é uma mensagem de INFO de teste")
    test_logger.warning("Esta é uma mensagem de WARNING de teste")
    test_logger.error("Esta é uma mensagem de ERROR de teste")
    
    analyze_logger.debug("Esta é uma mensagem de DEBUG de teste para analyze")
    analyze_logger.info("Esta é uma mensagem de INFO de teste para analyze")
    analyze_logger.warning("Esta é uma mensagem de WARNING de teste para analyze")
    analyze_logger.error("Esta é uma mensagem de ERROR de teste para analyze")

def check_env_vars():
    """Verificar variáveis de ambiente relacionadas ao logging."""
    logger.info("Verificando variáveis de ambiente...")
    
    log_level = os.getenv("LOG_LEVEL")
    logger.info(f"LOG_LEVEL: {log_level}")
    
    # Outras variáveis relevantes
    env = os.getenv("ENV")
    logger.info(f"ENV: {env}")
    
    debug = os.getenv("DEBUG")
    logger.info(f"DEBUG: {debug}")

def main():
    """Função principal."""
    logger.info("Iniciando depuração de logs...")
    
    check_env_vars()
    check_log_files()
    check_logger_config()
    
    logger.info("Depuração de logs concluída!")

if __name__ == "__main__":
    main()
