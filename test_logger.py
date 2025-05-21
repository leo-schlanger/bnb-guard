import sys
import os
import logging

# Add project root to path to import project modules
sys.path.insert(0, os.path.abspath('.'))

# Import custom logger
from app.core.utils.logger import get_logger, setup_logging

def main():
    """Test the logging functionality with various log levels and contexts."""
    # Configure logging with DEBUG level to see all messages
    logger = setup_logging(level=logging.DEBUG)
    
    print("\n=== Testing log levels ===")
    logger.debug("This is a DEBUG message")
    logger.info("This is an INFO message")
    logger.warning("This is a WARNING message")
    logger.error("This is an ERROR message")
    logger.critical("This is a CRITICAL message")
    
    print("\n=== Testing log with context ===")
    # Test logging with context
    logger.info("User authenticated", context={"user_id": 123, "ip": "192.168.1.1"})
    
    # Test with a custom logger
    custom_logger = get_logger("my_module")
    custom_logger.info("Custom module message", 
                      context={"module": "test", "action": "processing"})
    
    print("\n=== Testing exception logging ===")
    # Test exception logging
    try:
        1 / 0
    except Exception as e:
        logger.error("Error processing request", 
                    exc_info=e,
                    context={"attempt": 1, "status": "failed"})
    
    print("\nLogging test completed. Check the messages above.")

if __name__ == "__main__":
    main()
