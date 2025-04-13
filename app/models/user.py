from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime
import uuid

class UserBase(BaseModel):
    username: str
    email: EmailStr
    
class UserCreate(UserBase):
    password: str
    
class UserLogin(BaseModel):
    username: str
    password: str
    
class UserInvite(BaseModel):
    username: str
    email: EmailStr
    is_admin: bool = False
    expiry_hours: int = 48
    personal_message: Optional[str] = None
    
class UserDB(UserBase):
    id: uuid.UUID
    hashed_password: str = ""
    is_admin: bool = False
    status: str = "active"  # "active", "invited", "disabled"
    invitation_token: Optional[str] = None
    invitation_expiry: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    model_config = {
        "from_attributes": True
    }
        
class UserResponse(UserBase):
    id: str  # UUID as string for JSON compatibility
    is_admin: bool = False
    status: str = "active"
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    model_config = {
        "from_attributes": True
    } 