import logging
from fastapi import HTTPException, status
from typing import Optional, Dict, Any, Union, Type

logger = logging.getLogger(__name__)

class ErrorType:
    """Standardized error types for consistent API responses"""
    VALIDATION_ERROR = "validation_error"
    RESOURCE_NOT_FOUND = "resource_not_found"
    RESOURCE_EXISTS = "resource_exists"
    PERMISSION_DENIED = "permission_denied"
    INVALID_CREDENTIALS = "invalid_credentials"
    EXPIRED_TOKEN = "expired_token"
    INVALID_TOKEN = "invalid_token"
    INTERNAL_ERROR = "internal_error"
    SERVICE_UNAVAILABLE = "service_unavailable"
    BAD_REQUEST = "bad_request"

def api_error(
    message: str, 
    error_type: str, 
    status_code: int = status.HTTP_400_BAD_REQUEST,
    error_details: Optional[Dict[str, Any]] = None
) -> HTTPException:
    """
    Create a standardized API error response
    
    Args:
        message: Human-readable error message
        error_type: One of the ErrorType constants
        status_code: HTTP status code
        error_details: Optional dict with additional error details
        
    Returns:
        HTTPException with consistent error format
    """
    content = {
        "detail": message,
        "error_type": error_type
    }
    
    if error_details:
        content["error_details"] = error_details
        
    # Log the error appropriately based on status code
    if status_code >= 500:
        logger.error(f"Internal error ({error_type}): {message}")
    else:
        logger.warning(f"Client error ({error_type}): {message}")
        
    return HTTPException(
        status_code=status_code,
        detail=content
    )

# Common error helpers
def validation_error(message: str, details: Optional[Dict[str, Any]] = None) -> HTTPException:
    """Validation error (400 Bad Request)"""
    return api_error(message, ErrorType.VALIDATION_ERROR, status.HTTP_400_BAD_REQUEST, details)

def resource_not_found(resource_type: str, identifier: Any) -> HTTPException:
    """Resource not found error (404 Not Found)"""
    message = f"{resource_type} with identifier '{identifier}' not found"
    return api_error(message, ErrorType.RESOURCE_NOT_FOUND, status.HTTP_404_NOT_FOUND)

def resource_exists(resource_type: str, identifier: Any) -> HTTPException:
    """Resource already exists error (409 Conflict)"""
    message = f"{resource_type} with identifier '{identifier}' already exists"
    return api_error(message, ErrorType.RESOURCE_EXISTS, status.HTTP_409_CONFLICT)

def permission_denied(action: str) -> HTTPException:
    """Permission denied error (403 Forbidden)"""
    message = f"You do not have permission to {action}"
    return api_error(message, ErrorType.PERMISSION_DENIED, status.HTTP_403_FORBIDDEN)

def internal_error(message: str = "An unexpected error occurred") -> HTTPException:
    """Internal server error (500 Internal Server Error)"""
    return api_error(message, ErrorType.INTERNAL_ERROR, status.HTTP_500_INTERNAL_SERVER_ERROR) 