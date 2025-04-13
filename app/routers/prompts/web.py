"""
Prompts web routes
"""
from fastapi import APIRouter, Request, HTTPException, status, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from typing import List, Dict, Any, Optional
import uuid

from app.managers.prompt_manager import PromptManager
from app.managers.project_manager import ProjectManager
from app.managers.activity_manager import ActivityManager
from app.db import models
from app.models.activity import ActivityType
from app.dependencies.auth import require_auth

# Create router
router = APIRouter(tags=["prompts-web"])

# Templates
templates = Jinja2Templates(directory="app/templates")

def get_prompt_manager() -> PromptManager:
    """Dependency to get prompt manager instance"""
    return PromptManager()

def get_project_manager() -> ProjectManager:
    """Dependency to get project manager instance"""
    return ProjectManager()

def get_activity_manager() -> ActivityManager:
    """Dependency to get activity manager instance"""
    return ActivityManager()

@router.get("", response_class=HTMLResponse)
@require_auth()
async def prompts_page(
    request: Request,
    project_id: Optional[str] = None,
    prompt_manager: PromptManager = Depends(get_prompt_manager),
    project_manager: ProjectManager = Depends(get_project_manager)
):
    """Render the prompts list page"""
    user_id = uuid.UUID(request.session["user_id"])
    
    if project_id:
        try:
            project_uuid = uuid.UUID(project_id)
            project = project_manager.get_project(project_uuid)
            if not project or project.user_id != user_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Not authorized to access this project"
                )
            prompts = prompt_manager.get_project_prompts(project_uuid)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid project ID format"
            )
    else:
        prompts = prompt_manager.get_user_prompts(user_id)
        project = None
    
    return templates.TemplateResponse(
        "prompts/list.html",
        {
            "request": request,
            "user": request.session["user"],
            "project": project,
            "prompts": [
                {
                    "id": str(prompt.id),
                    "name": prompt.name,
                    "description": prompt.description,
                    "created_at": prompt.created_at,
                    "updated_at": prompt.updated_at
                }
                for prompt in prompts
            ]
        }
    )

@router.get("/{prompt_id}", response_class=HTMLResponse)
@require_auth()
async def prompt_detail_page(
    request: Request,
    prompt_id: str,
    prompt_manager: PromptManager = Depends(get_prompt_manager),
    project_manager: ProjectManager = Depends(get_project_manager)
):
    """Render the prompt detail page"""
    try:
        prompt_uuid = uuid.UUID(prompt_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid prompt ID format"
        )
    
    prompt = prompt_manager.get_prompt(prompt_uuid)
    if not prompt:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Prompt not found"
        )
    
    # Verify project ownership
    user_id = uuid.UUID(request.session["user_id"])
    project = project_manager.get_project(prompt.project_id)
    if not project or project.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this prompt"
        )
    
    return templates.TemplateResponse(
        "prompts/detail.html",
        {
            "request": request,
            "user": request.session["user"],
            "project": {
                "id": str(project.id),
                "name": project.name,
                "description": project.description
            },
            "prompt": {
                "id": str(prompt.id),
                "name": prompt.name,
                "description": prompt.description,
                "content": prompt.content,
                "created_at": prompt.created_at,
                "updated_at": prompt.updated_at
            }
        }
    )

@router.get("/create", response_class=HTMLResponse)
@require_auth()
async def create_prompt_page(
    request: Request,
    project_id: str,
    project_manager: ProjectManager = Depends(get_project_manager)
):
    """Render the create prompt page"""
    try:
        project_uuid = uuid.UUID(project_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid project ID format"
        )
    
    # Verify project ownership
    user_id = uuid.UUID(request.session["user_id"])
    project = project_manager.get_project(project_uuid)
    if not project or project.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to create prompts in this project"
        )
    
    return templates.TemplateResponse(
        "prompts/create.html",
        {
            "request": request,
            "user": request.session["user"],
            "project": {
                "id": str(project.id),
                "name": project.name,
                "description": project.description
            }
        }
    )

@router.get("/{prompt_id}/edit", response_class=HTMLResponse)
@require_auth()
async def edit_prompt_page(
    request: Request,
    prompt_id: str,
    prompt_manager: PromptManager = Depends(get_prompt_manager),
    project_manager: ProjectManager = Depends(get_project_manager)
):
    """Render the edit prompt page"""
    try:
        prompt_uuid = uuid.UUID(prompt_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid prompt ID format"
        )
    
    prompt = prompt_manager.get_prompt(prompt_uuid)
    if not prompt:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Prompt not found"
        )
    
    # Verify project ownership
    user_id = uuid.UUID(request.session["user_id"])
    project = project_manager.get_project(prompt.project_id)
    if not project or project.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to edit this prompt"
        )
    
    return templates.TemplateResponse(
        "prompts/edit.html",
        {
            "request": request,
            "user": request.session["user"],
            "project": {
                "id": str(project.id),
                "name": project.name,
                "description": project.description
            },
            "prompt": {
                "id": str(prompt.id),
                "name": prompt.name,
                "description": prompt.description,
                "content": prompt.content
            }
        }
    ) 