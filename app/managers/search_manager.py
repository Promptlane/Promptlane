from typing import List, Dict, Optional, Tuple
from sqlalchemy import or_, and_
from sqlalchemy.orm import Session
from app.managers.base_manager import BaseManager
from app.managers.project_manager import ProjectManager
from app.managers.prompt_manager import PromptManager
from app.utils import format_date, extract_variables

class SearchManager:
    def __init__(self, session: Session):
        self.session = session
        self.project_manager = ProjectManager(session)
        self.prompt_manager = PromptManager(session)
        
    def search(
        self,
        query: Optional[str] = None,
        search_type: str = "all",
        page: int = 1,
        per_page: int = 10
    ) -> Tuple[List[Dict], List[Dict], Dict]:
        """Search for projects and prompts with pagination
        
        Args:
            query: Search query string
            search_type: Type of search ('all', 'projects', 'prompts')
            page: Page number
            per_page: Items per page
            
        Returns:
            Tuple containing:
            - List of projects
            - List of prompts
            - Pagination info
        """
        projects = []
        prompts = []
        offset = (page - 1) * per_page

        if search_type in ["all", "projects"]:
            # Build efficient project search query
            project_query = self.project_manager.get_multi_with_relationships('creator')
            
            if query:
                # Use SQLAlchemy's or_ for efficient text search
                project_query = project_query.filter(
                    or_(
                        self.project_manager.model_class.name.ilike(f"%{query}%"),
                        self.project_manager.model_class.description.ilike(f"%{query}%")
                    )
                )
            
            # Add pagination
            project_query = project_query.offset(offset).limit(per_page)
            all_projects = project_query.all()
            
            for project in all_projects:
                # Format project for display
                prompt_count = len(project.prompts)
                created_at = format_date(project.created_at)
                updated_at = format_date(project.updated_at)
                created_by = project.creator.username if project.creator else "Unknown"
                
                projects.append({
                    "id": str(project.id),
                    "name": project.name,
                    "description": project.description or "",
                    "prompt_count": prompt_count,
                    "created_at": created_at,
                    "updated_at": updated_at,
                    "created_by": created_by
                })
        
        if search_type in ["all", "prompts"]:
            # Build efficient prompt search query
            prompt_query = self.prompt_manager.get_multi_with_relationships('creator', 'project')
            
            if query:
                # Use SQLAlchemy's or_ for efficient text search
                prompt_query = prompt_query.filter(
                    or_(
                        self.prompt_manager.model_class.name.ilike(f"%{query}%"),
                        self.prompt_manager.model_class.system_prompt.ilike(f"%{query}%"),
                        self.prompt_manager.model_class.user_prompt.ilike(f"%{query}%")
                    )
                )
            
            # Add pagination
            prompt_query = prompt_query.offset(offset).limit(per_page)
            all_prompts = prompt_query.all()
            
            for prompt in all_prompts:
                # Format prompt for display
                variables = extract_variables((prompt.system_prompt or "") + prompt.user_prompt)
                created_at = format_date(prompt.created_at)
                updated_at = format_date(prompt.updated_at)
                created_by = prompt.creator.username if prompt.creator else "Unknown"
                
                prompts.append({
                    "id": str(prompt.id),
                    "name": prompt.name,
                    "project_id": str(prompt.project_id),
                    "project_name": prompt.project.name,
                    "variables": variables,
                    "created_at": created_at,
                    "updated_at": updated_at,
                    "created_by": created_by
                })
        
        # Calculate pagination info
        total_projects = len(projects) if search_type in ["all", "projects"] else 0
        total_prompts = len(prompts) if search_type in ["all", "prompts"] else 0
        total_pages = max(
            (total_projects + per_page - 1) // per_page,
            (total_prompts + per_page - 1) // per_page
        )
        
        pagination = {
            "current_page": page,
            "total_pages": total_pages,
            "per_page": per_page,
            "total_items": total_projects + total_prompts
        }
        
        return projects, prompts, pagination 