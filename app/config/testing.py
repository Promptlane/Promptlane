import os
from .base import BaseSettings
from pydantic import Field


class TestingSettings(BaseSettings):
    """Testing environment settings"""
    
    # Override environment settings
    ENVIRONMENT: str = "testing"
    DEBUG: bool = True
    
    # Testing database settings
    POSTGRES_DB: str = "promptlane_test"
    
    # Testing security settings
    JWT_SECRET_KEY: str = "testing-secret-key"
    
    # Testing storage settings
    UPLOAD_DIR: str = "data/uploads/test"
    
    # Testing email settings
    EMAIL_HOST: str = "localhost"
    EMAIL_PORT: int = 1025
    EMAIL_FROM: str = "test@promptlane.test"
    SITE_URL: str = "http://test.promptlane.test"
    
    model_config = {
        "env_file": ".env.testing",
        "env_file_encoding": "utf-8",
        "case_sensitive": True,
        "extra": "ignore"
    }

class TestingConfig(BaseSettings):
    """Test environment settings"""
    
    # Test-specific overrides
    DEBUG: bool = Field(default_factory=lambda: os.environ.get('DEBUG', 'true').lower() == 'true')
    TESTING: bool = Field(default_factory=lambda: os.environ.get('TESTING', 'true').lower() == 'true')
    LOG_LEVEL: str = Field(default_factory=lambda: os.environ.get('LOG_LEVEL', 'DEBUG'))
    
    # Test database settings
    POSTGRES_DB: str = Field(default_factory=lambda: os.environ.get('POSTGRES_DB', 'test_db'))
    DATABASE_URL: str = Field(default_factory=lambda: os.environ.get('DATABASE_URL', 'sqlite:///./test.db'))
    
    # Test performance settings
    PASSWORD_HASHING_ROUNDS: int = Field(default_factory=lambda: int(os.environ.get('PASSWORD_HASHING_ROUNDS', '1')))
    
    # Test CORS settings
    ALLOWED_ORIGINS: list = Field(default_factory=lambda: [
        origin.strip() for origin in os.environ.get('ALLOWED_ORIGINS', '*').split(',')
    ])
    
    model_config = {
        **BaseSettings.model_config,
        "env_prefix": "TEST_",  # Load TEST_* environment variables first
        "env_file": ".env.testing"  # Load testing-specific env file
    } 