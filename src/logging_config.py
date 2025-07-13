"""
Logging configuration module for the Learn Language with Texts application.

This module provides centralized logging configuration with:
- Rotating file handlers for general and error logs
- Console output for development/monitoring
- Configurable log levels and file sizes
"""

import os
import logging
from logging.handlers import RotatingFileHandler
from typing import Optional


def setup_logging(
    logger_name: Optional[str] = None,
    log_dir: Optional[str] = None,
    log_level: int = logging.DEBUG,
    max_bytes: int = 10 * 1024 * 1024,  # 10 MB
    backup_count: int = 5,
    console_level: int = logging.INFO
) -> logging.Logger:
    """
    Configure and return a logger with file and console handlers.
    
    Args:
        logger_name: Name for the logger. If None, uses the calling module's name.
        log_dir: Directory for log files. If None, creates 'logs' dir relative to this module.
        log_level: Minimum log level for the logger (default: DEBUG).
        max_bytes: Maximum size per log file before rotation (default: 10MB).
        backup_count: Number of backup files to keep (default: 5).
        console_level: Minimum log level for console output (default: INFO).
    
    Returns:
        Configured logger instance.
    """
    # Determine log directory
    if log_dir is None:
        # Create logs directory relative to the src directory
        src_dir = os.path.dirname(os.path.abspath(__file__))
        log_dir = os.path.join(src_dir, 'logs')
    
    # Ensure log directory exists
    os.makedirs(log_dir, exist_ok=True)
    
    # Define log file paths
    general_log_file = os.path.join(log_dir, 'app.log')
    error_log_file = os.path.join(log_dir, 'app_errors.log')
    
    # Get logger
    logger = logging.getLogger(logger_name)
    
    # Avoid adding handlers multiple times if logger already configured
    if logger.handlers:
        return logger
    
    logger.setLevel(log_level)
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # 1. Handler for general logs (INFO and above) to app.log
    general_handler = RotatingFileHandler(
        general_log_file,
        maxBytes=max_bytes,
        backupCount=backup_count
    )
    general_handler.setLevel(logging.INFO)
    general_handler.setFormatter(formatter)
    logger.addHandler(general_handler)
    
    # 2. Handler for error logs (ERROR and above) to app_errors.log
    error_handler = RotatingFileHandler(
        error_log_file,
        maxBytes=max_bytes,
        backupCount=backup_count
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(formatter)
    logger.addHandler(error_handler)
    
    # 3. Handler for console output
    console_handler = logging.StreamHandler()
    console_handler.setLevel(console_level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    return logger


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """
    Get a logger instance. If not already configured, sets up logging with default settings.
    
    Args:
        name: Logger name. If None, uses the calling module's name.
    
    Returns:
        Logger instance.
    """
    logger = logging.getLogger(name)
    
    # If logger has no handlers, set it up with default configuration
    if not logger.handlers:
        return setup_logging(logger_name=name)
    
    return logger
