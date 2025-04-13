"""
Authentication dependencies for FastAPI routes
"""
from fastapi import Request, HTTPException, status, Depends
from fastapi.responses import RedirectResponse
from functools import wraps
import uuid
from app.managers.user_manager import UserManager

def require_auth():
    """
    Dependency to require authentication for a route.
    If user is not authenticated, redirects to login page for web routes
    or returns 401 for API routes.
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(request: Request, *args, **kwargs):
            user_id = request.session.get("user_id")
            if not user_id:
                # For web routes, redirect to login
                if request.url.path.startswith("/api/"):
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Not authenticated"
                    )
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
                
                return await func(request, *args, **kwargs)
            except ValueError:
                # Invalid UUID format
                request.session.clear()
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid user ID format"
                )
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
            user = request.session.get("user", {})
            if not user.get("is_admin", False):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Admin privileges required"
                )
            return await func(request, *args, **kwargs)
        return wrapper
    return decorator 