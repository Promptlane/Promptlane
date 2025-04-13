from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid
from enum import Enum

# Define the team roles enum 
class TeamRole(str, Enum):
    OWNER = "owner"
    ADMIN = "admin"
    EDITOR = "editor"
    VIEWER = "viewer"

class TeamMemberBase(BaseModel):
    user_id: str
    role: TeamRole = TeamRole.VIEWER

class TeamMemberCreate(TeamMemberBase):
    pass

class TeamMemberUpdate(BaseModel):
    role: TeamRole

class TeamMemberDB(TeamMemberBase):
    id: uuid.UUID
    team_id: uuid.UUID
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    model_config = {
        "from_attributes": True
    }

class TeamMemberResponse(BaseModel):
    id: str  # UUID as string for JSON compatibility
    user_id: str
    team_id: str
    role: TeamRole
    created_at: datetime
    updated_at: Optional[datetime] = None
    # Include user details for display
    username: Optional[str] = None
    email: Optional[str] = None
    
    model_config = {
        "from_attributes": True
    }

class TeamBase(BaseModel):
    name: str
    description: Optional[str] = None

class TeamCreate(TeamBase):
    pass

class TeamUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None

class TeamDB(TeamBase):
    id: uuid.UUID
    created_by: uuid.UUID
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    model_config = {
        "from_attributes": True
    }

class TeamResponse(BaseModel):
    id: str  # UUID as string for JSON compatibility
    name: str
    description: Optional[str] = None
    created_by: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    member_count: Optional[int] = None
    project_count: Optional[int] = None
    
    model_config = {
        "from_attributes": True
    }

class TeamDetailResponse(TeamResponse):
    members: List[TeamMemberResponse] = []
    
    model_config = {
        "from_attributes": True
    }

# Use this for permissions check
class TeamPermission(BaseModel):
    can_view: bool = False
    can_edit: bool = False
    can_manage_members: bool = False
    can_delete: bool = False
    role: Optional[TeamRole] = None 