"""
Configuration package for Promptlane.
"""
import os
from pathlib import Path
from .base import (
    BaseSettings,
    get_upload_path,
    is_debug_mode,
    get_db_url,
    get_logs_path,
    get_email_dev_path
)
from .development import DevelopmentSettings
from .production import ProductionSettings
from .testing import TestingSettings

# Get environment from environment variable, default to development
ENV = os.getenv("ENVIRONMENT", "development")

# Import the correct settings based on environment
if ENV == "production":
    settings = ProductionSettings()
elif ENV == "testing":
    settings = TestingSettings()
else:  # development is the default
    settings = DevelopmentSettings()

def get_template_config():
    """Get the template configuration"""
    base_dir = Path(__file__).resolve().parent.parent
    return {
        "templates_dir": str(base_dir / "templates"),
        "email_templates_dir": str(base_dir / "templates" / "email"),
        "default_language": "en",
        "allowed_languages": ["en"],
        "default_timezone": "UTC"
    }

def validate_template_variables(template_vars: dict, required_vars: list) -> bool:
    """Validate that all required variables are present in the template variables"""
    return all(var in template_vars for var in required_vars)

__all__ = [
    "settings",
    "get_upload_path",
    "is_debug_mode",
    "get_db_url",
    "get_logs_path",
    "get_email_dev_path",
    "get_template_config",
    "validate_template_variables"
] 