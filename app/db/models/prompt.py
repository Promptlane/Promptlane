from sqlalchemy import Column, String, Text, ForeignKey, Integer, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, declared_attr, backref
from ...db.models.base import BaseModel

class Prompt(BaseModel):
    """SQLAlchemy model for prompts table."""
    __tablename__ = 'prompts'

    name = Column(String(100), nullable=False)
    key = Column(String(50), unique=True, nullable=False, index=True)  # URL-friendly identifier
    description = Column(String(500), nullable=True)
    system_prompt = Column(Text, nullable=True)  # System instructions/context
    user_prompt = Column(Text, nullable=False)   # User-facing prompt
    is_active = Column(Boolean, default=True)
    version = Column(Integer, nullable=False, default=1)
    project_id = Column(UUID(as_uuid=True), ForeignKey('projects.id', ondelete='CASCADE'), nullable=False)
    parent_id = Column(UUID(as_uuid=True), ForeignKey("prompts.id"), nullable=True)

    @declared_attr
    def project(cls):
        return relationship("Project", back_populates="prompts")
    
    @declared_attr
    def parent(cls):
        # Fix circular dependency by using backref with overlaps parameter
        return relationship(
            "Prompt", 
            remote_side=[cls.id], 
            backref=backref("versions", overlaps="parent"),
            overlaps="versions"
        )
    
    # Comments relationship is defined in the Comment model using backref

    def __repr__(self):
        return f"<Prompt(key='{self.key}', name='{self.name}', version={self.version}, project_id={self.project_id})>" 