import os
from pathlib import Path
from typing import Optional, Dict, Any, List
from pydantic import Field, AnyHttpUrl, PostgresDsn, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

class DatabaseSettings(BaseSettings):
    """Database configuration settings"""
    HOST: str = Field(default_factory=lambda: os.getenv("POSTGRES_HOST", "db"))
    PORT: str = Field(default_factory=lambda: os.getenv("POSTGRES_PORT", "5432"))
    USER: str = Field(default_factory=lambda: os.getenv("POSTGRES_USER", "postgres"))
    PASSWORD: str = Field(default_factory=lambda: os.getenv("POSTGRES_PASSWORD", "postgres"))
    NAME: str = Field(default_factory=lambda: os.getenv("POSTGRES_DB", "promptlane"))
    URL: Optional[str] = Field(default=None)
    
    # Connection pool settings
    POOL_PRE_PING: bool = Field(
        default_factory=lambda: os.getenv("DB_POOL_PRE_PING", "true").lower() == "true"
    )
    POOL_SIZE: int = Field(
        default_factory=lambda: int(os.getenv("DB_POOL_SIZE", "20"))
    )
    MAX_OVERFLOW: int = Field(
        default_factory=lambda: int(os.getenv("DB_MAX_OVERFLOW", "30"))
    )
    POOL_TIMEOUT: int = Field(
        default_factory=lambda: int(os.getenv("DB_POOL_TIMEOUT", "60"))
    )
    POOL_RECYCLE: int = Field(
        default_factory=lambda: int(os.getenv("DB_POOL_RECYCLE", "3600"))  # 1 hour
    )
    POOL_USE_LIFO: bool = Field(
        default_factory=lambda: os.getenv("DB_POOL_USE_LIFO", "true").lower() == "true"
    )
    
    # Connection retry settings
    CONNECTION_RETRIES: int = Field(
        default_factory=lambda: int(os.getenv("DB_CONNECTION_RETRIES", "3"))
    )
    RETRY_DELAY: int = Field(
        default_factory=lambda: int(os.getenv("DB_RETRY_DELAY", "1"))
    )
    
    # Session settings
    SESSION_AUTOCOMMIT: bool = Field(
        default_factory=lambda: os.getenv("DB_SESSION_AUTOCOMMIT", "false").lower() == "true"
    )
    SESSION_AUTOFLUSH: bool = Field(
        default_factory=lambda: os.getenv("DB_SESSION_AUTOFLUSH", "false").lower() == "true"
    )
    SESSION_EXPIRE_ON_COMMIT: bool = Field(
        default_factory=lambda: os.getenv("DB_SESSION_EXPIRE_ON_COMMIT", "false").lower() == "true"
    )
    
    # Debug settings
    ECHO: bool = Field(
        default_factory=lambda: os.getenv("DB_ECHO", "false").lower() == "true"
    )
    ECHO_POOL: bool = Field(
        default_factory=lambda: os.getenv("DB_ECHO_POOL", "false").lower() == "true"
    )
    CONNECT_TIMEOUT: int = Field(
        default_factory=lambda: int(os.getenv("DB_CONNECT_TIMEOUT", "10"))
    )

class SecuritySettings(BaseSettings):
    """Security configuration settings"""
    JWT_SECRET_KEY: str = Field(default_factory=lambda: os.getenv("JWT_SECRET_KEY", "your-secret-key"))
    JWT_ALGORITHM: str = Field(default_factory=lambda: os.getenv("JWT_ALGORITHM", "HS256"))
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(
        default_factory=lambda: int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    )
    
    # Session settings
    SESSION_COOKIE_NAME: str = Field(default_factory=lambda: os.getenv("SESSION_COOKIE_NAME", "session"))
    SESSION_MAX_AGE: int = Field(default_factory=lambda: int(os.getenv("SESSION_MAX_AGE", "1800")))  # 30 minutes
    SESSION_SAME_SITE: str = Field(default_factory=lambda: os.getenv("SESSION_SAME_SITE", "lax"))
    SESSION_HTTPS_ONLY: bool = Field(
        default_factory=lambda: os.getenv("SESSION_HTTPS_ONLY", "false").lower() == "true"
    )
    
    # Auth paths settings
    AUTH_PROTECTED_PATHS: List[str] = Field(
        default_factory=lambda: [
            path.strip() for path in os.getenv(
                "AUTH_PROTECTED_PATHS",
                "/projects,/admin,/dashboard,/teams,/prompts"
            ).split(",")
        ]
    )
    AUTH_PUBLIC_PATHS: List[str] = Field(
        default_factory=lambda: [
            path.strip() for path in os.getenv(
                "AUTH_PUBLIC_PATHS",
                "/,/login,/register,/static,/healthcheck"
            ).split(",")
        ]
    )
    
    # Auth redirect settings
    AUTH_LOGIN_PATH: str = Field(default_factory=lambda: os.getenv("AUTH_LOGIN_PATH", "/login"))
    AUTH_DEFAULT_REDIRECT: str = Field(default_factory=lambda: os.getenv("AUTH_DEFAULT_REDIRECT", "/"))
    AUTH_USE_NEXT_PARAM: bool = Field(
        default_factory=lambda: os.getenv("AUTH_USE_NEXT_PARAM", "true").lower() == "true"
    )
    
    # Auth error messages
    AUTH_ERROR_NOT_AUTHENTICATED: str = Field(
        default_factory=lambda: os.getenv("AUTH_ERROR_NOT_AUTHENTICATED", "Not authenticated")
    )
    AUTH_ERROR_USER_NOT_FOUND: str = Field(
        default_factory=lambda: os.getenv("AUTH_ERROR_USER_NOT_FOUND", "User not found")
    )
    AUTH_ERROR_INVALID_USER_ID: str = Field(
        default_factory=lambda: os.getenv("AUTH_ERROR_INVALID_USER_ID", "Invalid user ID format")
    )
    AUTH_ERROR_ADMIN_REQUIRED: str = Field(
        default_factory=lambda: os.getenv("AUTH_ERROR_ADMIN_REQUIRED", "Admin privileges required")
    )

class EmailSettings(BaseSettings):
    """Email configuration settings"""
    HOST: str = Field(default_factory=lambda: os.getenv("EMAIL_HOST", "smtp.example.com"))
    PORT: int = Field(default_factory=lambda: int(os.getenv("EMAIL_PORT", "587")))
    USER: str = Field(default_factory=lambda: os.getenv("EMAIL_USER", "noreply@example.com"))
    PASSWORD: str = Field(default_factory=lambda: os.getenv("EMAIL_PASSWORD", ""))
    FROM: str = Field(default_factory=lambda: os.getenv("EMAIL_FROM", "noreply@example.com"))
    TLS: bool = Field(default_factory=lambda: os.getenv("EMAIL_TLS", "true").lower() == "true")
    SSL: bool = Field(default_factory=lambda: os.getenv("EMAIL_SSL", "false").lower() == "true")
    USE_CREDENTIALS: bool = Field(
        default_factory=lambda: os.getenv("EMAIL_USE_CREDENTIALS", "true").lower() == "true"
    )
    VALIDATE_CERTS: bool = Field(
        default_factory=lambda: os.getenv("EMAIL_VALIDATE_CERTS", "true").lower() == "true"
    )
    DEV_DIR: str = Field(default_factory=lambda: os.getenv("EMAIL_DEV_DIR", "data/emails"))

class StorageSettings(BaseSettings):
    """Storage configuration settings"""
    UPLOAD_DIR: str = Field(default_factory=lambda: os.getenv("UPLOAD_DIR", "data/uploads"))
    MAX_UPLOAD_SIZE: int = Field(
        default_factory=lambda: int(os.getenv("MAX_UPLOAD_SIZE", str(10 * 1024 * 1024)))
    )

class APISettings(BaseSettings):
    """API configuration settings"""
    RATE_LIMIT_ENABLED: bool = Field(
        default_factory=lambda: os.getenv("RATE_LIMIT_ENABLED", "true").lower() == "true"
    )
    RATE_LIMIT_REQUESTS: int = Field(
        default_factory=lambda: int(os.getenv("RATE_LIMIT_REQUESTS", "100"))
    )
    RATE_LIMIT_PERIOD: int = Field(
        default_factory=lambda: int(os.getenv("RATE_LIMIT_PERIOD", "60"))
    )
    ALLOWED_ORIGINS: List[str] = Field(
        default_factory=lambda: [
            origin.strip() for origin in os.getenv("ALLOWED_ORIGINS", "*").split(",")
        ]
    )
    V1_PREFIX: str = Field(
        default_factory=lambda: os.getenv("API_V1_PREFIX", "/api/v1")
    )

class ServerSettings(BaseSettings):
    """Server configuration settings"""
    HOST: str = Field(
        default_factory=lambda: os.getenv("HOST", "0.0.0.0")
    )
    PORT: int = Field(
        default_factory=lambda: int(os.getenv("PORT", "8000"))
    )
    RELOAD: bool = Field(
        default_factory=lambda: os.getenv("RELOAD", "false").lower() == "true"
    )
    WORKERS: int = Field(
        default_factory=lambda: int(os.getenv("WORKERS", "1"))
    )

class AppSettings(BaseSettings):
    """Application information settings"""
    NAME: str = Field(default_factory=lambda: os.getenv("APP_NAME", "PromptLane"))
    VERSION: str = Field(default_factory=lambda: os.getenv("APP_VERSION", "1.0.0"))
    DESCRIPTION: str = Field(
        default_factory=lambda: os.getenv("APP_DESCRIPTION", "PromptLane API")
    )
    SITE_URL: str = Field(
        default_factory=lambda: os.getenv("SITE_URL", "http://localhost:8000")
    )

class LoggingSettings(BaseSettings):
    """Logging configuration settings"""
    LEVEL: str = Field(default_factory=lambda: os.getenv("LOG_LEVEL", "INFO"))
    MAX_BYTES: int = Field(
        default_factory=lambda: int(os.getenv("LOG_MAX_BYTES", str(10 * 1024 * 1024)))  # 10MB default
    )
    BACKUP_COUNT: int = Field(
        default_factory=lambda: int(os.getenv("LOG_BACKUP_COUNT", "5"))
    )
    FORMAT: str = Field(
        default_factory=lambda: os.getenv("LOG_FORMAT", "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    )

class BaseSettings(BaseSettings):
    """Base settings with environment variable support"""
    
    # Environment
    ENVIRONMENT: str = Field(
        default_factory=lambda: os.getenv("ENVIRONMENT", "development")
    )
    DEBUG: bool = Field(
        default_factory=lambda: os.getenv("DEBUG", "false").lower() == "true"
    )
    
    # Grouped settings
    DATABASE: DatabaseSettings = DatabaseSettings()
    SECURITY: SecuritySettings = SecuritySettings()
    EMAIL: EmailSettings = EmailSettings()
    STORAGE: StorageSettings = StorageSettings()
    API: APISettings = APISettings()
    APP: AppSettings = AppSettings()
    LOGGING: LoggingSettings = LoggingSettings()
    SERVER: ServerSettings = ServerSettings()
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )
    
    @model_validator(mode='after')
    def validate_database_url(self) -> 'BaseSettings':
        """Build database URL from components if not provided"""
        if not self.DATABASE.URL:
            try:
                self.DATABASE.URL = str(PostgresDsn.build(
                    scheme="postgresql",
                    username=self.DATABASE.USER,
                    password=self.DATABASE.PASSWORD,
                    host=self.DATABASE.HOST,
                    port=self.DATABASE.PORT,
                    path=f"/{self.DATABASE.NAME}",
                ))
            except Exception as e:
                # Fallback URL in case of validation error
                self.DATABASE.URL = f"postgresql://{self.DATABASE.USER}:{self.DATABASE.PASSWORD}@{self.DATABASE.HOST}:{self.DATABASE.PORT}/{self.DATABASE.NAME}"
        return self

    @model_validator(mode='after')
    def validate_jwt_secret_key(self) -> 'BaseSettings':
        """Use SECRET_KEY as JWT_SECRET_KEY if not provided"""
        if not self.SECURITY.JWT_SECRET_KEY:
            self.SECURITY.JWT_SECRET_KEY = getattr(self.SECURITY, "SECRET_KEY", "your-secret-key")
        return self

# Helper functions for frequently used settings
def get_db_url() -> str:
    """Get the database URL"""
    from . import settings
    return str(settings.DATABASE.URL)

def is_debug_mode() -> bool:
    """Check if the application is in debug mode"""
    from . import settings
    return settings.DEBUG

def get_upload_path() -> Path:
    """Get the absolute path for file uploads"""
    from . import settings
    base_dir = Path(__file__).resolve().parent.parent.parent
    upload_path = base_dir / settings.STORAGE.UPLOAD_DIR
    
    # Ensure directory exists
    upload_path.mkdir(parents=True, exist_ok=True)
    
    return upload_path

def get_logs_path() -> Path:
    """Get the absolute path for log files"""
    from . import settings
    base_dir = Path(__file__).resolve().parent.parent.parent
    logs_path = base_dir / "logs"
    
    # Ensure directory exists
    logs_path.mkdir(parents=True, exist_ok=True)
    
    return logs_path

def get_email_dev_path() -> Path:
    """Get the absolute path for development email storage"""
    from . import settings
    base_dir = Path(__file__).resolve().parent.parent.parent
    email_path = base_dir / settings.EMAIL.DEV_DIR
    
    # Ensure directory exists
    email_path.mkdir(parents=True, exist_ok=True)
    
    return email_path 