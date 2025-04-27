from sqlalchemy import Column, String, Text, ForeignKey, Integer, Boolean, CheckConstraint, DateTime, UniqueConstraint, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, declared_attr, backref, validates
from sqlalchemy.sql import func, text
from ...db.models.base import BaseModel

class Prompt(BaseModel):
    """SQLAlchemy model for prompts table with versioning support."""
    __tablename__ = 'prompts'

    name = Column(String(100), nullable=False)
    key = Column(String(50), nullable=False, index=True)  # Unique within project
    description = Column(String(500), nullable=True)
    system_prompt = Column(Text, nullable=True)  # System instructions/context
    user_prompt = Column(Text, nullable=False)   # User-facing prompt
    is_active = Column(Boolean, default=True)
    version = Column(Integer, nullable=False, default=1)
    version_notes = Column(Text, nullable=True)  # Changelog for this version
    version_created_at = Column(DateTime(timezone=True), server_default=func.now())
    project_id = Column(UUID(as_uuid=True), ForeignKey('projects.id', ondelete='CASCADE'), nullable=False)
    parent_id = Column(UUID(as_uuid=True), ForeignKey("prompts.id"), nullable=True)

    # Add constraints
    __table_args__ = (
        # Ensure version numbers are sequential within a prompt family
        CheckConstraint(
            'version > 0',
            name='check_version_positive'
        ),
        # Ensure key is unique within project
        UniqueConstraint('project_id', 'key', name='uq_prompt_project_key'),
        # Ensure only one active version per prompt family using partial unique index
        Index(
            'ix_prompts_single_active_version',
            'parent_id',
            postgresql_where=text('is_active = true'),
            unique=True
        )
    )

    @declared_attr
    def project(cls):
        return relationship("Project", back_populates="prompts")
    
    # @declared_attr
    # def parent(cls):
    #     return relationship("Prompt", remote_side=[cls.id], backref=backref("versions", cascade="all, delete-orphan"))

    @property
    def version_count(self):
        """Get the count of versions including self"""
        if not hasattr(self, '_version_count'):
            self._version_count = len(self.versions.all()) + 1  # +1 for self
        return self._version_count

    @validates('version')
    def validate_version(self, key, version):
        """Ensure version numbers are sequential within a prompt family."""
        if self.parent_id:
            # For child versions, version must be greater than parent's version
            # Ensure parent is loaded from the session
            if not hasattr(self, '_parent'):
                self._parent = self.parent
            if not self._parent:
                raise ValueError("Parent prompt not found")
            if version <= self._parent.version:
                raise ValueError(f"Version must be greater than parent version {self._parent.version}")
        elif version < 1:
            # For root versions, version must be at least 1
            raise ValueError("Version must be at least 1")
        return version

    @validates('is_active')
    def validate_active(self, key, is_active):
        """Simply validate, don't modify others."""
        return is_active


    def __repr__(self):
        return f"<Prompt(key='{self.key}', name='{self.name}', version={self.version}, project_id={self.project_id})>" 