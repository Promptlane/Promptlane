"""
Global error handlers for the FastAPI application
"""
import traceback
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from app.templates import templates
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.config import settings
from app.logger import get_logger
from app.utils import JSONEncoder

# Initialize logger
logger = get_logger(__name__)

# Custom JSONResponse that uses our UUID-aware encoder
class CustomJSONResponse(JSONResponse):
    def render(self, content) -> bytes:
        return JSONEncoder().encode(content).encode("utf-8")

# Error handlers
async def not_found_error(request: Request, exc):
    # For API routes, always return JSON responses
    if request.url.path.startswith("/api/"):
        # Handle different types of error details
        if isinstance(exc, HTTPException):
            # For our custom structured errors
            if isinstance(exc.detail, dict) and "error_type" in exc.detail:
                return CustomJSONResponse(
                    status_code=exc.status_code,
                    content=exc.detail
                )
            # For standard FastAPI errors
            else:
                error_message = str(exc.detail) if hasattr(exc, "detail") else "Not found"
                return CustomJSONResponse(
                    status_code=exc.status_code,
                    content={
                        "detail": error_message,
                        "error_type": "not_found" if exc.status_code == 404 else "bad_request"
                    }
                )
        else:
            return CustomJSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content={
                    "detail": "Resource not found",
                    "error_type": "not_found"
                }
            )
    
    # Handle 404 errors specifically
    if isinstance(exc, StarletteHTTPException) and exc.status_code == 404:
        return templates.TemplateResponse(
            "404.html",
            {"request": request},
            status_code=404
        )
    
    # For other HTTP exceptions, pass through to the next handler
    if isinstance(exc, StarletteHTTPException):
        return templates.TemplateResponse(
            "500.html",
            {
                "request": request,
                "error": str(exc) if settings.DEBUG else None
            },
            status_code=exc.status_code
        )
    
    # Should not reach here
    return templates.TemplateResponse(
        "404.html",
        {"request": request},
        status_code=404
    )

async def server_error(request: Request, exc):
    # Log the full traceback
    error_details = "".join(traceback.format_exception(type(exc), exc, exc.__traceback__))
    logger.error(f"Unhandled exception: {error_details}")
    
    # For API routes, return JSON even for 500 errors
    if request.url.path.startswith("/api/"):
        # Handle different types of error details
        if isinstance(exc, HTTPException):
            # For our custom structured errors
            if isinstance(exc.detail, dict) and "error_type" in exc.detail:
                return CustomJSONResponse(
                    status_code=exc.status_code,
                    content=exc.detail
                )
            # For standard FastAPI errors
            else:
                return CustomJSONResponse(
                    status_code=exc.status_code,
                    content={"detail": str(exc.detail)}
                )
        # For unhandled exceptions
        else:
            return CustomJSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={
                    "detail": "Internal server error" if not settings.DEBUG else str(exc),
                    "error_type": "internal_error"
                }
            )
    
    # For web routes, return HTML response
    return templates.TemplateResponse(
        "500.html",
        {
            "request": request,
            "error": error_details if settings.DEBUG else None
        },
        status_code=500
    ) 