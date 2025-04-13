"""
Activity management operations and business logic
"""
from sqlalchemy.orm import Session
import uuid
from typing import Optional, List, Dict, Any, Tuple
from app.db import models
from sqlalchemy import func, desc
from datetime import datetime, timedelta
from app.models.activity import UserStats, UserActivity, ActivityType, ActivityResponse
from app.exceptions import ActivityCreationError
import json
from app.db.util import serialize_details
from app.db.database import get_db
from app.managers.base_manager import BaseManager
import logging

logger = logging.getLogger(__name__)

class ActivityManager(BaseManager):
    """Manager class for handling activity-related operations"""
    
    def __init__(self, db_session: Optional[Session] = None):
        super().__init__(models.Activity, db_session)

    def log_activity(
        self,
        user_id: uuid.UUID,
        activity_type: str,
        details: Dict[str, Any] = None,
        metadata: Dict[str, Any] = None
    ) -> models.Activity:
        """
        Log a user activity
        
        Args:
            user_id: User ID
            activity_type: Type of activity
            details: Additional activity details (optional)
            metadata: Alternative name for details (for backward compatibility)
            
        Returns:
            The created activity record
        """
        # Use metadata if details is None
        if details is None and metadata is not None:
            details = metadata
        
        # Convert UUIDs in details to strings for JSON serialization
        if details:
            details = serialize_details(details)
        
        # Create the activity record
        try:
            activity = models.Activity(
                user_id=user_id,
                activity_type=activity_type,
                details=details
            )
            self._db.add(activity)
            self._db.commit()
            self._db.refresh(activity)
            return activity
        except Exception as e:
            self._db.rollback()
            raise ActivityCreationError(f"Failed to create activity: {str(e)}")

    def get_recent_activities(self, limit: int = 10) -> List[models.Activity]:
        """Get the most recent activities across all users"""
        return self._db.query(models.Activity).order_by(desc(models.Activity.created_at)).limit(limit).all()

    def get_user_activities(
        self,
        user_id: uuid.UUID,
        skip: int = 0,
        limit: int = 100
    ) -> List[models.Activity]:
        """Get all activities for a user with pagination"""
        return self._db.query(models.Activity).filter(
            models.Activity.user_id == user_id
        ).offset(skip).limit(limit).all()

    def get_activity_by_type(self, user_id: uuid.UUID) -> Dict[str, int]:
        """Get count of activities by type for a user"""
        activities = self._db.query(
            models.Activity.activity_type,
            func.count(models.Activity.id).label("count")
        ).filter(
            models.Activity.user_id == user_id
        ).group_by(
            models.Activity.activity_type
        ).all()
        
        return {activity_type: count for activity_type, count in activities}

    def get_activity_by_date(self, user_id: uuid.UUID, days: int = 30) -> List[UserActivity]:
        """
        Get user activity counts by date for the specified number of days
        Returns a list of UserActivity objects with date and count
        """
        start_date = datetime.utcnow() - timedelta(days=days)
        
        activities_by_date = self._db.query(
            func.date_trunc('day', models.Activity.created_at).label('date'),
            func.count(models.Activity.id).label('count')
        ).filter(
            models.Activity.user_id == user_id,
            models.Activity.created_at >= start_date
        ).group_by(
            func.date_trunc('day', models.Activity.created_at)
        ).order_by(
            func.date_trunc('day', models.Activity.created_at)
        ).all()
        
        return [
            UserActivity(
                date=date.strftime('%Y-%m-%d'),
                count=count
            )
            for date, count in activities_by_date
        ]

    def get_user_stats(self, user_id: uuid.UUID) -> Dict[str, Any]:
        """Get statistics for a user"""
        total_activities = self._db.query(models.Activity).filter(
            models.Activity.user_id == user_id
        ).count()
        
        activities_by_type = self.count_user_activities_by_type(user_id)
        activities_by_date = self.count_user_activities_by_date(user_id, days=7)
        
        return {
            "total_activities": total_activities,
            "activities_by_type": activities_by_type,
            "activities_by_date": activities_by_date
        }

    def get_activity(self, activity_id: uuid.UUID) -> Optional[models.Activity]:
        """Get an activity by ID"""
        return self._db.query(models.Activity).filter(models.Activity.id == activity_id).first()

    def create_activity(
        self,
        user_id: uuid.UUID,
        activity_type: str,
        details: Optional[Dict[str, Any]] = None
    ) -> models.Activity:
        """Create a new activity"""
        try:
            db_activity = models.Activity(
                id=uuid.uuid4(),
                user_id=user_id,
                activity_type=activity_type,
                details=details or {}
            )
            
            self._db.add(db_activity)
            self._db.commit()
            self._db.refresh(db_activity)
            
            return db_activity
        except Exception as e:
            self._db.rollback()
            raise ActivityCreationError(f"Failed to create activity: {str(e)}")

    def get_user_activities_by_type(
        self,
        user_id: uuid.UUID,
        activity_type: str
    ) -> List[models.Activity]:
        """Get activities of a specific type for a user"""
        return self._db.query(models.Activity).filter(
            models.Activity.user_id == user_id,
            models.Activity.activity_type == activity_type
        ).order_by(desc(models.Activity.created_at)).all()

    def count_user_activities_by_type(
        self,
        user_id: uuid.UUID
    ) -> List[Dict[str, Any]]:
        """Count activities by type for a user"""
        return self._db.query(
            models.Activity.activity_type,
            func.count(models.Activity.id).label('count')
        ).filter(
            models.Activity.user_id == user_id
        ).group_by(
            models.Activity.activity_type
        ).all()

    def count_user_activities_by_date(
        self,
        user_id: uuid.UUID,
        days: int = 30
    ) -> List[Dict[str, Any]]:
        """Count activities by date for a user over the past specified days"""
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        return self._db.query(
            func.date_trunc('day', models.Activity.created_at).label('date'),
            func.count(models.Activity.id).label('count')
        ).filter(
            models.Activity.user_id == user_id,
            models.Activity.created_at >= cutoff_date
        ).group_by(
            func.date_trunc('day', models.Activity.created_at)
        ).all()

    def to_pydantic(self, activity: models.Activity) -> ActivityResponse:
        """Convert SQLAlchemy Activity model to Pydantic ActivityResponse model"""
        return ActivityResponse(
            id=str(activity.id),
            user_id=str(activity.user_id),
            activity_type=activity.activity_type,
            timestamp=activity.timestamp,
            details=activity.details
        )

    def create(
        self,
        user_id: uuid.UUID,
        action: str,
        resource_type: str,
        resource_id: Optional[uuid.UUID] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> models.Activity:
        """Create a new activity log entry"""
        try:
            activity = models.Activity(
                id=uuid.uuid4(),
                user_id=user_id,
                action=action,
                resource_type=resource_type,
                resource_id=resource_id,
                metadata=metadata or {},
                created_at=datetime.utcnow()
            )
            
            self._db.add(activity)
            self._db.commit()
            self._db.refresh(activity)
            
            return activity
        except Exception as e:
            self._db.rollback()
            raise Exception(f"Failed to create activity: {str(e)}")

    def get_resource_activities(
        self,
        resource_type: str,
        resource_id: uuid.UUID,
        skip: int = 0,
        limit: int = 100
    ) -> list[models.Activity]:
        """Get activities for a specific resource"""
        return self._db.query(models.Activity).filter(
            models.Activity.resource_type == resource_type,
            models.Activity.resource_id == resource_id
        ).order_by(
            models.Activity.created_at.desc()
        ).offset(skip).limit(limit).all()

    def get_project_activities(
        self,
        project_id: uuid.UUID,
        skip: int = 0,
        limit: int = 100
    ) -> List[models.Activity]:
        """Get activities for a project with pagination"""
        return self._db.query(models.Activity).filter(
            models.Activity.project_id == project_id
        ).offset(skip).limit(limit).all()

    def get_recent_activities(
        self,
        user_id: Optional[uuid.UUID] = None,
        project_id: Optional[uuid.UUID] = None,
        limit: int = 50
    ) -> List[models.Activity]:
        """Get recent activities with optional filtering"""
        try:
            query = self._db.query(models.Activity)
            
            if user_id:
                query = query.filter(models.Activity.user_id == user_id)
            if project_id:
                query = query.filter(models.Activity.project_id == project_id)
            
            return query.order_by(models.Activity.created_at.desc()).limit(limit).all()
        except Exception as e:
            logger.error(f"Error getting recent activities: {str(e)}")
            return []

    def get_activity_stats(
        self,
        user_id: Optional[uuid.UUID] = None,
        project_id: Optional[uuid.UUID] = None,
        days: int = 30
    ) -> Dict[str, Any]:
        """Get activity statistics for a time period"""
        try:
            start_date = datetime.utcnow() - timedelta(days=days)
            
            query = self._db.query(models.Activity)
            
            if user_id:
                query = query.filter(models.Activity.user_id == user_id)
            if project_id:
                query = query.filter(models.Activity.project_id == project_id)
            
            query = query.filter(models.Activity.created_at >= start_date)
            
            # Get total count
            total_count = query.count()
            
            # Get counts by activity type
            type_counts = {}
            for activity_type in models.ActivityType:
                count = query.filter(models.Activity.activity_type == activity_type).count()
                type_counts[activity_type.name] = count
            
            return {
                "total_count": total_count,
                "type_counts": type_counts,
                "period_days": days
            }
        except Exception as e:
            logger.error(f"Error getting activity stats: {str(e)}")
            return {
                "total_count": 0,
                "type_counts": {},
                "period_days": days
            } 