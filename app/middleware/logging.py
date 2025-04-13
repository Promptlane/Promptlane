"""
Logging middleware for request/response logging
"""
import time
import uuid
from typing import Dict, Any, Tuple
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from app.logger import log_request_info

class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for logging HTTP requests and responses"""
    
    def _generate_request_id(self, request: Request) -> Tuple[str, str]:
        """Generate request ID and handle client-provided correlation ID"""
        # Generate our own request ID
        request_id = str(uuid.uuid4())
        
        # Get client correlation ID if provided
        client_correlation_id = request.headers.get("X-Correlation-ID")
        
        return request_id, client_correlation_id
    
    def _get_request_details(self, request: Request) -> Dict[str, Any]:
        """Extract common request details"""
        request_id, client_correlation_id = self._generate_request_id(request)
        
        # Safely get session data
        session_id = None
        user_id = None
        try:
            if hasattr(request, "session") and "session" in request.scope:
                session_id = request.session.get("session_id")
                user_id = request.session.get("user_id")
        except Exception:
            # If there's any error accessing session, just use None values
            pass
        
        return {
            "request_id": request_id,
            "client_correlation_id": client_correlation_id,
            "method": request.method,
            "url": str(request.url),
            "path": request.url.path,
            "query_params": dict(request.query_params),
            "client_host": request.client.host if request.client else None,
            "user_agent": request.headers.get("user-agent"),
            "referer": request.headers.get("referer"),
            "content_type": request.headers.get("content-type"),
            "accept": request.headers.get("accept"),
            "content_length": request.headers.get("content-length"),
            "x_forwarded_for": request.headers.get("x-forwarded-for"),
            "x_real_ip": request.headers.get("x-real-ip"),
            "session_id": session_id,
            "user_id": user_id,
        }
    
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        # Get request details
        request_details = self._get_request_details(request)
        
        # Add request ID to request state
        request.state.request_id = request_details["request_id"]
        if request_details["client_correlation_id"]:
            request.state.client_correlation_id = request_details["client_correlation_id"]
        
        # Log request received
        log_request_info(request)
        
        try:
            response = await call_next(request)
            process_time = time.time() - start_time
            
            # Add headers to response
            response.headers["X-Request-ID"] = request_details["request_id"]
            if request_details["client_correlation_id"]:
                response.headers["X-Correlation-ID"] = request_details["client_correlation_id"]
            response.headers["X-Process-Time"] = str(process_time)
            
            # Log response with timing
            log_request_info(request, response=response)
            
            return response
        except Exception as e:
            # Log error with request details
            log_request_info(request, error=e)
            raise 