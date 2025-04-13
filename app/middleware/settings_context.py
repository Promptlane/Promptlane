"""
Middleware to add settings to template context
"""
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from app.config import settings

class SettingsContextMiddleware(BaseHTTPMiddleware):
    """Middleware to add settings to template context"""
    
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        if hasattr(response, "context"):
            response.context["settings"] = settings
        return response 