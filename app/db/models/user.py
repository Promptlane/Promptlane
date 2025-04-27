from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, declared_attr
from ...db.models.base import BaseModel
from ...core.security import get_password_hash, verify_password

class User(BaseModel):
    """SQLAlchemy model for users table."""
    __tablename__ = 'users'

    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(100), nullable=True)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    status = Column(Enum('active', 'invited', 'disabled', name='user_status'), 
                   default='active', nullable=False)
    invitation_token = Column(String(255), nullable=True, unique=True)
    invitation_expiry = Column(DateTime, nullable=True)

    @declared_attr
    def projects(cls):
        return relationship("Project", foreign_keys="[Project.created_by]", back_populates="owner")

    @declared_attr
    def team_memberships(cls):
        return relationship("TeamMember", foreign_keys="[TeamMember.user_id]", back_populates="user")

    @declared_attr
    def activities(cls):
        return relationship("Activity", foreign_keys="[Activity.user_id]", back_populates="user")

    def set_password(self, password: str) -> None:
        """Set the user's password."""
        self.hashed_password = get_password_hash(password)

    def verify_password(self, password: str) -> bool:
        """Verify the user's password."""
        return verify_password(password, self.hashed_password)

    def __repr__(self):
        return f"<User(username='{self.username}', email='{self.email}')>" 