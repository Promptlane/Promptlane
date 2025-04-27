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
from sqlalchemy.orm import joinedload

logger = logging.getLogger(__name__)

class PromptManager(BaseManager):
    """Manager class for handling prompt-related operations"""
    
    def __init__(self, db_session: Optional[Session] = None):
        super().__init__(models.Prompt, db_session)

    def get_prompt(self, prompt_id: uuid.UUID) -> Optional[models.Prompt]:
        """Get a prompt by ID with its versions"""
        try:
            logger.info(f"Getting prompt with ID: {prompt_id}")
            
            # First, get the prompt by ID
            prompt = self._db.query(self.model_class)\
                .filter(self.model_class.id == prompt_id)\
                .first()
                
            if not prompt:
                logger.warning(f"Prompt not found: {prompt_id}")
                return None
                
            logger.debug(f"Found prompt: id={prompt.id}, name={prompt.name}, " + 
                       f"parent_id={prompt.parent_id}, version={getattr(prompt, 'version', 'N/A')}")
            
            # Find the original root parent by traversing up
            current = prompt
            root_parent = current
            
            # Traverse up the parent chain to find the root (v1)
            while current.parent_id is not None:
                logger.debug(f"Traversing up from version {current.version} to parent")
                parent = self._db.query(self.model_class)\
                    .filter(self.model_class.id == current.parent_id)\
                    .first()
                
                if not parent:
                    logger.warning(f"Parent not found for prompt {current.id}")
                    break
                
                root_parent = parent
                current = parent
                logger.debug(f"Found parent: id={parent.id}, version={parent.version}")
            
            logger.info(f"Found root parent: id={root_parent.id}, version={root_parent.version}")
            
            # Get ALL descendants at all levels using recursive CTE (Common Table Expression)
            # This is the most efficient way to get the entire hierarchy
            versions = []
            version_ids = set()
            
            # First add the root parent (version 1)
            versions.append(root_parent)
            version_ids.add(root_parent.id)
            
            # Function to recursively collect all descendants
            def collect_descendants(parent_id, indent=1):
                children = self._db.query(self.model_class)\
                    .filter(self.model_class.parent_id == parent_id)\
                    .all()
                
                for child in children:
                    if child.id not in version_ids:
                        versions.append(child)
                        version_ids.add(child.id)
                        logger.debug(f"{'  ' * indent}Added child: id={child.id}, version={child.version}")
                        # Recursively get this child's children
                        collect_descendants(child.id, indent + 1)
            
            # Start collecting from the root
            logger.debug(f"Starting to collect all descendants from root parent: {root_parent.id}")
            collect_descendants(root_parent.id)
            
            # Log the full version list
            version_info = [{"id": str(v.id), "version": v.version} for v in versions]
            logger.info(f"Complete versions list: {version_info}")
            
            # Attach the versions list to the prompt
            prompt.versions = versions
            
            logger.info(f"Returning prompt with {len(versions)} total versions")
            return prompt
                
        except Exception as e:
            logger.error(f"Error getting prompt with versions: {str(e)}")
            return None

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
        system_prompt: Optional[str] = None,
        user_prompt: Optional[str] = None,
        is_active: Optional[bool] = None,
        updated_by: Optional[uuid.UUID] = None,
        create_new_version: bool = False
    ) -> Tuple[Optional[models.Prompt], str]:
        """Update a prompt or create a new version"""
        try:
            logger.info(f"Updating prompt {prompt_id} (create_new_version={create_new_version})")
            logger.debug(f"Update params - name: {name}, system_prompt: {system_prompt and len(system_prompt)}, " +
                        f"user_prompt: {user_prompt and len(user_prompt)}, updated_by: {updated_by}")
            
            prompt = self.get_prompt(prompt_id)
            if not prompt:
                logger.error(f"Prompt {prompt_id} not found")
                return None, "Prompt not found"
                
            logger.debug(f"Found prompt: id={prompt.id}, name={prompt.name}, " +
                         f"has version attr: {hasattr(prompt, 'version')}, " +
                         f"has is_active attr: {hasattr(prompt, 'is_active')}")

            if create_new_version:
                logger.info(f"Creating new version of prompt {prompt_id}")
                # Create a new version of the prompt
                current_version = prompt.version if hasattr(prompt, "version") else 1
                logger.debug(f"Current version: {current_version}, new version will be: {current_version + 1}")
                
                # Get the root parent's key
                root_parent = prompt
                while root_parent.parent_id:
                    root_parent = self.get_prompt(root_parent.parent_id)
                
                # Create a new prompt with the original as the parent
                new_prompt_data = {
                    'id': str(uuid.uuid4()),
                    'project_id': prompt.project_id,
                    'key': f"{root_parent.key}_v{current_version + 1}",  # Use root parent's key
                    'name': name or prompt.name,
                    'description': description or prompt.description,
                    'system_prompt': system_prompt or prompt.system_prompt,
                    'user_prompt': user_prompt or prompt.user_prompt,
                    'is_active': True,  # New version is active by default
                    'version': current_version + 1,  # Increment version
                    'parent_id': str(prompt_id),  # Set parent ID to original prompt
                    'created_by': updated_by or prompt.created_by,
                    'created_at': datetime.utcnow()
                }
                logger.debug(f"Creating new prompt with data: {new_prompt_data}")
                
                try:
                    new_prompt = self.create(new_prompt_data)
                    logger.debug(f"New prompt created: {new_prompt and new_prompt.id}")
                    
                    if not new_prompt:
                        logger.error("Failed to create new prompt version")
                        return None, "Failed to create new prompt version"
                    
                    # Deactivate all versions in the chain
                    logger.debug(f"Deactivating all versions in the chain for prompt {prompt_id}")
                    prompt.deactivate_all_versions(self._db)
                    
                    # Log activity
                    logger.debug(f"Logging activity for new prompt version: {new_prompt.id}")
                    self._log_activity(updated_by or prompt.created_by, models.ActivityType.CREATE_PROMPT_VERSION, {
                        "prompt_id": str(new_prompt.id),
                        "original_prompt_id": str(prompt_id),
                        "project_id": str(prompt.project_id),
                        "name": name or prompt.name,
                        "version": current_version + 1
                    })
                    
                    logger.info(f"Successfully created new prompt version: {new_prompt.id} (version {current_version + 1})")
                    return new_prompt, ""
                except Exception as inner_e:
                    logger.exception(f"Exception during new version creation: {str(inner_e)}")
                    return None, f"Error creating new version: {str(inner_e)}"
            else:
                logger.info(f"Updating existing prompt {prompt_id}")
                # Update fields
                update_data = {}
                if name is not None:
                    update_data['name'] = name
                if description is not None:
                    update_data['description'] = description
                if content is not None:
                    update_data['content'] = content
                if system_prompt is not None:
                    update_data['system_prompt'] = system_prompt
                if user_prompt is not None:
                    update_data['user_prompt'] = user_prompt
                if is_active is not None:
                    update_data['is_active'] = is_active
                if updated_by is not None:
                    update_data['updated_by'] = updated_by
                    update_data['updated_at'] = datetime.utcnow()

                logger.debug(f"Updating prompt with data: {update_data.keys()}")
                updated_prompt = self.update(prompt, update_data)
                if not updated_prompt:
                    logger.error("Failed to update prompt")
                    return None, "Failed to update prompt"

                # Log activity
                logger.debug(f"Logging activity for updated prompt: {prompt_id}")
                self._log_activity(updated_by or prompt.created_by, models.ActivityType.UPDATE_PROMPT, {
                    "prompt_id": prompt_id,
                    "project_id": prompt.project_id,
                    "updated_fields": [k for k, v in update_data.items() if v is not None]
                })

                logger.info(f"Successfully updated prompt: {prompt_id}")
                return updated_prompt, ""
        except Exception as e:
            logger.exception(f"Error updating prompt: {str(e)}")
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