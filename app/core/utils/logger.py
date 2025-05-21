import logging
import logging.handlers
import sys
from typing import Optional, Dict, Any
from colorama import init as init_colorama

# Inicializa o colorama para suporte a cores no Windows
init_colorama()

class ColoredFormatter(logging.Formatter):
    """Custom formatter that adds colors to log messages."""
    
    # Cores ANSI
    COLORS = {
        'DEBUG': '\033[36m',     # Ciano
        'INFO': '\033[32m',      # Verde
        'WARNING': '\033[33m',   # Amarelo
        'ERROR': '\033[31m',     # Vermelho
        'CRITICAL': '\033[1;31m', # Vermelho brilhante
        'RESET': '\033[0m'       # Resetar cor
    }
    
    def format(self, record):
        # Aplica cor ao nível de log
        levelname = record.levelname
        color = self.COLORS.get(levelname, '')
        reset = self.COLORS['RESET']
        
        # Formata a mensagem com cor
        record.msg = f"{color}{record.msg}{reset}"
        
        # Se for um erro ou crítico, formata o traceback também
        if levelname in ['ERROR', 'CRITICAL'] and record.exc_info:
            record.exc_text = f"{color}{super().formatException(record.exc_info)}{reset}"
        
        return super().format(record)

class CustomLogger:
    """Wrapper around Python's logging module with some convenience methods."""
    
    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
        # Add level attribute for compatibility
        self.level = self.logger.level
        
    @property
    def level(self):
        """Get the current log level."""
        return self.logger.level
        
    @level.setter
    def level(self, value):
        """Set the log level."""
        self.logger.setLevel(value)
    
    def debug(self, message: str, context: Optional[Dict[str, Any]] = None, exc_info=None):
        """Log a debug message."""
        self._log(logging.DEBUG, message, context, exc_info=exc_info)
    
    def info(self, message: str, context: Optional[Dict[str, Any]] = None, exc_info=None):
        """Log an info message."""
        self._log(logging.INFO, message, context, exc_info=exc_info)
    
    def warning(self, message: str, context: Optional[Dict[str, Any]] = None, exc_info=None):
        """Log a warning message."""
        self._log(logging.WARNING, message, context, exc_info=exc_info)
    
    def error(self, message: str, context: Optional[Dict[str, Any]] = None, exc_info=None):
        """Log an error message with optional exception info."""
        self._log(logging.ERROR, message, context, exc_info=exc_info)
    
    def critical(self, message: str, context: Optional[Dict[str, Any]] = None, exc_info=None):
        """Log a critical message with optional exception info."""
        self._log(logging.CRITICAL, message, context, exc_info=exc_info)
    
    def _log(self, level: int, message: str, context: Optional[Dict[str, Any]] = None, **kwargs):
        """Internal method to handle logging with context."""
        # Extract exc_info from kwargs if it exists
        exc_info = kwargs.pop('exc_info', None)
        
        # Format the message with context if provided
        if context:
            context_str = " ".join(f"{k}={v}" for k, v in context.items())
            message = f"{message} | {context_str}" if message else context_str
        
        # If there's exc_info, add it back to kwargs
        if exc_info is not None:
            kwargs['exc_info'] = exc_info
        
        # Remove context from kwargs to avoid errors
        kwargs.pop('context', None)
        
        # Log the message
        self.logger.log(level, message, **kwargs)

def setup_logging(level=logging.INFO):
    """Configure application logging."""
    try:
        # Convert string level to logging level if needed
        if isinstance(level, str):
            level = getattr(logging, level.upper(), logging.INFO)
        
        # Configure root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(level)
        
        # Remove existing handlers to avoid duplication
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)
        
        # Create console handler with colored output
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level)
        
        # Define log format with colors
        console_formatter = ColoredFormatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        console_handler.setFormatter(console_formatter)
        
        # Create file handler for persistent logging
        import os
        from pathlib import Path
        
        # Ensure logs directory exists
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        # Create rotating file handler
        file_handler = logging.handlers.RotatingFileHandler(
            filename=log_dir / "app.log",
            maxBytes=10 * 1024 * 1024,  # 10 MB
            backupCount=5,
            encoding="utf-8"
        )
        file_handler.setLevel(level)
        
        # Use a standard formatter for file logs (no colors)
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s - %(filename)s:%(lineno)d',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_formatter)
        
        # Add handlers to root logger
        root_logger.addHandler(console_handler)
        root_logger.addHandler(file_handler)
        
        # Configure third-party loggers
        logging.getLogger('uvicorn').setLevel(logging.WARNING)
        logging.getLogger('uvicorn.error').setLevel(logging.WARNING)
        logging.getLogger('uvicorn.access').disabled = True
        logging.getLogger('fastapi').setLevel(logging.WARNING)
        
        # Enable debug logging for our application
        app_logger = logging.getLogger('app')
        app_logger.setLevel(level)
        app_logger.propagate = True
        
        # Create a test log message to verify logging is working
        test_logger = logging.getLogger('app.test')
        test_logger.debug("Debug test message")
        test_logger.info("Info test message")
        test_logger.warning("Warning test message")
        test_logger.error("Error test message")
        
        # Get logger for this module
        logger = get_logger(__name__)
        logger.info("Logging configured successfully", context={"log_level": logging.getLevelName(level)})
        
        return logger
    except Exception as e:
        # Fallback to basic logging if our custom setup fails
        logging.basicConfig(level=level, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        logging.error(f"Failed to configure custom logging: {str(e)}")
        return logging.getLogger(__name__)

def get_logger(name: str) -> 'CustomLogger':
    """Get a logger instance with the given name."""
    return CustomLogger(name)
