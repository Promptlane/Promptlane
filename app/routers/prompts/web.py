"""
Prompts web routes
"""
from fastapi import APIRouter, Request, HTTPException, status, Depends, Form, Query
from fastapi.responses import HTMLResponse, RedirectResponse
from app.templates import templates
from typing import List, Dict, Any, Optional
import uuid

from app.managers.prompt_manager import PromptManager
from app.managers.project_manager import ProjectManager
from app.managers.activity_manager import ActivityManager
from app.db import models
from app.models.activity import ActivityType
from app.dependencies.auth import require_auth
from app.managers.user_manager import UserManager
from app.utils.format_date import format_relative_time

# Create router
router = APIRouter(tags=["prompts-web"])

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
    search: Optional[str] = Query(None),
    sort: Optional[str] = Query(None),
    filter: Optional[str] = Query(None),
    prompt_manager: PromptManager = Depends(get_prompt_manager),
    project_manager: ProjectManager = Depends(get_project_manager)
):
    """Render the prompts list page"""
    user_id = uuid.UUID(request.session["user_id"])
    user_manager = UserManager()
    
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
        # Show all prompts created by the user, irrespective of project
        prompts = [p for p in prompt_manager.get_all_prompts() if str(p.created_by) == str(user_id)]
        project = None
    
    # --- Search ---
    if search:
        prompts = [
            p for p in prompts
            if search.lower() in p.name.lower() or search.lower() in (p.description or "").lower()
        ]
    # --- Filter ---
    if filter == "with_vars":
        prompts = [p for p in prompts if getattr(p, "variables", [])]
    elif filter == "no_vars":
        prompts = [p for p in prompts if not getattr(p, "variables", [])]
    elif filter == "my_prompts":
        prompts = [p for p in prompts if str(p.created_by) == str(user_id)]
    # --- Sort ---
    if sort == "name_asc":
        prompts = sorted(prompts, key=lambda p: p.name.lower())
    elif sort == "name_desc":
        prompts = sorted(prompts, key=lambda p: p.name.lower(), reverse=True)
    elif sort == "created_asc":
        prompts = sorted(prompts, key=lambda p: p.created_at)
    elif sort == "created_desc":
        prompts = sorted(prompts, key=lambda p: p.created_at, reverse=True)
    
    prompt_dicts = []
    for prompt in prompts:
        # Get project name
        project_obj = project_manager.get_project(prompt.project_id)
        project_name = project_obj.name if project_obj else "Unknown Project"
        # Get creator username
        creator = user_manager.get_user(prompt.created_by)
        created_by = creator.username if creator else "Unknown"
        # Get variables (if attribute exists)
        variables = getattr(prompt, "variables", [])
        prompt_dicts.append({
            "id": str(prompt.id),
            "name": prompt.name,
            "description": prompt.description,
            "project_id": str(prompt.project_id),
            "project_name": project_name,
            "created_at": format_relative_time(prompt.created_at),
            "created_by": created_by,
            "variables": variables
        })
    
    return templates.TemplateResponse(
        "prompts/list.html",
        {
            "request": request,
            "user": request.session["user"],
            "project": project,
            "prompts": prompt_dicts,
            "search": search,
            "sort": sort,
            "filter": filter
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
    if not project or project.created_by != user_id:
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

@router.post("", response_class=HTMLResponse)
@require_auth()
async def create_prompt(
    request: Request,
    project_id: str,
    name: str = Form(...),
    system_prompt: str = Form(...),
    user_prompt: str = Form(...),
    project_manager: ProjectManager = Depends(get_project_manager),
    prompt_manager: PromptManager = Depends(get_prompt_manager),
    activity_manager: ActivityManager = Depends(get_activity_manager)
):
    """Create a new prompt"""
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
    if not project or project.created_by != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to create prompts in this project"
        )
    
    # Generate a key from the name
    prompt_key = name.lower().replace(" ", "_")
    
    # Create the prompt
    prompt, error = prompt_manager.create_prompt(
        name=name,
        project_id=project_uuid,
        key=prompt_key,
        description="",  # Default empty description
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        created_by=user_id
    )
    
    if error:
        # Return to the create prompt page with an error message
        return templates.TemplateResponse(
            "prompts/create.html",
            {
                "request": request,
                "user": request.session["user"],
                "project": {
                    "id": str(project.id),
                    "name": project.name,
                    "description": project.description
                },
                "error": error,
                "form_data": {
                    "name": name,
                    "system_prompt": system_prompt,
                    "user_prompt": user_prompt
                }
            }
        )
    
    # Log activity
    activity_manager.create_activity(
        user_id=user_id,
        activity_type=ActivityType.CREATE_PROMPT,
        details={"prompt_id": str(prompt.id), "name": prompt.name, "project_id": str(project_uuid)}
    )
    
    # Redirect to the project details page
    return RedirectResponse(
        url=f"/projects/{project_uuid}",
        status_code=status.HTTP_303_SEE_OTHER
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
    if not project or project.created_by != user_id:
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
    if not project or project.created_by != user_id:
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