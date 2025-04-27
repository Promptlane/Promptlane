"""
Authentication dependencies for FastAPI routes
"""
from fastapi import Request, HTTPException, status, Depends, Header
from fastapi.responses import RedirectResponse
from functools import wraps
import uuid
from app.managers.user_manager import UserManager
from typing import Optional

def get_token_from_header(authorization: Optional[str] = Header(None)) -> Optional[str]:
    """Extract token from Authorization header"""
    if not authorization:
        return None
    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            return None
        return token
    except:
        return None

def require_auth():
    """
    Dependency to require authentication for a route.
    For API routes: Uses token-based authentication
    For web routes: Uses session-based authentication
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(request: Request, *args, **kwargs):
            # Check if this is an API route
            is_api_route = request.url.path.startswith("/api/")
            
            if is_api_route:
                # Token-based authentication for API routes
                token = get_token_from_header(request.headers.get("Authorization"))
                if not token:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="No token provided",
                        headers={"WWW-Authenticate": "Bearer"}
                    )
                
                # Verify token and get user
                user_manager = UserManager()
                user = user_manager.verify_token(token)
                if not user:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Invalid token",
                        headers={"WWW-Authenticate": "Bearer"}
                    )
                
                # Add user to request state for use in route
                request.state.user = user
                
            else:
                # Session-based authentication for web routes
                user_id = request.session.get("user_id")
                if not user_id:
                    return RedirectResponse(
                        url=f"/login?next={request.url.path}",
                        status_code=status.HTTP_307_TEMPORARY_REDIRECT
                    )
                
                try:
                    # Verify user exists and is valid
                    user_uuid = uuid.UUID(user_id)
                    user_manager = UserManager()
                    user = user_manager.get_user(user_uuid)
                    if not user:
                        request.session.clear()
                        raise HTTPException(
                            status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="User not found"
                        )
                    
                    # Update session data with latest user information
                    request.session["user"] = {
                        "id": str(user.id),
                        "username": user.username,
                        "is_admin": user.is_admin
                    }
                    
                    # Add user to request state
                    request.state.user = user
                    
                except ValueError:
                    # Invalid UUID format
                    request.session.clear()
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Invalid user ID format"
                    )
            
            return await func(request, *args, **kwargs)
        return wrapper
    return decorator

def require_admin():
    """
    Dependency to require admin privileges for a route.
    Must be used after require_auth() decorator.
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(request: Request, *args, **kwargs):
            user = request.state.user
            if not user.is_admin:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Admin privileges required"
                )
            return await func(request, *args, **kwargs)
        return wrapper
    return decorator 