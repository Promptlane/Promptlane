"""
Logging configuration for Promptlane.

This module configures logging for the application.
"""

import logging
import sys
import os
from pathlib import Path
from fastapi import Request
from logging.handlers import RotatingFileHandler
from app.config import settings, get_logs_path

# Base logging level
LOG_LEVEL = os.getenv("LOG_LEVEL", settings.LOGGING.LEVEL).upper()

# Get logs directory
LOGS_DIR = get_logs_path()

# Configure root logger
def configure_logging():
    """Configure the application's logging system"""
    
    # Create formatters
    console_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'
    )
    
    # Create handlers
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(console_formatter)
    
    # Create file handlers for different log types
    general_file_handler = RotatingFileHandler(
        str(LOGS_DIR / "app.log"),
        maxBytes=settings.LOGGING.MAX_BYTES,
        backupCount=settings.LOGGING.BACKUP_COUNT
    )
    general_file_handler.setFormatter(file_formatter)
    
    invitation_file_handler = RotatingFileHandler(
        str(LOGS_DIR / "invitations.log"),
        maxBytes=settings.LOGGING.MAX_BYTES,
        backupCount=settings.LOGGING.BACKUP_COUNT
    )
    invitation_file_handler.setFormatter(file_formatter)
    
    email_file_handler = RotatingFileHandler(
        str(LOGS_DIR / "emails.log"),
        maxBytes=settings.LOGGING.MAX_BYTES,
        backupCount=settings.LOGGING.BACKUP_COUNT
    )
    email_file_handler.setFormatter(file_formatter)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(LOG_LEVEL)
    root_logger.addHandler(console_handler)
    root_logger.addHandler(general_file_handler)
    
    # Configure specific loggers
    invitation_logger = logging.getLogger("app.routers.admin")
    invitation_logger.setLevel(logging.DEBUG)
    invitation_logger.addHandler(invitation_file_handler)
    
    invitation_crud_logger = logging.getLogger("app.db.crud")
    invitation_crud_logger.setLevel(logging.DEBUG)
    invitation_crud_logger.addHandler(invitation_file_handler)
    
    email_logger = logging.getLogger("app.services.email")
    email_logger.setLevel(logging.DEBUG)
    email_logger.addHandler(email_file_handler)
    
    template_logger = logging.getLogger("app.services.template")
    template_logger.setLevel(logging.DEBUG)
    template_logger.addHandler(email_file_handler)
    
    # Additional loggers
    request_logger = logging.getLogger("app.request")
    request_logger.setLevel(logging.INFO)
    request_logger.addHandler(general_file_handler)
    
    return root_logger

# Create a logger for the current module
def get_logger(name):
    """Get a logger for the specified name"""
    return logging.getLogger(name)

# Log request information
def log_request_info(request: Request, response=None, error=None):
    """Log information about a request"""
    logger = get_logger("app.request")
    
    if error:
        logger.error(f"Exception during request processing: {str(error)}")
        return
    
    if response:
        status_code = getattr(response, "status_code", "unknown")
        logger.info(f"Request processed successfully")
    else:
        logger.info(f"Request received: {request.method} {request.url.path}") 