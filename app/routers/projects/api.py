"""
Projects API routes
"""
from fastapi import APIRouter, Request, HTTPException, status,Depends, Query
from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.managers.project_manager import ProjectManager
from app.managers.prompt_manager import PromptManager
from app.managers.activity_manager import ActivityManager
from app.db import models
from app.models.activity import ActivityType
from app.models.project import ProjectCreate, ProjectUpdate, ProjectResponse
from app.dependencies.auth import require_auth

# Create router
router = APIRouter(tags=["projects-api"])

def get_project_manager() -> ProjectManager:
    """Dependency to get project manager instance"""
    return ProjectManager()

def get_prompt_manager() -> PromptManager:
    """Dependency to get prompt manager instance"""
    return PromptManager()

def get_activity_manager() -> ActivityManager:
    """Dependency to get activity manager instance"""
    return ActivityManager()

@router.get("", response_model=List[ProjectResponse])
@require_auth()
async def get_projects(
    request: Request,
    project_manager: ProjectManager = Depends(get_project_manager)
):
    """Get all projects for the current user"""
    user_id = uuid.UUID(request.session["user_id"])
    projects = project_manager.get_user_projects(user_id)
    return [ProjectResponse.from_orm(project) for project in projects]

@router.post("", response_model=ProjectResponse)
@require_auth()
async def create_project(
    request: Request,
    project_data: ProjectCreate,
    project_manager: ProjectManager = Depends(get_project_manager),
    activity_manager: ActivityManager = Depends(get_activity_manager)
):
    """Create a new project"""
    user_id = uuid.UUID(request.session["user_id"])
    project = project_manager.create_project(
        name=project_data.name,
        description=project_data.description,
        user_id=user_id
    )
    
    # Log activity
    activity_manager.create(
        type=ActivityType.PROJECT_CREATED,
        description=f"Project {project.name} created",
        user_id=user_id
    )
    
    return ProjectResponse.from_orm(project)

@router.get("/{project_id}", response_model=ProjectResponse)
@require_auth()
async def get_project(
    request: Request,
    project_id: str,
    project_manager: ProjectManager = Depends(get_project_manager)
):
    """Get a specific project"""
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
    if project.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this project"
        )
    
    return ProjectResponse.from_orm(project)

@router.put("/{project_id}", response_model=ProjectResponse)
@require_auth()
async def update_project(
    request: Request,
    project_id: str,
    project_data: ProjectUpdate,
    project_manager: ProjectManager = Depends(get_project_manager),
    activity_manager: ActivityManager = Depends(get_activity_manager)
):
    """Update a project"""
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
    if project.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this project"
        )
    
    updated_project = project_manager.update_project(
        project_id=project_uuid,
        name=project_data.name,
        description=project_data.description
    )
    
    # Log activity
    activity_manager.create(
        type=ActivityType.PROJECT_UPDATED,
        description=f"Project {updated_project.name} updated",
        user_id=user_id
    )
    
    return ProjectResponse.from_orm(updated_project)

@router.delete("/{project_id}")
@require_auth()
async def delete_project(
    request: Request,
    project_id: str,
    project_manager: ProjectManager = Depends(get_project_manager),
    activity_manager: ActivityManager = Depends(get_activity_manager)
):
    """Delete a project"""
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
    if project.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this project"
        )
    
    # Log activity before deletion
    activity_manager.create(
        type=ActivityType.PROJECT_DELETED,
        description=f"Project {project.name} deleted",
        user_id=user_id
    )
    
    # Delete project
    project_manager.delete_project(project_uuid)
    
    return {"message": "Project deleted successfully"}

@router.get("/search", response_model=List[Dict[str, Any]])
@require_auth()
async def search_projects(
    request: Request,
    query: str = Query(..., min_length=1, description="Search query"),
    limit: int = Query(10, ge=1, le=100, description="Maximum number of results"),
    offset: int = Query(0, ge=0, description="Number of results to skip"),
    project_manager: ProjectManager = Depends(get_project_manager),
    activity_manager: ActivityManager = Depends(get_activity_manager)
):
    """Search for projects"""
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
    
    return [
        {
            "id": str(project.id),
            "name": project.name,
            "description": project.description,
            "created_at": project.created_at,
            "updated_at": project.updated_at
        }
        for project in projects
    ]

@router.get("/search/suggestions", response_model=List[str])
@require_auth()
async def get_search_suggestions(
    request: Request,
    query: str = Query(..., min_length=1, description="Search query"),
    limit: int = Query(5, ge=1, le=20, description="Maximum number of suggestions"),
    project_manager: ProjectManager = Depends(get_project_manager)
):
    """Get project search suggestions"""
    user_id = uuid.UUID(request.session["user_id"])
    suggestions = project_manager.get_search_suggestions(
        query=query,
        user_id=user_id,
        limit=limit
    )
    
    return suggestions 