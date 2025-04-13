"""
Project management operations and business logic
"""
from sqlalchemy.orm import Session
import uuid
from typing import Optional, List, Dict, Any, Tuple
from app.db import models
from datetime import datetime
from app.models.team import TeamRole
from app.db.database import db
from app.managers.base_manager import BaseManager
import logging

logger = logging.getLogger(__name__)

class ProjectManager(BaseManager):
    """Manager class for handling project-related operations"""
    
    def __init__(self, db_session: Optional[Session] = None):
        super().__init__(models.Project, db_session)

    def get_project(self, project_id: uuid.UUID) -> Optional[models.Project]:
        """Get a project by ID"""
        return self.get(project_id)

    def get_project_by_key(self, key: str) -> Optional[models.Project]:
        """Get a project by key"""
        return self.get_by_field('key', key)

    def get_all_projects(self) -> List[models.Project]:
        """Get all projects (admin only)"""
        return self.get_multi()

    def create_project(
        self,
        project_key: str,
        name: str,
        description: str,
        created_by: uuid.UUID
    ) -> Tuple[Optional[models.Project], str]:
        """Create a new project"""
        try:
            # Check if project key already exists
            existing_project = self.get_project_by_key(project_key)
            if existing_project:
                return None, "Project key already exists"

            # Create project
            project = self.create({
                'id': str(uuid.uuid4()),
                'key': project_key,
                'name': name,
                'description': description,
                'created_by': created_by,
                'created_at': datetime.utcnow()
            })

            if not project:
                return None, "Failed to create project"

            # Log activity
            self._log_activity(created_by, models.ActivityType.CREATE_PROJECT, {
                "project_id": project.id,
                "name": name,
                "key": project_key
            })

            return project, ""
        except Exception as e:
            logger.error(f"Error creating project: {str(e)}")
            return None, str(e)

    def update_project(
        self,
        project_id: uuid.UUID,
        name: Optional[str] = None,
        description: Optional[str] = None,
        updated_by: Optional[uuid.UUID] = None
    ) -> Tuple[Optional[models.Project], str]:
        """Update a project"""
        try:
            project = self.get_project(project_id)
            if not project:
                return None, "Project not found"

            # Update fields
            update_data = {}
            if name is not None:
                update_data['name'] = name
            if description is not None:
                update_data['description'] = description
            if updated_by is not None:
                update_data['updated_by'] = updated_by
                update_data['updated_at'] = datetime.utcnow()

            updated_project = self.update(project, update_data)
            if not updated_project:
                return None, "Failed to update project"

            # Log activity
            self._log_activity(updated_by or project.created_by, models.ActivityType.UPDATE_PROJECT, {
                "project_id": project_id,
                "updated_fields": [k for k, v in update_data.items() if v is not None]
            })

            return updated_project, ""
        except Exception as e:
            logger.error(f"Error updating project: {str(e)}")
            return None, str(e)

    def delete_project(self, project_id: uuid.UUID) -> bool:
        """Delete a project"""
        try:
            project = self.get_project(project_id)
            if not project:
                return False

            success = self.delete(project_id)
            if not success:
                return False

            # Log activity
            self._log_activity(project.created_by, models.ActivityType.DELETE_PROJECT, {
                "project_id": project_id,
                "name": project.name
            })

            return True
        except Exception as e:
            logger.error(f"Error deleting project: {str(e)}")
            return False

    def get_user_projects(self, user_id: uuid.UUID) -> List[models.Project]:
        """Get all projects for a user"""
        return self.get_multi_by_field('created_by', user_id)

    def check_project_permissions(
        self,
        project_id: uuid.UUID,
        user_id: uuid.UUID
    ) -> Dict[str, Any]:
        """Check user permissions for a project"""
        try:
            project = self.get_project(project_id)
            if not project:
                return {"has_access": False, "is_owner": False}

            # Check if user is the project owner
            is_owner = project.created_by == user_id

            return {
                "has_access": is_owner,  # For now, only owners have access
                "is_owner": is_owner
            }
        except Exception as e:
            logger.error(f"Error checking project permissions: {str(e)}")
            return {"has_access": False, "is_owner": False}

    def _log_activity(self, user_id: uuid.UUID, activity_type: models.ActivityType, details: Dict[str, Any]):
        """Log project activity"""
        try:
            activity = models.Activity(
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