from fastapi import APIRouter, Request, Depends, Query
from app.templates import templates
from typing import Dict, List, Optional
from app.managers.project_manager import ProjectManager
from app.managers.prompt_manager import PromptManager
from app.utils import format_date, extract_variables
from app.dependencies.auth import require_auth
from app.db.database import session_scope

router = APIRouter(tags=["Search"])

@router.get("/search")
@require_auth()
async def search(
    request: Request,
    q: Optional[str] = Query(None),
    type: str = Query("all")
):
    """Search for projects and prompts"""
    projects = []
    prompts = []
    query = q or ""
    search_type = type

    with session_scope() as session:
        project_manager = ProjectManager(session)
        prompt_manager = PromptManager(session)

        if search_type in ["all", "projects"]:
            # Search projects with joined user data
            all_projects = project_manager.get_multi_with_relationships(
                'creator'
            ).all()
            
            for project in all_projects:
                # Skip projects that don't match the search query
                if query and query.lower() not in project.name.lower() and query.lower() not in (project.description or "").lower():
                    continue
                
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
            # Search prompts with joined user data
            all_prompts = prompt_manager.get_multi_with_relationships(
                'creator',
                'project'
            ).all()
            
            for prompt in all_prompts:
                # Skip prompts that don't match the search query
                if query and query.lower() not in prompt.name.lower() and \
                   query.lower() not in (prompt.system_prompt or "").lower() and \
                   query.lower() not in prompt.user_prompt.lower():
                    continue
                
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
    
    return templates.TemplateResponse(
        "search_results.html",
        {
            "request": request,
            "query": query,
            "search_type": search_type,
            "projects": projects,
            "prompts": prompts
        }
    ) 