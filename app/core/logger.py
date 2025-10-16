import logging
import sys
from pathlib import Path
from datetime import datetime
import os

# Create logs directory if it doesn't exist
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)

# Log file name with timestamp
log_file = log_dir / f"app_{datetime.now().strftime('%Y%m%d')}.log"

# Log format
log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
log_date_format = "%Y-%m-%d %H:%M:%S"

def get_logger(name: str) -> logging.Logger:
    """
    Get a configured logger instance.
    
    Args:
        name (str): Name of the logger (usually __name__)
        
    Returns:
        logging.Logger: Configured logger instance
    """
    logger = logging.getLogger(name)
    
    # Don't add handlers to a logger that already has handlers
    if logger.hasHandlers():
        return logger
    
    logger.setLevel(logging.DEBUG)
    
    # Create formatters
    formatter = logging.Formatter(fmt=log_format, datefmt=log_date_format)
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    
    # File handler
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    
    # Add handlers to the logger
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    
    return logger