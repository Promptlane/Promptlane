"""
Custom exceptions for the application
"""
import uuid
from typing import Optional
from fastapi import HTTPException, status

class ActivityCreationError(Exception):
    """Custom exception for activity creation failures"""
    def __init__(self, message: str, user_id: Optional[uuid.UUID] = None, activity_type: Optional[str] = None):
        self.message = message
        self.user_id = user_id
        self.activity_type = activity_type
        super().__init__(self.message)

class DatabaseError(Exception):
    """Base exception for database-related errors"""
    pass

class ValidationError(Exception):
    """Base exception for validation errors"""
    pass

class UserCreationError(Exception):
    """Custom exception for user creation failures"""
    def __init__(self, message: str, username: Optional[str] = None, email: Optional[str] = None):
        self.message = message
        self.username = username
        self.email = email
        super().__init__(self.message)

class UserNotFoundError(Exception):
    """Exception raised when a user is not found"""
    pass

class UserUpdateError(Exception):
    """Exception raised when user update fails"""
    pass

class ProjectCreationError(Exception):
    """Custom exception for project creation failures"""
    def __init__(self, message: str, project_key: Optional[str] = None, created_by: Optional[uuid.UUID] = None):
        self.message = message
        self.project_key = project_key
        self.created_by = created_by
        super().__init__(self.message)

class ProjectNotFoundError(Exception):
    """Exception raised when a project is not found"""
    pass

class ProjectUpdateError(Exception):
    """Exception raised when project update fails"""
    pass

class PromptCreationError(Exception):
    """Custom exception for prompt creation failures"""
    def __init__(self, message: str, name: Optional[str] = None, project_id: Optional[uuid.UUID] = None, created_by: Optional[uuid.UUID] = None):
        self.message = message
        self.name = name
        self.project_id = project_id
        self.created_by = created_by
        super().__init__(self.message)

class PromptNotFoundError(Exception):
    """Exception raised when a prompt is not found"""
    pass

class PromptUpdateError(Exception):
    """Exception raised when prompt update fails"""
    pass

class EmailServiceError(Exception):
    """Exception raised when email service operations fail"""
    pass

class TemplateRenderError(Exception):
    """Exception raised when template rendering fails"""
    pass

class InvalidCredentialsError(HTTPException):
    """Exception raised when credentials are invalid"""
    def __init__(self, detail: str = "Invalid credentials"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"}
        )

class UnauthorizedError(HTTPException):
    """Exception raised when user is not authorized"""
    def __init__(self, detail: str = "Not authorized"):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail
        )

class ResourceNotFoundError(HTTPException):
    """Exception raised when a resource is not found"""
    def __init__(self, detail: str = "Resource not found"):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail
        )

class ValidationError(HTTPException):
    """Exception raised when validation fails"""
    def __init__(self, detail: str = "Validation error"):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=detail
        )

class TeamCreationError(Exception):
    """Exception raised when team creation fails"""
    pass

class TeamNotFoundError(Exception):
    """Exception raised when a team is not found"""
    pass

class TeamUpdateError(Exception):
    """Exception raised when team update fails"""
    pass

class TeamMemberError(Exception):
    """Exception raised when team member operations fail"""
    pass 