from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from ...db.models.base import BaseModel

class Team(BaseModel):
    """SQLAlchemy model for teams table."""
    __tablename__ = 'teams'

    name = Column(String(100), nullable=False)
    description = Column(String(500), nullable=True)

    # Relationships
    members = relationship("TeamMember", back_populates="team", cascade="all, delete-orphan")
    projects = relationship("Project", back_populates="team", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Team(name='{self.name}')>" 