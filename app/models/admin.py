from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List, Dict, Any

class UserInvite(BaseModel):
    """Schema for inviting new users"""
    username: str = Field(..., description="Username for the new user")
    email: EmailStr = Field(..., description="Email address of the user")
    is_admin: bool = Field(False, description="Whether the user should have admin privileges")
    expiry_hours: int = Field(48, description="Hours until invitation expires")
    personal_message: Optional[str] = Field(None, description="Optional personal message to include in invitation")

class AdminStatusUpdate(BaseModel):
    """Schema for updating a user's admin status"""
    is_admin_status: bool = Field(..., description="Whether the user should have admin privileges") 