"""
Projects web routes
"""
from fastapi import APIRouter, Request, HTTPException, status, Depends, Query
from fastapi.responses import HTMLResponse, RedirectResponse
from app.templates import templates
from typing import List, Dict, Any, Optional
import uuid

from app.dependencies.auth import require_auth
from app.managers.project_manager import ProjectManager
from app.managers.prompt_manager import PromptManager
from app.managers.activity_manager import ActivityManager
from app.db import models
from app.models.activity import ActivityType
from app.utils.format_date import format_datetime, format_relative_time

# Create router
router = APIRouter(tags=["projects-web"])

def get_project_manager() -> ProjectManager:
    """Dependency to get project manager instance"""
    return ProjectManager()

def get_prompt_manager() -> PromptManager:
    """Dependency to get prompt manager instance"""
    return PromptManager()

def get_activity_manager() -> ActivityManager:
    """Dependency to get activity manager instance"""
    return ActivityManager()

@router.get("", response_class=HTMLResponse)
@require_auth()
async def projects_page(
    request: Request,
    project_manager: ProjectManager = Depends(get_project_manager),
    prompt_manager: PromptManager = Depends(get_prompt_manager)
):
    """Render the projects list page"""
    user_id = uuid.UUID(request.session["user_id"])
    projects = project_manager.get_user_projects(user_id)
    
    # Get prompt counts for each project
    project_data = []
    for project in projects:
        prompt_count = prompt_manager.get_project_prompts_count(project.id)
        project_data.append({
            "id": str(project.id),
            "name": project.name,
            "description": project.description,
            "prompt_count": prompt_count,
            "created_at": format_relative_time(project.created_at),
            "created_by": project.creator.username if project.creator else "Unknown"
        })
    
    return templates.TemplateResponse(
        "projects/list.html",
        {
            "request": request,
            "user": request.session["user"],
            "projects": project_data
        }
    )

@router.get("/{project_id}", response_class=HTMLResponse)
@require_auth()
async def project_detail_page(
    request: Request,
    project_id: str,
    project_manager: ProjectManager = Depends(get_project_manager),
    prompt_manager: PromptManager = Depends(get_prompt_manager)
):
    """Render the project detail page"""
    try:
        project_uuid = uuid.UUID(project_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid project ID format"
        )
    
    project = project_manager.get_project(project_uuid)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    user_id = uuid.UUID(request.session["user_id"])
    if project.created_by != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this project"
        )
    
    prompts = prompt_manager.get_project_prompts(project.id)
    
    return templates.TemplateResponse(
        "projects/detail.html",
        {
            "request": request,
            "user": request.session["user"],
            "project": {
                "id": str(project.id),
                "name": project.name,
                "description": project.description,
                "created_at": format_relative_time(project.created_at),
                "updated_at": format_relative_time(project.updated_at) if project.updated_at else None,
                "created_by": project.creator.username if project.creator else "Unknown"
            },
            "prompts": [
                {
                    "id": str(prompt.id),
                    "name": prompt.name,
                    "description": prompt.description,
                    "created_at": format_relative_time(prompt.created_at),
                    "updated_at": format_relative_time(prompt.updated_at) if prompt.updated_at else None,
                    "enabled": prompt.is_active,
                    "version": prompt.version,
                    "has_history": len(prompt.versions) > 1 if hasattr(prompt, 'versions') else False,
                    "variables": prompt.variables if hasattr(prompt, 'variables') else [],
                    "last_used": format_relative_time(prompt.last_used) if hasattr(prompt, 'last_used') and prompt.last_used else None
                }
                for prompt in prompts
            ]
        }
    )

@router.get("/search")
@require_auth()
async def search_projects_page(
    request: Request,
    query: str = Query(..., min_length=1, description="Search query"),
    limit: int = Query(10, ge=1, le=100, description="Maximum number of results"),
    offset: int = Query(0, ge=0, description="Number of results to skip"),
    project_manager: ProjectManager = Depends(get_project_manager),
    activity_manager: ActivityManager = Depends(get_activity_manager)
):
    """Search projects page"""
    user_id = uuid.UUID(request.session["user_id"])
    projects = project_manager.search_projects(
        query=query,
        user_id=user_id,
        limit=limit,
        offset=offset
    )
    
    # Log activity
    activity_manager.create(
        type=ActivityType.PROJECT_SEARCHED,
        description=f"Searched for projects with query: {query}",
        user_id=user_id
    )
    
    return templates.TemplateResponse(
        "projects/search.html",
        {
            "request": request,
            "projects": projects,
            "query": query,
            "limit": limit,
            "offset": offset
        }
    ) 