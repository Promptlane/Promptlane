import uuid
from sqlalchemy import Column, String, ForeignKey, DateTime, Enum, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship, declared_attr
from .base import BaseModel
import sqlalchemy
from datetime import datetime

class ActivityType(str, Enum):
    """Types of user activities tracked in the system"""
    LOGIN = "login"
    LOGOUT = "logout"
    REGISTER = "register"
    UPDATE_USER = "update_user"
    CREATE_USER = "create_user"
    CREATE_PROJECT = "create_project"
    UPDATE_PROJECT = "update_project" 
    DELETE_PROJECT = "delete_project"
    CREATE_PROMPT = "create_prompt"
    UPDATE_PROMPT = "update_prompt"
    DELETE_PROMPT = "delete_prompt"
    PROJECT_SEARCHED = "project_search"
    CREATE_PROMPT_VERSION = "create_prompt_version"
    EXECUTE_PROMPT = "execute_prompt"
    VIEW_DASHBOARD = "view_dashboard"
    VIEW_PROJECT = "view_project"
    VIEW_PROMPT = "view_prompt"
    VIEW_TEAMS = "view_teams"
    VIEW_TEAM = "view_team"
    CREATE_TEAM = "create_team"
    UPDATE_TEAM = "update_team"
    DELETE_TEAM = "delete_team"
    ADD_TEAM_MEMBER = "add_team_member"
    REMOVE_TEAM_MEMBER = "remove_team_member"
    UPDATE_TEAM_MEMBER_ROLE = "update_team_member_role"
    ADD_PROJECT_TO_TEAM = "add_project_to_team"

class Activity(BaseModel):
    __tablename__ = "activities"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    activity_type = Column(String, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    details = Column(JSONB, nullable=True)
    
    # Relationships
    @declared_attr
    def user(cls):
        return relationship("User", foreign_keys=[cls.user_id], back_populates="activities")
    
    # Indexes for common queries
    __table_args__ = (
        sqlalchemy.Index('idx_activities_user_id', 'user_id'),
        sqlalchemy.Index('idx_activities_timestamp', 'timestamp'),
    ) 

    def __repr__(self):
        return f"<Activity(id={self.id}, action='{self.activity_type}')>" 