"""
Prompts API routes
"""
from fastapi import APIRouter, Request, HTTPException, status, Depends
from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.managers.prompt_manager import PromptManager
from app.managers.project_manager import ProjectManager
from app.managers.activity_manager import ActivityManager
from app.db import models
from app.models.activity import ActivityType
from app.models.prompt import PromptCreate, PromptUpdate, PromptResponse
from app.dependencies.auth import require_auth

# Create router
router = APIRouter(tags=["prompts-api"])

def get_prompt_manager() -> PromptManager:
    """Dependency to get prompt manager instance"""
    return PromptManager()

def get_project_manager() -> ProjectManager:
    """Dependency to get project manager instance"""
    return ProjectManager()

def get_activity_manager() -> ActivityManager:
    """Dependency to get activity manager instance"""
    return ActivityManager()

@router.get("", response_model=List[PromptResponse])
@require_auth()
async def get_prompts(
    request: Request,
    project_id: Optional[str] = None,
    prompt_manager: PromptManager = Depends(get_prompt_manager),
    project_manager: ProjectManager = Depends(get_project_manager)
):
    """Get all prompts for the current user or a specific project"""
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
    
    return [PromptResponse.from_orm(prompt) for prompt in prompts]

@router.post("", response_model=PromptResponse)
@require_auth()
async def create_prompt(
    request: Request,
    prompt_data: PromptCreate,
    prompt_manager: PromptManager = Depends(get_prompt_manager),
    project_manager: ProjectManager = Depends(get_project_manager),
    activity_manager: ActivityManager = Depends(get_activity_manager)
):
    """Create a new prompt"""
    user_id = uuid.UUID(request.session["user_id"])
    
    # Verify project ownership
    try:
        project_uuid = uuid.UUID(prompt_data.project_id)
        project = project_manager.get_project(project_uuid)
        if not project or project.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to create prompts in this project"
            )
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid project ID format"
        )
    
    prompt = prompt_manager.create_prompt(
        name=prompt_data.name,
        description=prompt_data.description,
        content=prompt_data.content,
        project_id=project_uuid
    )
    
    # Log activity
    activity_manager.create(
        type=ActivityType.PROMPT_CREATED,
        description=f"Prompt {prompt.name} created in project {project.name}",
        user_id=user_id
    )
    
    return PromptResponse.from_orm(prompt)

@router.get("/{prompt_id}", response_model=PromptResponse)
@require_auth()
async def get_prompt(
    request: Request,
    prompt_id: str,
    prompt_manager: PromptManager = Depends(get_prompt_manager),
    project_manager: ProjectManager = Depends(get_project_manager)
):
    """Get a specific prompt"""
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
    
    return PromptResponse.from_orm(prompt)

@router.put("/{prompt_id}", response_model=PromptResponse)
@require_auth()
async def update_prompt(
    request: Request,
    prompt_id: str,
    prompt_data: PromptUpdate,
    prompt_manager: PromptManager = Depends(get_prompt_manager),
    project_manager: ProjectManager = Depends(get_project_manager),
    activity_manager: ActivityManager = Depends(get_activity_manager)
):
    """Update a prompt"""
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
            detail="Not authorized to update this prompt"
        )
    
    updated_prompt = prompt_manager.update_prompt(
        prompt_id=prompt_uuid,
        name=prompt_data.name,
        description=prompt_data.description,
        content=prompt_data.content
    )
    
    # Log activity
    activity_manager.create(
        type=ActivityType.PROMPT_UPDATED,
        description=f"Prompt {updated_prompt.name} updated in project {project.name}",
        user_id=user_id
    )
    
    return PromptResponse.from_orm(updated_prompt)

@router.delete("/{prompt_id}")
@require_auth()
async def delete_prompt(
    request: Request,
    prompt_id: str,
    prompt_manager: PromptManager = Depends(get_prompt_manager),
    project_manager: ProjectManager = Depends(get_project_manager),
    activity_manager: ActivityManager = Depends(get_activity_manager)
):
    """Delete a prompt"""
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
            detail="Not authorized to delete this prompt"
        )
    
    # Log activity before deletion
    activity_manager.create(
        type=ActivityType.PROMPT_DELETED,
        description=f"Prompt {prompt.name} deleted from project {project.name}",
        user_id=user_id
    )
    
    # Delete prompt
    prompt_manager.delete_prompt(prompt_uuid)
    
    return {"message": "Prompt deleted successfully"} 