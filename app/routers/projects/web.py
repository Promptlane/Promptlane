"""
Projects web routes
"""

from fastapi import APIRouter, Request, HTTPException, status, Depends, Query, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from app.templates import templates
from typing import List, Dict, Any, Optional
import uuid

from app.dependencies.auth import require_auth
from app.managers.project_manager import ProjectManager
from app.managers.prompt_manager import PromptManager
from app.managers.activity_manager import ActivityManager
from app.db import models
from app.db.models.activity import ActivityType
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
    prompt_manager: PromptManager = Depends(get_prompt_manager),
):
    """Render the projects list page"""
    user_id = uuid.UUID(request.session["user_id"])
    projects = project_manager.get_user_projects(user_id)

    # Get prompt counts for each project
    project_data = []
    for project in projects:
        prompt_count = prompt_manager.get_project_prompts_count(project.id)
        project_data.append(
            {
                "id": str(project.id),
                "name": project.name,
                "description": project.description,
                "prompt_count": prompt_count,
                "created_at": format_relative_time(project.created_at),
                "created_by": (
                    project.creator.username if project.creator else "Unknown"
                ),
            }
        )

    return templates.TemplateResponse(
        "projects/list.html",
        {"request": request, "user": request.session["user"], "projects": project_data},
    )


@router.get("/{project_id}", response_class=HTMLResponse)
@require_auth()
async def project_detail_page(
    request: Request,
    project_id: str,
    project_manager: ProjectManager = Depends(get_project_manager),
    prompt_manager: PromptManager = Depends(get_prompt_manager),
):
    """Render the project detail page"""
    try:
        project_uuid = uuid.UUID(project_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid project ID format"
        )

    project = project_manager.get_project(project_uuid)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Project not found"
        )

    user_id = uuid.UUID(request.session["user_id"])
    if project.created_by != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this project",
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
                "updated_at": (
                    format_relative_time(project.updated_at)
                    if project.updated_at
                    else None
                ),
                "created_by": (
                    project.creator.username if project.creator else "Unknown"
                ),
                "prompts": [
                    {
                        "id": str(prompt.id),
                        "name": prompt.name,
                        "description": prompt.description,
                        "created_at": format_relative_time(prompt.created_at),
                        "updated_at": (
                            format_relative_time(prompt.updated_at)
                            if prompt.updated_at
                            else None
                        ),
                        "enabled": prompt.is_active,
                        "version": prompt.version,
                        "has_history": (
                            len(prompt.versions) > 1
                            if hasattr(prompt, "versions")
                            else False
                        ),
                        "variables": (
                            prompt.variables if hasattr(prompt, "variables") else []
                        ),
                        "last_used": (
                            format_relative_time(prompt.last_used)
                            if hasattr(prompt, "last_used") and prompt.last_used
                            else None
                        ),
                    }
                    for prompt in prompts
                ],
            },
        },
    )


@router.get("/search")
@require_auth()
async def search_projects_page(
    request: Request,
    query: str = Query(..., min_length=1, description="Search query"),
    limit: int = Query(10, ge=1, le=100, description="Maximum number of results"),
    offset: int = Query(0, ge=0, description="Number of results to skip"),
    project_manager: ProjectManager = Depends(get_project_manager),
    activity_manager: ActivityManager = Depends(get_activity_manager),
):
    """Search projects page"""
    user_id = uuid.UUID(request.session["user_id"])
    projects = project_manager.search_projects(
        query=query, user_id=user_id, limit=limit, offset=offset
    )

    # Log activity
    activity_manager.create_activity(
        user_id=user_id,
        activity_type=ActivityType.PROJECT_SEARCHED,
        details={"query": query},
    )

    return templates.TemplateResponse(
        "projects/search.html",
        {
            "request": request,
            "projects": projects,
            "query": query,
            "limit": limit,
            "offset": offset,
        },
    )


@router.post("", response_class=HTMLResponse)
@require_auth()
async def create_project(
    request: Request,
    name: str = Form(...),
    description: str = Form(None),
    project_key: str = Form(None),
    project_manager: ProjectManager = Depends(get_project_manager),
    activity_manager: ActivityManager = Depends(get_activity_manager),
):
    """Create a new project"""
    user_id = uuid.UUID(request.session["user_id"])

    # Generate project key from name if not provided
    if not project_key:
        project_key = name.lower().replace(" ", "-")

    # Create the project
    project, error = project_manager.create_project(
        project_key=project_key, name=name, description=description, created_by=user_id
    )

    if error:
        # Return to the projects page with an error message
        return templates.TemplateResponse(
            "projects/list.html",
            {
                "request": request,
                "user": request.session["user"],
                "projects": project_manager.get_user_projects(user_id),
                "error": error,
            },
        )

    # Log activity
    activity_manager.create_activity(
        user_id=user_id,
        activity_type=ActivityType.CREATE_PROJECT,
        details={"project_id": str(project.id), "name": name},
    )

    # Redirect to the project details page
    return RedirectResponse(
        url=f"/projects/{project.id}", status_code=status.HTTP_303_SEE_OTHER
    )


@router.post("/{project_id}", response_class=HTMLResponse)
@require_auth()
async def update_project(
    request: Request,
    project_id: str,
    name: str = Form(...),
    description: str = Form(None),
    project_manager: ProjectManager = Depends(get_project_manager),
    prompt_manager: PromptManager = Depends(get_prompt_manager),
    activity_manager: ActivityManager = Depends(get_activity_manager),
):
    """Update a project"""
    try:
        project_uuid = uuid.UUID(project_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid project ID format"
        )

    user_id = uuid.UUID(request.session["user_id"])

    # Verify project ownership
    project = project_manager.get_project(project_uuid)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Project not found"
        )

    if project.created_by != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this project",
        )

    # Update the project
    updated_project, error = project_manager.update_project(
        project_id=project_uuid, name=name, description=description, updated_by=user_id
    )

    if error:
        # Return to the project details page with an error message
        prompts = prompt_manager.get_project_prompts(project_uuid)
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
                    "updated_at": (
                        format_relative_time(project.updated_at)
                        if project.updated_at
                        else None
                    ),
                    "created_by": (
                        project.creator.username if project.creator else "Unknown"
                    ),
                    "prompts": [
                        {
                            "id": str(prompt.id),
                            "name": prompt.name,
                            "description": prompt.description,
                            "created_at": format_relative_time(prompt.created_at),
                            "updated_at": (
                                format_relative_time(prompt.updated_at)
                                if prompt.updated_at
                                else None
                            ),
                            "enabled": (
                                prompt.is_active
                                if hasattr(prompt, "is_active")
                                else True
                            ),
                            "version": (
                                prompt.version if hasattr(prompt, "version") else 1
                            ),
                            "has_history": (
                                len(prompt.versions) > 1
                                if hasattr(prompt, "versions")
                                else False
                            ),
                            "variables": (
                                prompt.variables if hasattr(prompt, "variables") else []
                            ),
                            "last_used": (
                                format_relative_time(prompt.last_used)
                                if hasattr(prompt, "last_used") and prompt.last_used
                                else None
                            ),
                        }
                        for prompt in prompts
                    ],
                },
                "error": error,
            },
        )

    # Log activity
    activity_manager.create_activity(
        user_id=user_id,
        activity_type=ActivityType.UPDATE_PROJECT,
        details={"project_id": str(updated_project.id), "name": name},
    )

    # Redirect to the project details page
    return RedirectResponse(
        url=f"/projects/{project_uuid}", status_code=status.HTTP_303_SEE_OTHER
    )


@router.post("/{project_id}/delete", response_class=HTMLResponse)
@require_auth()
async def delete_project_form(
    request: Request,
    project_id: str,
    project_manager: ProjectManager = Depends(get_project_manager),
    activity_manager: ActivityManager = Depends(get_activity_manager),
):
    """Handle form-based deletion for projects (for HTML forms that can't use DELETE method)"""
    try:
        project_uuid = uuid.UUID(project_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid project ID format"
        )

    user_id = uuid.UUID(request.session["user_id"])

    # Verify project ownership
    project = project_manager.get_project(project_uuid)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Project not found"
        )

    if project.created_by != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this project",
        )

    # Delete the project
    success = project_manager.delete_project(project_uuid)

    if not success:
        # Return to the project details page with an error message
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
                    "updated_at": (
                        format_relative_time(project.updated_at)
                        if project.updated_at
                        else None
                    ),
                    "created_by": (
                        project.creator.username if project.creator else "Unknown"
                    ),
                },
                "error": "Failed to delete project",
            },
        )

    # Log activity
    activity_manager.create_activity(
        user_id=user_id,
        activity_type=ActivityType.DELETE_PROJECT,
        details={"project_id": str(project_uuid), "name": project.name},
    )

    # Redirect to the projects list page
    return RedirectResponse(url="/projects", status_code=status.HTTP_303_SEE_OTHER)


@router.get("/{project_id}/prompts/create", response_class=HTMLResponse)
@require_auth()
async def redirect_to_create_prompt_page(request: Request, project_id: str):
    """Redirect to the prompt creation page with the project ID as a query parameter"""
    return RedirectResponse(
        url=f"/prompts/create?project_id={project_id}",
        status_code=status.HTTP_302_FOUND,
    )


@router.post("/{project_id}/prompts", response_class=HTMLResponse)
@require_auth()
async def create_prompt(
    request: Request,
    project_id: str,
    name: str = Form(...),
    system_prompt: str = Form(...),
    user_prompt: str = Form(...),
    project_manager: ProjectManager = Depends(get_project_manager),
    prompt_manager: PromptManager = Depends(get_prompt_manager),
    activity_manager: ActivityManager = Depends(get_activity_manager),
):
    """Create a new prompt within a project"""
    try:
        project_uuid = uuid.UUID(project_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid project ID format"
        )

    # Verify project ownership
    user_id = uuid.UUID(request.session["user_id"])
    project = project_manager.get_project(project_uuid)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Project not found"
        )

    if project.created_by != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to create prompts in this project",
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
        created_by=user_id,
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
                    "description": project.description,
                    "created_at": format_relative_time(project.created_at),
                    "updated_at": (
                        format_relative_time(project.updated_at)
                        if project.updated_at
                        else None
                    ),
                    "created_by": (
                        project.creator.username if project.creator else "Unknown"
                    ),
                },
                "error": error,
                "form_data": {
                    "name": name,
                    "system_prompt": system_prompt,
                    "user_prompt": user_prompt,
                },
            },
        )

    # Log activity
    activity_manager.create_activity(
        user_id=user_id,
        activity_type=ActivityType.CREATE_PROMPT,
        details={
            "prompt_id": str(prompt.id),
            "name": prompt.name,
            "project_id": str(project_uuid),
        },
    )

    # Redirect to the project details page
    return RedirectResponse(
        url=f"/projects/{project_uuid}", status_code=status.HTTP_303_SEE_OTHER
    )


@router.get("/{project_id}/prompts/{prompt_id}", response_class=HTMLResponse)
@require_auth()
async def project_prompt_detail(
    request: Request,
    project_id: str,
    prompt_id: str,
    project_manager: ProjectManager = Depends(get_project_manager),
    prompt_manager: PromptManager = Depends(get_prompt_manager),
):
    """View a specific prompt within a project"""
    try:
        project_uuid = uuid.UUID(project_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid project ID format"
        )
    
    try:
        prompt_uuid = uuid.UUID(prompt_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid prompt ID format"
        )
    
    # Verify project ownership
    user_id = uuid.UUID(request.session["user_id"])
    project = project_manager.get_project(project_uuid)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Project not found"
        )
    
    if project.created_by != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this project",
        )
    
    # Get the prompt
    prompt = prompt_manager.get_prompt(prompt_uuid)
    if not prompt:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Prompt not found"
        )
    
    # Verify that the prompt belongs to the project
    if prompt.project_id != project_uuid:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Prompt does not belong to this project",
        )
    
    # Return the template response
    return templates.TemplateResponse(
        "prompts/detail.html",
        {
            "request": request,
            "user": request.session["user"],
            "project": {
                "id": str(project.id),
                "name": project.name,
                "description": project.description,
                "created_at": format_relative_time(project.created_at),
                "updated_at": (
                    format_relative_time(project.updated_at)
                    if project.updated_at
                    else None
                ),
                "created_by": (
                    project.creator.username if project.creator else "Unknown"
                ),
            },
            "prompt": {
                "id": str(prompt.id),
                "name": prompt.name,
                "description": prompt.description,
                "system_prompt": prompt.system_prompt,
                "user_prompt": prompt.user_prompt,
                "created_at": format_relative_time(prompt.created_at),
                "updated_at": (
                    format_relative_time(prompt.updated_at)
                    if prompt.updated_at
                    else None
                ),
                "enabled": prompt.is_active if hasattr(prompt, "is_active") else True,
                "version": prompt.version if hasattr(prompt, "version") else 1,
                "has_history": (
                    len(prompt.versions) > 1
                    if hasattr(prompt, "versions")
                    else False
                ),
                "variables": prompt.variables if hasattr(prompt, "variables") else [],
                "last_used": (
                    format_relative_time(prompt.last_used)
                    if hasattr(prompt, "last_used") and prompt.last_used
                    else None
                ),
            },
        },
    )


@router.get("/{project_id}/prompts/{prompt_id}/use", response_class=HTMLResponse)
@require_auth()
async def prompt_use_page(
    request: Request,
    project_id: str,
    prompt_id: str,
    project_manager: ProjectManager = Depends(get_project_manager),
    prompt_manager: PromptManager = Depends(get_prompt_manager),
):
    """Render the prompt use page for a specific prompt within a project"""
    try:
        project_uuid = uuid.UUID(project_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid project ID format"
        )
    
    try:
        prompt_uuid = uuid.UUID(prompt_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid prompt ID format"
        )
    
    # Verify project ownership
    user_id = uuid.UUID(request.session["user_id"])
    project = project_manager.get_project(project_uuid)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Project not found"
        )
    
    if project.created_by != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this project",
        )
    
    # Get the prompt
    prompt = prompt_manager.get_prompt(prompt_uuid)
    if not prompt:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Prompt not found"
        )
    
    # Verify that the prompt belongs to the project
    if prompt.project_id != project_uuid:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Prompt does not belong to this project",
        )
    
    # Extract variables from the prompt
    variables = []
    if hasattr(prompt, "variables") and prompt.variables:
        variables = prompt.variables
    else:
        # Try to extract variables from the user_prompt if not already defined
        import re
        variable_pattern = r'\{\{([a-zA-Z0-9_]+)\}\}'
        user_prompt_variables = re.findall(variable_pattern, prompt.user_prompt)
        system_prompt_variables = re.findall(variable_pattern, prompt.system_prompt or "")
        variables = list(set(user_prompt_variables + system_prompt_variables))
    
    # Return the template response
    return templates.TemplateResponse(
        "prompts/use.html",
        {
            "request": request,
            "user": request.session["user"],
            "project": {
                "id": str(project.id),
                "name": project.name,
                "description": project.description,
            },
            "prompt": {
                "id": str(prompt.id),
                "name": prompt.name,
                "description": prompt.description,
                "system_prompt": prompt.system_prompt,
                "user_prompt": prompt.user_prompt,
                "variables": variables,
            },
        },
    )
