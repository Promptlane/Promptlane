"""
User management operations and business logic
"""
from sqlalchemy.orm import Session
import bcrypt
from datetime import datetime, timedelta
import uuid
from typing import Optional, List, Dict, Any, Tuple
import secrets
import logging
from sqlalchemy import or_
from app.db import models
from app.models.activity import UserStats, UserActivity
from app.db.models import User, TeamMember, Activity, ActivityType
from app.db.database import db
from app.managers.base_manager import BaseManager
import jwt
from app.config import settings

logger = logging.getLogger(__name__)

class UserManager(BaseManager):
    """Manager class for handling user-related operations"""
    
    def __init__(self, db_session: Optional[Session] = None):
        super().__init__(models.User, db_session)

    def get_user(self, user_id: uuid.UUID) -> Optional[models.User]:
        """Get a user by ID"""
        return self.get(user_id)

    def get_user_by_username(self, username: str) -> Optional[models.User]:
        """Get a user by username"""
        return self.get_by_field('username', username)

    def get_user_by_email(self, email: str) -> Optional[models.User]:
        """Get a user by email"""
        return self.get_by_field('email', email)

    def get_user_by_invitation_token(self, token: str) -> Optional[models.User]:
        """Get a user by their invitation token"""
        return self.get_by_field('invitation_token', token)

    def get_users(self, skip: int = 0, limit: int = 100) -> List[models.User]:
        """Get all users with pagination"""
        return self.get_multi(skip, limit)

    def get_active_users(self, days: int = 30) -> List[models.User]:
        """Get users who have been active in the last N days"""
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        return self.filter(last_login__gte=cutoff_date)

    def get_all_users(self) -> List[models.User]:
        """Get all users (admin only)"""
        return self.get_multi()

    def create_user(
        self,
        username: str,
        email: str,
        password: str,
        is_admin: bool = False,
        invitation_token: Optional[str] = None
    ) -> Tuple[Optional[models.User], Optional[str]]:
        """Create a new user"""
        try:
            # Check if username or email already exists
            if self.get_user_by_username(username):
                return None, "Username already exists"
            if self.get_user_by_email(email):
                return None, "Email already exists"

            # Hash the password
            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            
            user = self.create({
                'username': username,
                'email': email,
                'hashed_password': hashed_password.decode('utf-8'),
                'is_admin': is_admin,
                'invitation_token': invitation_token,
                'status': 'active',
                'created_at': datetime.utcnow()
            })

            if not user:
                return None, "Failed to create user"

            # Log activity
            self._log_activity(user.id, ActivityType.CREATE_USER, {"username": username})

            return user, None
        except Exception as e:
            logger.error(f"Error creating user: {str(e)}")
            return None, str(e)

    def update_user(
        self,
        user_id: uuid.UUID,
        username: Optional[str] = None,
        email: Optional[str] = None,
        password: Optional[str] = None,
        is_admin: Optional[bool] = None
    ) -> Tuple[Optional[models.User], Optional[str]]:
        """Update a user"""
        try:
            user = self.get_user(user_id)
            if not user:
                return None, "User not found"

            # Update fields
            update_data = {}
            if username is not None:
                update_data['username'] = username
            if email is not None:
                update_data['email'] = email
            if password is not None:
                hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
                update_data['hashed_password'] = hashed_password.decode('utf-8')
            if is_admin is not None:
                update_data['is_admin'] = is_admin
            update_data['updated_at'] = datetime.utcnow()

            updated_user = self.update(user, update_data)
            if not updated_user:
                return None, "Failed to update user"

            # Log activity
            self._log_activity(user_id, ActivityType.UPDATE_USER, {
                "updated_fields": [k for k, v in update_data.items() if v is not None]
            })

            return updated_user, None
        except Exception as e:
            logger.error(f"Error updating user: {str(e)}")
            return None, str(e)

    def delete_user(self, user_id: uuid.UUID) -> Tuple[bool, Optional[str]]:
        """Delete a user"""
        try:
            user = self.get_user(user_id)
            if not user:
                return False, "User not found"

            # Delete user's team memberships
            self._db.query(TeamMember).filter(TeamMember.user_id == user_id).delete()

            # Delete user's activities
            self._db.query(Activity).filter(Activity.user_id == user_id).delete()

            # Delete user
            success = self.delete(user_id)
            if not success:
                return False, "Failed to delete user"

            # Log activity
            self._log_activity(user_id, ActivityType.DELETE_USER, {"username": user.username})

            return True, None
        except Exception as e:
            logger.error(f"Error deleting user: {str(e)}")
            return False, str(e)

    def verify_password(self, user: models.User, password: str) -> bool:
        """Verify a user's password"""
        try:
            return bcrypt.checkpw(password.encode('utf-8'), user.hashed_password.encode('utf-8'))
        except Exception as e:
            logger.error(f"Error verifying password: {str(e)}")
            return False

    def generate_invitation_token(self) -> str:
        """Generate a secure invitation token"""
        return secrets.token_urlsafe(32)

    def create_invitation(
        self,
        username: str,
        email: str,
        is_admin: bool = False,
        expiry_hours: int = 48
    ) -> Tuple[Optional[models.User], str, str]:
        """Create a user invitation with a token that expires"""
        try:
            # Check if username or email already exists
            if self.get_user_by_username(username):
                return None, "Username already exists", ""
            if self.get_user_by_email(email):
                return None, "Email already exists", ""

            # Generate invitation token
            invitation_token = self.generate_invitation_token()
            expiry_time = datetime.utcnow() + timedelta(hours=expiry_hours)

            # Create user
            user = self.create({
                'username': username,
                'email': email,
                'is_admin': is_admin,
                'status': 'invited',
                'invitation_token': invitation_token,
                'invitation_expiry': expiry_time,
                'created_at': datetime.utcnow()
            })

            if not user:
                return None, "Failed to create invitation", ""

            return user, "", invitation_token
        except Exception as e:
            logger.error(f"Error creating invitation: {str(e)}")
            return None, str(e), ""

    def reset_invitation(
        self,
        user_id: uuid.UUID,
        expiry_hours: int = 48
    ) -> Tuple[Optional[models.User], str, str]:
        """Reset a user's invitation token and expiry time"""
        try:
            user = self.get_user(user_id)
            if not user:
                return None, "User not found", ""

            if user.status != "invited":
                return None, "User is not in invited status", ""

            new_token = self.generate_invitation_token()
            expiry_time = datetime.utcnow() + timedelta(hours=expiry_hours)

            updated_user = self.update(user, {
                'invitation_token': new_token,
                'invitation_expiry': expiry_time
            })

            if not updated_user:
                return None, "Failed to reset invitation", ""

            return updated_user, "", new_token
        except Exception as e:
            logger.error(f"Error resetting invitation: {str(e)}")
            return None, str(e), ""

    def complete_invitation(
        self,
        token: str,
        password: str
    ) -> Tuple[Optional[models.User], str]:
        """Complete the invitation process by setting the user's password"""
        try:
            user = self.get_user_by_invitation_token(token)
            if not user:
                return None, "Invalid invitation token"

            if user.invitation_expiry and user.invitation_expiry < datetime.utcnow():
                return None, "Invitation has expired"

            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

            updated_user = self.update(user, {
                'hashed_password': hashed_password.decode('utf-8'),
                'status': 'active',
                'invitation_token': None,
                'invitation_expiry': None,
                'updated_at': datetime.utcnow()
            })

            if not updated_user:
                return None, "Failed to complete invitation"

            return updated_user, ""
        except Exception as e:
            logger.error(f"Error completing invitation: {str(e)}")
            return None, str(e)

    def verify_user(self, username: str, password: str) -> Optional[models.User]:
        """Verify user credentials"""
        try:
            user = self.get_user_by_username(username)
            if not user or user.status != "active":
                return None

            if self.verify_password(user, password):
                return user
            return None
        except Exception as e:
            logger.error(f"Error verifying user: {str(e)}")
            return None

    def set_user_admin_status(self, user_id: uuid.UUID, is_admin: bool) -> Tuple[Optional[models.User], Optional[str]]:
        """Set a user's admin status"""
        try:
            user = self.get_user(user_id)
            if not user:
                return None, "User not found"

            updated_user = self.update(user, {
                'is_admin': is_admin,
                'updated_at': datetime.utcnow()
            })

            if not updated_user:
                return None, "Failed to update admin status"

            # Log activity
            self._log_activity(user_id, ActivityType.UPDATE_USER, {
                "action": "admin_status_change",
                "is_admin": is_admin
            })

            return updated_user, None
        except Exception as e:
            logger.error(f"Error setting admin status: {str(e)}")
            return None, str(e)

    def get_username(self, user_id: uuid.UUID) -> str:
        """Get username for the given user ID"""
        user = self.get_user(user_id)
        return user.username if user else "Unknown User"

    def search_users(self, query: str, limit: int = 10) -> List[models.User]:
        """Search users by name or email"""
        return self._db.query(models.User).filter(
            or_(
                models.User.name.ilike(f"%{query}%"),
                models.User.email.ilike(f"%{query}%")
            )
        ).limit(limit).all()

    def _log_activity(self, user_id: str, activity_type: ActivityType, details: dict):
        """Log user activity"""
        try:
            activity = Activity(
                id=str(uuid.uuid4()),
                user_id=user_id,
                activity_type=activity_type,
                details=details,
                created_at=datetime.utcnow()
            )
            self._db.add(activity)
            self._db.commit()
        except Exception as e:
            logger.error(f"Error logging activity: {str(e)}")
            self._db.rollback()

    def generate_token(self, user: User) -> str:
        """Generate JWT token for user"""
        payload = {
            "user_id": str(user.id),
            "exp": datetime.utcnow() + timedelta(minutes=settings.SECURITY.JWT_ACCESS_TOKEN_EXPIRE_MINUTES),
            "iat": datetime.utcnow()
        }
        return jwt.encode(
            payload,
            settings.SECURITY.JWT_SECRET_KEY,
            algorithm=settings.SECURITY.JWT_ALGORITHM
        )
    
    def verify_token(self, token: str) -> Optional[User]:
        """Verify JWT token and return user if valid"""
        try:
            payload = jwt.decode(token, settings.SECURITY.JWT_SECRET_KEY, algorithms=["HS256"])
            user_id = payload.get("user_id")
            if not user_id:
                return None
            return self.get_user(user_id)
        except jwt.InvalidTokenError:
            return None 