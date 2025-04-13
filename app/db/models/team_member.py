from sqlalchemy import Column, String, ForeignKey, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, declared_attr
from ...db.models.base import BaseModel
from enum import Enum as PyEnum


# Team member role enumeration
class TeamRole(PyEnum):
    """Roles for team members with different permission levels"""
    OWNER = "owner"         # Full access, can manage team, projects, prompts
    ADMIN = "admin"         # Can manage projects and prompts, limited team management
    EDITOR = "editor"       # Can edit projects and prompts, no team management
    VIEWER = "viewer"       # Read-only access

class TeamMember(BaseModel):
    """SQLAlchemy model for team_members table."""
    __tablename__ = 'team_members'

    team_id = Column(UUID(as_uuid=True), ForeignKey('teams.id', ondelete='CASCADE'), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    role = Column(Enum(TeamRole), default=TeamRole.VIEWER, nullable=False)
    status = Column(Enum('active', 'pending', 'inactive', name='member_status'), nullable=False, default='pending')

    @declared_attr
    def team(cls):
        return relationship("Team", back_populates="members")

    @declared_attr
    def user(cls):
        return relationship("User", foreign_keys=[cls.user_id], back_populates="team_memberships")

    def __repr__(self):
        return f"<TeamMember(team_id='{self.team_id}', user_id='{self.user_id}', role='{self.role}')>" 