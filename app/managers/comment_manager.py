import uuid
import logging
from typing import List, Dict, Any, Tuple, Optional, Union
from datetime import datetime

from app.db.database import db
from app.db.models import Comment, Reply, Prompt, User
from sqlalchemy.orm import Session
from sqlalchemy import desc

logger = logging.getLogger(__name__)

class CommentManager:
    """Manager class for handling comment operations."""
    
    def __init__(self, db_session=None):
        self._db = db_session or db.get_session()
    
    def get_prompt_comments(self, prompt_id: uuid.UUID) -> List[Comment]:
        """Get all comments for a specific prompt."""
        try:
            comments = self._db.query(Comment)\
                .filter(Comment.prompt_id == prompt_id)\
                .order_by(desc(Comment.is_pinned), desc(Comment.created_at))\
                .all()
            return comments
        except Exception as e:
            logger.error(f"Error fetching comments for prompt {prompt_id}: {str(e)}")
            return []
    
    def get_comment(self, comment_id: uuid.UUID) -> Optional[Comment]:
        """Get a specific comment by ID."""
        try:
            comment = self._db.query(Comment).filter(Comment.id == comment_id).first()
            return comment
        except Exception as e:
            logger.error(f"Error fetching comment {comment_id}: {str(e)}")
            return None
    
    def get_comment_replies(self, comment_id: uuid.UUID) -> List[Reply]:
        """Get all replies for a specific comment."""
        try:
            replies = self._db.query(Reply)\
                .filter(Reply.comment_id == comment_id)\
                .order_by(Reply.created_at)\
                .all()
            return replies
        except Exception as e:
            logger.error(f"Error fetching replies for comment {comment_id}: {str(e)}")
            return []
    
    def create_comment(self, prompt_id: uuid.UUID, content: str, 
                      created_by: uuid.UUID) -> Tuple[Optional[Comment], Optional[str]]:
        """Create a new comment on a prompt."""
        try:
            # Verify that the prompt exists
            prompt = self._db.query(Prompt).filter(Prompt.id == prompt_id).first()
            if not prompt:
                return None, "Prompt not found"
            
            # Create the comment
            comment = Comment(
                content=content,
                prompt_id=prompt_id,
                created_by=created_by,
                updated_by=created_by
            )
            
            self._db.add(comment)
            self._db.commit()
            
            return comment, None
        except Exception as e:
            self._db.rollback()
            logger.error(f"Error creating comment: {str(e)}")
            return None, f"Failed to create comment: {str(e)}"
    
    def create_reply(self, comment_id: uuid.UUID, content: str, 
                    created_by: uuid.UUID) -> Tuple[Optional[Reply], Optional[str]]:
        """Create a new reply to a comment."""
        try:
            # Verify that the comment exists
            comment = self._db.query(Comment).filter(Comment.id == comment_id).first()
            if not comment:
                return None, "Comment not found"
            
            # Create the reply
            reply = Reply(
                content=content,
                comment_id=comment_id,
                created_by=created_by,
                updated_by=created_by
            )
            
            self._db.add(reply)
            self._db.commit()
            
            return reply, None
        except Exception as e:
            self._db.rollback()
            logger.error(f"Error creating reply: {str(e)}")
            return None, f"Failed to create reply: {str(e)}"
    
    def update_comment(self, comment_id: uuid.UUID, content: str, 
                      updated_by: uuid.UUID) -> Tuple[Optional[Comment], Optional[str]]:
        """Update an existing comment."""
        try:
            comment = self._db.query(Comment).filter(Comment.id == comment_id).first()
            if not comment:
                return None, "Comment not found"
            
            # Check if the user is the comment creator
            if comment.created_by != updated_by:
                return None, "You can only edit your own comments"
            
            comment.content = content
            comment.updated_by = updated_by
            comment.updated_at = datetime.utcnow()
            comment.is_edited = True
            
            self._db.commit()
            
            return comment, None
        except Exception as e:
            self._db.rollback()
            logger.error(f"Error updating comment: {str(e)}")
            return None, f"Failed to update comment: {str(e)}"
    
    def update_reply(self, reply_id: uuid.UUID, content: str, 
                    updated_by: uuid.UUID) -> Tuple[Optional[Reply], Optional[str]]:
        """Update an existing reply."""
        try:
            reply = self._db.query(Reply).filter(Reply.id == reply_id).first()
            if not reply:
                return None, "Reply not found"
            
            # Check if the user is the reply creator
            if reply.created_by != updated_by:
                return None, "You can only edit your own replies"
            
            reply.content = content
            reply.updated_by = updated_by
            reply.updated_at = datetime.utcnow()
            reply.is_edited = True
            
            self._db.commit()
            
            return reply, None
        except Exception as e:
            self._db.rollback()
            logger.error(f"Error updating reply: {str(e)}")
            return None, f"Failed to update reply: {str(e)}"
    
    def delete_comment(self, comment_id: uuid.UUID, user_id: uuid.UUID) -> Tuple[bool, Optional[str]]:
        """Delete a comment and all its replies."""
        try:
            comment = self._db.query(Comment).filter(Comment.id == comment_id).first()
            if not comment:
                return False, "Comment not found"
            
            # Check if the user is the comment creator
            if comment.created_by != user_id:
                return False, "You can only delete your own comments"
            
            # Delete will cascade to replies
            self._db.delete(comment)
            self._db.commit()
            
            return True, None
        except Exception as e:
            self._db.rollback()
            logger.error(f"Error deleting comment: {str(e)}")
            return False, f"Failed to delete comment: {str(e)}"
    
    def delete_reply(self, reply_id: uuid.UUID, user_id: uuid.UUID) -> Tuple[bool, Optional[str]]:
        """Delete a reply."""
        try:
            reply = self._db.query(Reply).filter(Reply.id == reply_id).first()
            if not reply:
                return False, "Reply not found"
            
            # Check if the user is the reply creator
            if reply.created_by != user_id:
                return False, "You can only delete your own replies"
            
            self._db.delete(reply)
            self._db.commit()
            
            return True, None
        except Exception as e:
            self._db.rollback()
            logger.error(f"Error deleting reply: {str(e)}")
            return False, f"Failed to delete reply: {str(e)}"
    
    def pin_comment(self, comment_id: uuid.UUID, pin: bool = True) -> Tuple[Optional[Comment], Optional[str]]:
        """Pin or unpin a comment."""
        try:
            comment = self._db.query(Comment).filter(Comment.id == comment_id).first()
            if not comment:
                return None, "Comment not found"
            
            comment.is_pinned = pin
            self._db.commit()
            
            return comment, None
        except Exception as e:
            self._db.rollback()
            logger.error(f"Error {'pinning' if pin else 'unpinning'} comment: {str(e)}")
            return None, f"Failed to {'pin' if pin else 'unpin'} comment: {str(e)}"
    
    def format_comment_data(self, comment: Comment) -> Dict[str, Any]:
        """Format a comment object for API response."""
        user = self._db.query(User).filter(User.id == comment.created_by).first()
        return {
            "id": str(comment.id),
            "content": comment.content,
            "created_at": comment.created_at.isoformat(),
            "updated_at": comment.updated_at.isoformat(),
            "created_by": user.username if user else "Unknown",
            "created_by_id": str(comment.created_by),
            "is_edited": comment.is_edited,
            "is_pinned": comment.is_pinned,
            "user_color": self._generate_user_color(str(comment.created_by)),
            "replies_count": len(comment.replies)
        }
    
    def format_reply_data(self, reply: Reply) -> Dict[str, Any]:
        """Format a reply object for API response."""
        user = self._db.query(User).filter(User.id == reply.created_by).first()
        return {
            "id": str(reply.id),
            "content": reply.content,
            "created_at": reply.created_at.isoformat(),
            "updated_at": reply.updated_at.isoformat(),
            "created_by": user.username if user else "Unknown",
            "created_by_id": str(reply.created_by),
            "is_edited": reply.is_edited,
            "user_color": self._generate_user_color(str(reply.created_by))
        }
    
    def _generate_user_color(self, user_id: str) -> str:
        """Generate a consistent color based on user ID."""
        # Simple hash function to generate a color
        hash_val = 0
        for char in user_id:
            hash_val = (hash_val * 31 + ord(char)) & 0xFFFFFFFF
        
        # Generate pastel colors for better readability on white background
        r = ((hash_val & 0xFF0000) >> 16) % 156 + 100
        g = ((hash_val & 0x00FF00) >> 8) % 156 + 100
        b = (hash_val & 0x0000FF) % 156 + 100
        
        return f"#{r:02x}{g:02x}{b:02x}" 