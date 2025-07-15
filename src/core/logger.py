"""Centralized logging configuration."""
import logging
from .logging_config import LOG_FILE, LOG_FORMAT, LOG_LEVEL

def setup_logger(name: str) -> logging.Logger:
    """Create and configure a logger instance for a module.
    
    Args:
        name: The name of the module requesting the logger
        
    Returns:
        A configured logger instance
    """
    logger = logging.getLogger(name)
    
    if not logger.handlers:  # Avoid adding handlers multiple times
        formatter = logging.Formatter(LOG_FORMAT)
        
        # File handler
        file_handler = logging.FileHandler(LOG_FILE)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        
        logger.setLevel(getattr(logging, LOG_LEVEL))
    
    return logger
