import os
from .base import BaseSettings, DatabaseSettings, SecuritySettings, EmailSettings, StorageSettings, AppSettings, ServerSettings, LoggingSettings, APISettings
from pydantic import Field


class DevelopmentSettings(BaseSettings):
    """Development environment settings"""
    
    # Override environment settings
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    
    # Override grouped settings
    DATABASE: DatabaseSettings = DatabaseSettings(
        NAME="promptlane",
        ECHO=True,  # Enable SQL logging in development
        ECHO_POOL=True  # Enable connection pool logging
    )
    
    SECURITY: SecuritySettings = SecuritySettings(
        JWT_SECRET_KEY="development-secret-key",  # Only for development!
        JWT_ACCESS_TOKEN_EXPIRE_MINUTES=60,  # Longer expiry for development
        SESSION_HTTPS_ONLY=False  # Allow non-HTTPS in development
    )
    
    STORAGE: StorageSettings = StorageSettings(
        UPLOAD_DIR="data/uploads/dev"
    )
    
    EMAIL: EmailSettings = EmailSettings(
        HOST="localhost",
        PORT=1025,  # Mailhog default port
        FROM="dev@promptlane.local",
        TLS=False,  # Disable TLS for local development
        SSL=False,  # Disable SSL for local development
        VALIDATE_CERTS=False  # Don't validate certs in development
    )
    
    API: APISettings = APISettings(
        ALLOWED_ORIGINS=["http://localhost:3000", "http://localhost:8000"],
        RATE_LIMIT_ENABLED=False,  # Disable rate limiting in development
        V1_PREFIX="/api/v1"
    )
    
    SERVER: ServerSettings = ServerSettings(
        RELOAD=True,  # Enable auto-reload in development
        WORKERS=1
    )
    
    APP: AppSettings = AppSettings(
        SITE_URL="http://localhost:8000"
    )
    
    LOGGING: LoggingSettings = LoggingSettings(
        LEVEL="DEBUG",  # More verbose logging in development
        FORMAT="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    model_config = {
        "env_file": ".env.development",
        "env_file_encoding": "utf-8",
        "case_sensitive": True,
        "extra": "ignore"
    } 