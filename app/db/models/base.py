from datetime import datetime
from sqlalchemy import Column, DateTime, ForeignKey
from sqlalchemy.orm import declared_attr, relationship
from sqlalchemy.ext.declarative import declarative_base
import uuid
from sqlalchemy.dialects.postgresql import UUID

Base = declarative_base()

class BaseModel(Base):
    """Base model class that includes common fields and methods."""
    __abstract__ = True

    @declared_attr
    def id(cls):
        return Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    @declared_attr
    def created_at(cls):
        return Column(DateTime, default=datetime.utcnow, nullable=False)

    @declared_attr
    def updated_at(cls):
        return Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    @declared_attr
    def created_by(cls):
        return Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=True)

    @declared_attr
    def updated_by(cls):
        return Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=True)

    @declared_attr
    def creator(cls):
        return relationship("User", foreign_keys=[cls.created_by])

    @declared_attr
    def updater(cls):
        return relationship("User", foreign_keys=[cls.updated_by]) 