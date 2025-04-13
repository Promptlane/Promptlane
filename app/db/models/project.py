from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, declared_attr
from ...db.models.base import BaseModel

class Project(BaseModel):
    """SQLAlchemy model for projects table."""
    __tablename__ = 'projects'

    name = Column(String(100), nullable=False)
    key = Column(String(50), unique=True, nullable=False, index=True) 
    description = Column(String(500), nullable=True)
    team_id = Column(UUID(as_uuid=True), ForeignKey('teams.id', ondelete='CASCADE'), nullable=True)

    @declared_attr
    def team(cls):
        return relationship("Team", back_populates="projects")

    @declared_attr
    def owner(cls):
        return relationship("User", foreign_keys=[cls.created_by], back_populates="projects", overlaps="creator,updater")

    @declared_attr
    def creator(cls):
        return relationship("User", foreign_keys=[cls.created_by], overlaps="projects,owner,updater", viewonly=True)

    @declared_attr
    def updater(cls):
        return relationship("User", foreign_keys=[cls.updated_by], overlaps="owner,creator")

    @declared_attr
    def prompts(cls):
        return relationship("Prompt", back_populates="project", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Project(name='{self.name}', team_id={self.team_id})>" 