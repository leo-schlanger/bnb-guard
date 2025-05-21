"""Logging configuration for the application with context support."""
import logging
import logging.config
import json
import sys
from pathlib import Path
from typing import Any, Dict, Optional, Union

# Create logs directory if it doesn't exist
LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

class ColoredFormatter(logging.Formatter):
    """Custom formatter that adds colors to log messages."""
    
    # ANSI escape codes for colors
    COLORS = {
        'WARNING': '\033[93m',  # Yellow
        'INFO': '\033[92m',     # Green
        'DEBUG': '\033[94m',    # Blue
        'CRITICAL': '\033[91m', # Red
        'ERROR': '\033[91m',    # Red
    }
    RESET = '\033[0m'
    
    def __init__(self, fmt=None, datefmt=None, style='%'):
        super().__init__(fmt, datefmt, style)
        self.use_color = sys.stdout.isatty()
    
    def format(self, record):
        # Store original levelname
        levelname = record.levelname
        
        # Add colors if output is a terminal
        if self.use_color and levelname in self.COLORS:
            colored_levelname = f"{self.COLORS[levelname]}{levelname}{self.RESET}"
            record.levelname = colored_levelname
            
            # Color the message for all levels
            record.msg = f"{self.COLORS[levelname]}{record.msg}{self.RESET}"
        
        # Call the original format method
        result = super().format(record)
        
        # Restore original levelname to avoid side effects
        record.levelname = levelname
        
        return result


class ContextLogger(logging.Logger):
    """Custom logger that supports context in log messages."""
    
    def _log(self, level, msg, args, exc_info=None, extra=None, **kwargs):
        """
        Low-level logging routine which creates a LogRecord and then calls
        all the handlers of this logger to handle the record.
        """
        # Handle context if provided
        context = kwargs.pop('context', None)
        if context is not None:
            if isinstance(context, dict):
                # Format context as JSON string for the log message
                context_str = json.dumps(context, default=str)
            else:
                context_str = str(context)
                
            # Add context to the message
            msg = f"{msg} | {context_str}"
        
        # Call the original _log method
        super()._log(level, msg, args, exc_info=exc_info, extra=extra, **kwargs)

# Register our custom logger class
logging.setLoggerClass(ContextLogger)

# Base logger configuration
LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "colored": {
            "()": "app.core.logging_config.ColoredFormatter",
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
        "standard": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
        "detailed": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s - %(filename)s:%(lineno)d",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": "DEBUG",
            "formatter": "colored",
            "stream": sys.stdout,
        },
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "DEBUG",
            "formatter": "detailed",
            "filename": str(LOG_DIR / "app.log"),
            "maxBytes": 10485760,  # 10MB
            "backupCount": 5,
            "encoding": "utf8",
        },
    },
    "loggers": {
        "app": {
            "handlers": ["console", "file"],
            "level": "DEBUG",
            "propagate": False,
        },
        "uvicorn": {
            "handlers": ["console", "file"],
            "level": "INFO",
            "propagate": False,
        },
        "uvicorn.error": {
            "level": "WARNING",
            "propagate": False,
        },
        "uvicorn.access": {
            "handlers": ["file"],  # Only log to file
            "level": "INFO",
            "propagate": False,
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "WARNING",
    },
}

def setup_logging():
    """
    Configure logging for the application.
    
    Returns:
        logging.Logger: The root logger instance
    """
    # Apply logging configuration
    logging.config.dictConfig(LOGGING_CONFIG)
    
    # Get the root logger
    logger = logging.getLogger("app")
    
    # Test logging at different levels
    logger.debug("Debug message from logging config")
    logger.info("Info message from logging config")
    logger.warning("Warning message from logging config")
    logger.error("Error message from logging config")
    
    # Test context logging
    logger.info("Testing context logging", context={"test": True, "value": 123})
    
    return logger
