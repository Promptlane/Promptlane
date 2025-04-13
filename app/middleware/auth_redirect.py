"""
Authentication redirect middleware for handling auth-related redirects
"""
from fastapi import Request, HTTPException
from fastapi.responses import RedirectResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette import status

class AuthRedirectMiddleware(BaseHTTPMiddleware):
    """Middleware for handling authentication redirects"""
    
    async def dispatch(self, request: Request, call_next):
        try:
            response = await call_next(request)
            
            # Check if the response is a redirect for authentication
            if response.status_code == status.HTTP_307_TEMPORARY_REDIRECT:
                redirect_url = response.headers.get("Location")
                if redirect_url and redirect_url.startswith("/login"):
                    # Convert HTTPException to RedirectResponse
                    return RedirectResponse(url=redirect_url, status_code=status.HTTP_303_SEE_OTHER)
                    
            return response
        except HTTPException as e:
            # Check if the exception is a redirect for authentication
            if e.status_code == status.HTTP_307_TEMPORARY_REDIRECT:
                redirect_url = e.headers.get("Location")
                if redirect_url and redirect_url.startswith("/login"):
                    # Convert HTTPException to RedirectResponse
                    return RedirectResponse(url=redirect_url, status_code=status.HTTP_303_SEE_OTHER)
            raise 