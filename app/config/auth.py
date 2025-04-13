"""
Authentication configuration settings
"""
from typing import List, Dict, Any
from pydantic import BaseModel
from .base import BaseSettings

class AuthConfig(BaseModel):
    # List of paths that require authentication
    protected_paths: List[str] = BaseSettings().SECURITY.AUTH_PROTECTED_PATHS
    
    # List of paths that are public (no auth required)
    public_paths: List[str] = BaseSettings().SECURITY.AUTH_PUBLIC_PATHS
    
    # Session configuration
    session_config: Dict[str, Any] = {
        "cookie_name": BaseSettings().SECURITY.SESSION_COOKIE_NAME,
        "max_age": BaseSettings().SECURITY.SESSION_MAX_AGE,
        "same_site": BaseSettings().SECURITY.SESSION_SAME_SITE,
        "https_only": BaseSettings().SECURITY.SESSION_HTTPS_ONLY
    }
    
    # Redirect configuration
    redirect_config: Dict[str, Any] = {
        "login_path": BaseSettings().SECURITY.AUTH_LOGIN_PATH,
        "default_redirect": BaseSettings().SECURITY.AUTH_DEFAULT_REDIRECT,
        "use_next_param": BaseSettings().SECURITY.AUTH_USE_NEXT_PARAM
    }
    
    # Error messages
    error_messages: Dict[str, str] = {
        "not_authenticated": BaseSettings().SECURITY.AUTH_ERROR_NOT_AUTHENTICATED,
        "user_not_found": BaseSettings().SECURITY.AUTH_ERROR_USER_NOT_FOUND,
        "invalid_user_id": BaseSettings().SECURITY.AUTH_ERROR_INVALID_USER_ID,
        "admin_required": BaseSettings().SECURITY.AUTH_ERROR_ADMIN_REQUIRED
    }

# Create default auth config
auth_config = AuthConfig() 