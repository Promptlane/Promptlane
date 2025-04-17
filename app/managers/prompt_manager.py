"""
Prompt management operations and business logic
"""
from sqlalchemy.orm import Session
import uuid
from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime
from app.db import models
from app.exceptions import PromptCreationError, PromptNotFoundError, PromptUpdateError
from app.db.database import get_db
from app.managers.base_manager import BaseManager
import logging

logger = logging.getLogger(__name__)

class PromptManager(BaseManager):
    """Manager class for handling prompt-related operations"""
    
    def __init__(self, db_session: Optional[Session] = None):
        super().__init__(models.Prompt, db_session)

    def get_prompt(self, prompt_id: uuid.UUID) -> Optional[models.Prompt]:
        """Get a prompt by ID"""
        return self.get(prompt_id)

    def get_prompt_by_key(self, key: str) -> Optional[models.Prompt]:
        """Get a prompt by key"""
        return self.get_by_field('key', key)

    def get_all_prompts(self, skip: int = 0, limit: int = 100) -> List[models.Prompt]:
        """Get all prompts with pagination"""
        return self.get_multi(skip=skip, limit=limit)

    def create_prompt(
        self,
        project_id: uuid.UUID,
        key: str,
        name: str,
        description: str,
        system_prompt: str,
        user_prompt: str,
        created_by: uuid.UUID
    ) -> Tuple[Optional[models.Prompt], str]:
        """Create a new prompt"""
        try:
            # Check if prompt key already exists in the project
            existing_prompt = self.get_prompt_by_key(key)
            if existing_prompt and existing_prompt.project_id == project_id:
                return None, "Prompt key already exists in this project"

            # Create prompt
            prompt = self.create({
                'id': str(uuid.uuid4()),
                'project_id': project_id,
                'key': key,
                'name': name,
                'description': description,
                'system_prompt': system_prompt,
                'user_prompt': user_prompt,
                'created_by': created_by,
                'created_at': datetime.utcnow()
            })

            if not prompt:
                return None, "Failed to create prompt"

            # Log activity
            self._log_activity(created_by, models.ActivityType.CREATE_PROMPT, {
                "prompt_id": prompt.id,
                "project_id": project_id,
                "name": name,
                "key": key
            })

            return prompt, ""
        except Exception as e:
            logger.error(f"Error creating prompt: {str(e)}")
            return None, str(e)

    def update_prompt(
        self,
        prompt_id: uuid.UUID,
        name: Optional[str] = None,
        description: Optional[str] = None,
        content: Optional[str] = None,
        updated_by: Optional[uuid.UUID] = None
    ) -> Tuple[Optional[models.Prompt], str]:
        """Update a prompt"""
        try:
            prompt = self.get_prompt(prompt_id)
            if not prompt:
                return None, "Prompt not found"

            # Update fields
            update_data = {}
            if name is not None:
                update_data['name'] = name
            if description is not None:
                update_data['description'] = description
            if content is not None:
                update_data['content'] = content
            if updated_by is not None:
                update_data['updated_by'] = updated_by
                update_data['updated_at'] = datetime.utcnow()

            updated_prompt = self.update(prompt, update_data)
            if not updated_prompt:
                return None, "Failed to update prompt"

            # Log activity
            self._log_activity(updated_by or prompt.created_by, models.ActivityType.UPDATE_PROMPT, {
                "prompt_id": prompt_id,
                "project_id": prompt.project_id,
                "updated_fields": [k for k, v in update_data.items() if v is not None]
            })

            return updated_prompt, ""
        except Exception as e:
            logger.error(f"Error updating prompt: {str(e)}")
            return None, str(e)

    def delete_prompt(self, prompt_id: uuid.UUID) -> bool:
        """Delete a prompt"""
        try:
            prompt = self.get_prompt(prompt_id)
            if not prompt:
                return False

            success = self.delete(prompt_id)
            if not success:
                return False

            # Log activity
            self._log_activity(prompt.created_by, models.ActivityType.DELETE_PROMPT, {
                "prompt_id": prompt_id,
                "project_id": prompt.project_id,
                "name": prompt.name
            })

            return True
        except Exception as e:
            logger.error(f"Error deleting prompt: {str(e)}")
            return False

    def get_project_prompts(self, project_id: uuid.UUID) -> List[models.Prompt]:
        """Get all prompts for a project"""
        return self.get_multi_by_field('project_id', project_id)

    def get_prompts_by_tag(self, tag: str) -> List[models.Prompt]:
        """Get all prompts with a specific tag"""
        try:
            return self.get_multi_by_field('tags', tag)
        except Exception as e:
            raise PromptCreationError(f"Failed to get prompts by tag: {str(e)}")

    def search_prompts(
        self,
        query: str,
        project_id: Optional[uuid.UUID] = None,
        tags: Optional[List[str]] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[models.Prompt]:
        """Search prompts by query string, optionally filtered by project and tags"""
        try:
            # Start with base query
            base_query = self.get_multi()
            
            # Add search conditions
            search_conditions = []
            
            # Add text search conditions
            search_conditions.append(
                (models.Prompt.name.ilike(f"%{query}%")) |
                (models.Prompt.description.ilike(f"%{query}%")) |
                (models.Prompt.content.ilike(f"%{query}%"))
            )
            
            # Add project filter if specified
            if project_id:
                search_conditions.append(models.Prompt.project_id == project_id)
            
            # Add tag filters if specified
            if tags:
                for tag in tags:
                    search_conditions.append(models.Prompt.tags.contains([tag]))
            
            # Apply all conditions
            if search_conditions:
                base_query = base_query.filter(*search_conditions)
            
            # Apply pagination
            return base_query.offset(skip).limit(limit).all()
        except Exception as e:
            raise PromptCreationError(f"Failed to search prompts: {str(e)}")

    def check_prompt_permissions(
        self,
        prompt_id: uuid.UUID,
        user_id: uuid.UUID
    ) -> Dict[str, Any]:
        """Check user permissions for a prompt"""
        try:
            prompt = self.get_prompt(prompt_id)
            if not prompt:
                return {"has_access": False, "is_owner": False}

            # Check if user is the prompt owner
            is_owner = prompt.created_by == user_id

            return {
                "has_access": is_owner,  # For now, only owners have access
                "is_owner": is_owner
            }
        except Exception as e:
            logger.error(f"Error checking prompt permissions: {str(e)}")
            return {"has_access": False, "is_owner": False}

    def get_all_prompts(self) -> List[models.Prompt]:
        """Get all prompts (admin only)"""
        return self.get_multi()

    def get_project_prompts_count(self, project_id: uuid.UUID) -> int:
        """Get the count of prompts in a project"""
        prompts = self.get_multi_by_field('project_id', project_id)
        return len(prompts)

    def _log_activity(self, user_id: uuid.UUID, activity_type: models.ActivityType, details: Dict[str, Any]):
        """Log prompt activity"""
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