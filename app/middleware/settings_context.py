"""
Middleware to add settings to template context
"""
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from app.config import settings

class SettingsContextMiddleware(BaseHTTPMiddleware):
    """Middleware to add settings to template context"""
    
    async def dispatch(self, request: Request, call_next):
        # Add settings to the request state before processing
        request.state.settings = settings
        
        # Process the request
        response = await call_next(request)
        
        # Return the response
        return response 