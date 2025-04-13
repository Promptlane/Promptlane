import os
from .base import BaseSettings, DatabaseSettings, SecuritySettings, EmailSettings, StorageSettings, AppSettings, ServerSettings, LoggingSettings, APISettings
from pydantic import Field


class ProductionSettings(BaseSettings):
    """Production environment settings"""
    
    # Override environment settings
    ENVIRONMENT: str = "production"
    DEBUG: bool = False
    
    # Override grouped settings
    DATABASE: DatabaseSettings = DatabaseSettings(
        ECHO=False,  # Disable SQL logging in production
        ECHO_POOL=False,  # Disable connection pool logging
        POOL_SIZE=20,  # Larger connection pool for production
        MAX_OVERFLOW=30,  # Allow more connections in production
        POOL_RECYCLE=3600  # Recycle connections every hour
    )
    
    SECURITY: SecuritySettings = SecuritySettings(
        JWT_ACCESS_TOKEN_EXPIRE_MINUTES=15,  # Shorter expiry for production
        SESSION_HTTPS_ONLY=True,  # Enforce HTTPS in production
        SESSION_SAME_SITE="strict"  # Strict same-site policy
    )
    
    STORAGE: StorageSettings = StorageSettings(
        UPLOAD_DIR="/var/uploads/prod"  # Production upload directory
    )
    
    EMAIL: EmailSettings = EmailSettings(
        FROM="noreply@promptlane.com",
        TLS=True,  # Enforce TLS in production
        SSL=True,  # Enforce SSL in production
        VALIDATE_CERTS=True  # Validate certificates in production
    )
    
    API: APISettings = APISettings(
        RATE_LIMIT_ENABLED=True,  # Enable rate limiting in production
        RATE_LIMIT_REQUESTS=100,  # Requests per period
        RATE_LIMIT_PERIOD=60,  # Period in seconds
        ALLOWED_ORIGINS=["https://promptlane.com"]  # Production domain
    )
    
    SERVER: ServerSettings = ServerSettings(
        RELOAD=False,  # Disable auto-reload in production
        WORKERS=4  # Multiple workers for production
    )
    
    APP: AppSettings = AppSettings(
        SITE_URL="https://promptlane.com"
    )
    
    LOGGING: LoggingSettings = LoggingSettings(
        LEVEL="INFO",  # Less verbose logging in production
        FORMAT="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    model_config = {
        "env_file": ".env.production",
        "env_file_encoding": "utf-8",
        "case_sensitive": True,
        "extra": "ignore"
    } 