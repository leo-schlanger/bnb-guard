import logging
from typing import Optional
from datetime import datetime
import colorama
from colorama import Fore, Style, Back

# Initialize colorama
colorama.init(autoreset=True)

class CustomLogger:
    """
    A custom logger class with colored output and different log levels.
    
    Log Levels:
    - DEBUG: Detailed information, typically of interest only when diagnosing problems.
    - INFO: Confirmation that things are working as expected.
    - WARNING: An indication that something unexpected happened.
    - ERROR: Due to a more serious problem, the software has not been able to perform some function.
    - CRITICAL: A serious error, indicating that the program itself may be unable to continue running.
    """
    
    def __init__(self, name: str, log_level: int = logging.INFO):
        """
        Initialize the logger.
        
        Args:
            name (str): Name of the logger, usually __name__
            log_level (int): Logging level (default: logging.INFO)
        """
        self.logger = logging.getLogger(name)
        self.logger.setLevel(log_level)
        
        # Create console handler with a higher log level
        ch = logging.StreamHandler()
        ch.setLevel(log_level)
        
        # Create formatter and add it to the handlers
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        ch.setFormatter(formatter)
        
        # Add the handlers to the logger
        if not self.logger.handlers:
            self.logger.addHandler(ch)
    
    def debug(self, message: str, context: Optional[dict] = None):
        """Log a debug message with blue color."""
        self._log_with_context(logging.DEBUG, Fore.BLUE, "DEBUG", message, context)
    
    def info(self, message: str, context: Optional[dict] = None):
        """Log an info message with green color."""
        self._log_with_context(logging.INFO, Fore.GREEN, "INFO", message, context)
    
    def warning(self, message: str, context: Optional[dict] = None):
        """Log a warning message with yellow color."""
        self._log_with_context(logging.WARNING, Fore.YELLOW, "WARNING", message, context)
    
    def error(self, message: str, context: Optional[dict] = None, exc_info=None):
        """
        Log an error message with red color.
        
        Args:
            message: The error message to log
            context: Optional dictionary with additional context
            exc_info: Exception information to include in the log
        """
        self._log_with_context(logging.ERROR, Fore.RED, "ERROR", message, context, exc_info=exc_info)
    
    def critical(self, message: str, context: Optional[dict] = None, exc_info=None):
        """
        Log a critical message with bold red background.
        
        Args:
            message: The critical message to log
            context: Optional dictionary with additional context
            exc_info: Exception information to include in the log
        """
        self._log_with_context(logging.CRITICAL, f"{Style.BRIGHT}{Fore.WHITE}{Back.RED}", 
                             "CRITICAL", message, context, exc_info=exc_info)
    
    def _log_with_context(self, level: int, color: str, level_name: str, 
                         message: str, context: Optional[dict] = None, exc_info=None):
        """
        Internal method to log messages with context and optional exception info.
        
        Args:
            level: Logging level (e.g., logging.ERROR)
            color: Color code for the log message
            level_name: Name of the log level (e.g., "ERROR")
            message: The message to log
            context: Optional dictionary with additional context
            exc_info: Exception information to include in the log
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_message = f"{color}[{timestamp}] [{level_name}] {message}"
        
        # Add context if provided
        if context:
            context_str = " ".join(f"{k}={v}" for k, v in context.items())
            log_message += f" {Fore.CYAN}{context_str}"
        
        # Add reset at the end
        log_message += Style.RESET_ALL
        
        # Log the message with optional exception info
        if exc_info is not None:
            self.logger.log(level, log_message, exc_info=exc_info)
        else:
            self.logger.log(level, log_message)

# Create a default logger instance
def get_logger(name: str) -> CustomLogger:
    """
    Get a logger instance with the given name.
    
    Args:
        name (str): Name of the logger, usually __name__
        
    Returns:
        CustomLogger: Configured logger instance
    """
    return CustomLogger(name)
