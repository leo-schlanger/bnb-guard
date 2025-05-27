import logging
import logging.handlers
import sys
import json
from datetime import datetime
from typing import Optional, Dict, Any, Union
from colorama import init as init_colorama, Fore, Style, Back

# Inicializa o colorama para suporte a cores no Windows
init_colorama()

class EnhancedFormatter(logging.Formatter):
    """Enhanced formatter with better readability and structured output."""
    
    # Cores e estilos melhorados
    LEVEL_COLORS = {
        'DEBUG': Fore.CYAN + Style.DIM,
        'INFO': Fore.GREEN,
        'WARNING': Fore.YELLOW + Style.BRIGHT,
        'ERROR': Fore.RED + Style.BRIGHT,
        'CRITICAL': Fore.WHITE + Back.RED + Style.BRIGHT,
    }
    
    # Emojis para diferentes tipos de log
    LEVEL_ICONS = {
        'DEBUG': '🔍',
        'INFO': '📝',
        'WARNING': '⚠️',
        'ERROR': '❌',
        'CRITICAL': '🚨',
    }
    
    def __init__(self, use_colors=True, use_icons=True, compact=False):
        self.use_colors = use_colors
        self.use_icons = use_icons
        self.compact = compact
        super().__init__()
    
    def format(self, record):
        # Extrair informações do record
        timestamp = datetime.fromtimestamp(record.created).strftime('%H:%M:%S.%f')[:-3]
        level = record.levelname
        name = record.name
        message = record.getMessage()
        
        # Aplicar cores se habilitado
        if self.use_colors:
            level_color = self.LEVEL_COLORS.get(level, '')
            reset = Style.RESET_ALL
        else:
            level_color = ''
            reset = ''
        
        # Aplicar ícones se habilitado
        icon = self.LEVEL_ICONS.get(level, '') if self.use_icons else ''
        
        # Formatação compacta ou detalhada
        if self.compact:
            # Formato compacto para console
            if icon:
                formatted = f"{level_color}{icon} {timestamp} {level:8} {name:25} | {message}{reset}"
            else:
                formatted = f"{level_color}{timestamp} {level:8} {name:25} | {message}{reset}"
        else:
            # Formato detalhado para arquivo
            formatted = f"{timestamp} - {level:8} - {name:30} - {message}"
            
            # Adicionar informações extras se disponíveis
            if hasattr(record, 'filename') and hasattr(record, 'lineno'):
                formatted += f" [{record.filename}:{record.lineno}]"
        
        # Adicionar traceback se for erro
        if record.exc_info and not self.compact:
            exc_text = self.formatException(record.exc_info)
            if self.use_colors:
                exc_text = f"{Fore.RED}{exc_text}{Style.RESET_ALL}"
            formatted += f"\n{exc_text}"
        
        return formatted

class StructuredLogger:
    """Enhanced logger with structured logging capabilities."""
    
    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
        self.name = name
        
    @property
    def level(self):
        """Get the current log level."""
        return self.logger.level
        
    @level.setter
    def level(self, value):
        """Set the log level."""
        if isinstance(value, str):
            value = getattr(logging, value.upper(), logging.INFO)
        self.logger.setLevel(value)
    
    def _format_context(self, context: Optional[Dict[str, Any]]) -> str:
        """Format context dictionary into a readable string."""
        if not context:
            return ""
        
        formatted_items = []
        for key, value in context.items():
            # Truncar valores muito longos
            if isinstance(value, str) and len(value) > 50:
                value = value[:47] + "..."
            elif isinstance(value, (dict, list)):
                value = json.dumps(value, default=str)[:50] + "..." if len(str(value)) > 50 else json.dumps(value, default=str)
            
            formatted_items.append(f"{key}={value}")
        
        return " | ".join(formatted_items)
    
    def debug(self, message: str, context: Optional[Dict[str, Any]] = None, **kwargs):
        """Log a debug message."""
        self._log(logging.DEBUG, message, context, **kwargs)
    
    def info(self, message: str, context: Optional[Dict[str, Any]] = None, **kwargs):
        """Log an info message."""
        self._log(logging.INFO, message, context, **kwargs)
    
    def warning(self, message: str, context: Optional[Dict[str, Any]] = None, **kwargs):
        """Log a warning message."""
        self._log(logging.WARNING, message, context, **kwargs)
    
    def error(self, message: str, context: Optional[Dict[str, Any]] = None, **kwargs):
        """Log an error message."""
        self._log(logging.ERROR, message, context, **kwargs)
    
    def critical(self, message: str, context: Optional[Dict[str, Any]] = None, **kwargs):
        """Log a critical message."""
        self._log(logging.CRITICAL, message, context, **kwargs)
    
    def success(self, message: str, context: Optional[Dict[str, Any]] = None, **kwargs):
        """Log a success message (info level with success context)."""
        if context is None:
            context = {}
        context['status'] = 'success'
        self._log(logging.INFO, f"✅ {message}", context, **kwargs)
    
    def failure(self, message: str, context: Optional[Dict[str, Any]] = None, **kwargs):
        """Log a failure message (error level with failure context)."""
        if context is None:
            context = {}
        context['status'] = 'failure'
        self._log(logging.ERROR, f"❌ {message}", context, **kwargs)
    
    def performance(self, message: str, duration: float, context: Optional[Dict[str, Any]] = None, **kwargs):
        """Log a performance message with duration."""
        if context is None:
            context = {}
        context['duration_ms'] = round(duration * 1000, 2)
        
        # Escolher emoji baseado na duração
        if duration < 0.1:
            emoji = "⚡"
        elif duration < 1.0:
            emoji = "🚀"
        elif duration < 5.0:
            emoji = "⏱️"
        else:
            emoji = "🐌"
        
        self._log(logging.INFO, f"{emoji} {message}", context, **kwargs)
    
    def api_request(self, method: str, url: str, status_code: int, duration: float, 
                   client_ip: str = None, **kwargs):
        """Log an API request with structured information."""
        context = {
            'method': method,
            'url': url,
            'status_code': status_code,
            'duration_ms': round(duration * 1000, 2),
        }
        
        if client_ip:
            context['client_ip'] = client_ip
        
        # Escolher emoji baseado no status code
        if 200 <= status_code < 300:
            emoji = "✅"
            level = logging.INFO
        elif 300 <= status_code < 400:
            emoji = "↩️"
            level = logging.INFO
        elif 400 <= status_code < 500:
            emoji = "⚠️"
            level = logging.WARNING
        else:
            emoji = "❌"
            level = logging.ERROR
        
        message = f"{emoji} {method} {url} → {status_code}"
        self._log(level, message, context, **kwargs)
    
    def blockchain_operation(self, operation: str, token_address: str = None, 
                           success: bool = True, context: Optional[Dict[str, Any]] = None, **kwargs):
        """Log blockchain operations with specific formatting."""
        if context is None:
            context = {}
        
        if token_address:
            context['token_address'] = token_address
        
        emoji = "⛓️" if success else "💥"
        level = logging.INFO if success else logging.ERROR
        
        self._log(level, f"{emoji} {operation}", context, **kwargs)
    
    def _log(self, level: int, message: str, context: Optional[Dict[str, Any]] = None, **kwargs):
        """Internal method to handle logging with context."""
        # Formatar contexto
        if context:
            context_str = self._format_context(context)
            if context_str:
                message = f"{message} | {context_str}"
        
        # Log the message
        self.logger.log(level, message, **kwargs)

def setup_logging(level: Union[str, int] = logging.INFO, 
                 enable_file_logging: bool = True,
                 enable_colors: bool = True,
                 enable_icons: bool = True) -> StructuredLogger:
    """Configure enhanced application logging."""
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
        
        # Create console handler with enhanced formatting
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level)
        
        console_formatter = EnhancedFormatter(
            use_colors=enable_colors,
            use_icons=enable_icons,
            compact=True
        )
        console_handler.setFormatter(console_formatter)
        
        # Add console handler
        root_logger.addHandler(console_handler)
        
        # Create file handler if enabled
        if enable_file_logging:
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
            
            # Use detailed formatter for file logs (no colors/icons)
            file_formatter = EnhancedFormatter(
                use_colors=False,
                use_icons=False,
                compact=False
            )
            file_handler.setFormatter(file_formatter)
            
            root_logger.addHandler(file_handler)
        
        # Configure third-party loggers to be less verbose
        logging.getLogger('uvicorn').setLevel(logging.WARNING)
        logging.getLogger('uvicorn.error').setLevel(logging.WARNING)
        logging.getLogger('uvicorn.access').disabled = True
        logging.getLogger('fastapi').setLevel(logging.WARNING)
        logging.getLogger('httpx').setLevel(logging.WARNING)
        logging.getLogger('urllib3').setLevel(logging.WARNING)
        
        # Enable debug logging for our application
        app_logger = logging.getLogger('app')
        app_logger.setLevel(level)
        app_logger.propagate = True
        
        # Get logger for this module and log success
        logger = get_logger(__name__)
        logger.success("Enhanced logging system initialized", {
            "log_level": logging.getLevelName(level),
            "file_logging": enable_file_logging,
            "colors": enable_colors,
            "icons": enable_icons
        })
        
        return logger
        
    except Exception as e:
        # Fallback to basic logging if our custom setup fails
        logging.basicConfig(
            level=level, 
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%H:%M:%S'
        )
        logging.error(f"Failed to configure enhanced logging: {str(e)}")
        return StructuredLogger(__name__)

def get_logger(name: str) -> StructuredLogger:
    """Get an enhanced logger instance with the given name."""
    return StructuredLogger(name)

# Compatibility aliases
CustomLogger = StructuredLogger
