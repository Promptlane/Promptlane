from pydantic import BaseModel, Field
from typing import Optional, Any, List, Dict
from datetime import datetime
import uuid
from enum import Enum

class ActivityType(str, Enum):
    """Types of user activities tracked in the system"""
    login = "login"
    logout = "logout"
    register = "register"
    create_project = "create_project"
    update_project = "update_project"
    delete_project = "delete_project"
    create_prompt = "create_prompt"
    update_prompt = "update_prompt"
    delete_prompt = "delete_prompt"
    create_prompt_version = "create_prompt_version"
    execute_prompt = "execute_prompt"
    view_dashboard = "view_dashboard"
    view_project = "view_project"
    view_prompt = "view_prompt"
    view_teams = "view_teams"
    view_team = "view_team"
    create_team = "create_team"
    update_team = "update_team"
    delete_team = "delete_team"
    add_team_member = "add_team_member"
    remove_team_member = "remove_team_member"
    update_team_member_role = "update_team_member_role"

class ActivityBase(BaseModel):
    user_id: str
    activity_type: ActivityType
    timestamp: datetime = Field(default_factory=datetime.now)
    
    class Config:
        orm_mode = True

class ActivityCreate(ActivityBase):
    metadata: Optional[Dict[str, Any]] = None

class Activity(BaseModel):
    """User activity data model"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    activity_type: ActivityType
    description: str
    resource_id: Optional[str] = None
    resource_type: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        orm_mode = True

class ActivityResponse(BaseModel):
    """Model for returning activity data to the frontend"""
    id: str  # UUID as string for JSON compatibility
    user_id: str  # UUID as string for JSON compatibility
    activity_type: ActivityType
    timestamp: datetime
    details: Optional[dict] = None
    
    model_config = {
        "from_attributes": True
    }

class UserActivity(BaseModel):
    """Model for user activity data"""
    id: str
    user_id: str
    activity_type: str
    timestamp: datetime
    details: Optional[Dict] = None
    
    class Config:
        orm_mode = True

class DateActivity(BaseModel):
    """Model for activity counts by date"""
    date: str
    count: int

class TypeActivity(BaseModel):
    """Model for activity counts by type"""
    activity_type: str
    count: int

class ProjectActivity(BaseModel):
    """Model for project activity data"""
    project_id: str
    project_name: str
    activity_count: int

class PromptActivity(BaseModel):
    """Model for prompt activity data"""
    prompt_id: str
    prompt_name: str
    project_name: str
    activity_count: int

class UserStats(BaseModel):
    """User statistics model"""
    total_projects: int
    total_prompts: int
    total_versions: int
    login_count: int
    prompt_execution_count: int
    first_login: Optional[datetime] = None
    last_login: Optional[datetime] = None
    activity_count: int

    class Config:
        orm_mode = True

class ActivitySummary(BaseModel):
    """
    Summary of activities for charts and visualizations
    """
    label: str
    count: int

    class Config:
        orm_mode = True 