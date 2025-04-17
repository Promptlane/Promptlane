from sqlalchemy import Column, Text, ForeignKey, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, declared_attr, backref
from ...db.models.base import BaseModel

class Comment(BaseModel):
    """SQLAlchemy model for prompt comments table."""
    __tablename__ = 'prompt_comments'

    content = Column(Text, nullable=False)
    prompt_id = Column(UUID(as_uuid=True), ForeignKey('prompts.id', ondelete='CASCADE'), nullable=False)
    is_edited = Column(Boolean, default=False)
    is_pinned = Column(Boolean, default=False)
    
    @declared_attr
    def prompt(cls):
        # Use overlaps to prevent circular dependency issues
        return relationship("Prompt", backref=backref("comments", overlaps="prompt"))
    
    @declared_attr
    def replies(cls):
        return relationship("Reply", 
                           back_populates="comment", 
                           cascade="all, delete-orphan",
                           order_by="Reply.created_at")
    
    def __repr__(self):
        return f"<Comment(id='{self.id}', prompt_id='{self.prompt_id}', created_by='{self.created_by}')>"

class Reply(BaseModel):
    """SQLAlchemy model for comment replies table."""
    __tablename__ = 'comment_replies'
    
    content = Column(Text, nullable=False)
    comment_id = Column(UUID(as_uuid=True), ForeignKey('prompt_comments.id', ondelete='CASCADE'), nullable=False)
    is_edited = Column(Boolean, default=False)
    
    @declared_attr
    def comment(cls):
        return relationship("Comment", back_populates="replies")
    
    def __repr__(self):
        return f"<Reply(id='{self.id}', comment_id='{self.comment_id}', created_by='{self.created_by}')>" 