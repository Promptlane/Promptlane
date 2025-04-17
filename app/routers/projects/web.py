"""
Projects web routes
"""

from fastapi import APIRouter, Request, HTTPException, status, Depends, Query, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from app.templates import templates
from typing import List, Dict, Any, Optional
import uuid
import logging

from app.dependencies.auth import require_auth
from app.managers.project_manager import ProjectManager
from app.managers.prompt_manager import PromptManager
from app.managers.activity_manager import ActivityManager
from app.db import models
from app.db.models.activity import ActivityType
from app.utils.format_date import format_datetime, format_relative_time

# Create router
router = APIRouter(tags=["projects-web"])

# Configure logger
logger = logging.getLogger(__name__)


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
                        "created_by": (
                            prompt.creator.username
                            if hasattr(prompt, "creator") and prompt.creator
                            else "Unknown"
                        ),
                        "updated_by": (
                            prompt.updater.username
                            if hasattr(prompt, "updater") and prompt.updater
                            else "Unknown"
                        ),
                        "enabled": (
                            prompt.is_active if hasattr(prompt, "is_active") else True
                        ),
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
                            "created_by": (
                                prompt.creator.username
                                if hasattr(prompt, "creator") and prompt.creator
                                else "Unknown"
                            ),
                            "updated_by": (
                                prompt.updater.username
                                if hasattr(prompt, "updater") and prompt.updater
                                else "Unknown"
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
    logger.info(
        f"Accessing prompt detail view: project_id={project_id}, prompt_id={prompt_id}"
    )

    try:
        project_uuid = uuid.UUID(project_id)
        logger.debug(f"Valid project UUID: {project_uuid}")
    except ValueError:
        logger.error(f"Invalid project ID format: {project_id}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid project ID format"
        )

    try:
        prompt_uuid = uuid.UUID(prompt_id)
        logger.debug(f"Valid prompt UUID: {prompt_uuid}")
    except ValueError:
        logger.error(f"Invalid prompt ID format: {prompt_id}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid prompt ID format"
        )

    # Verify project ownership
    user_id = uuid.UUID(request.session["user_id"])
    logger.debug(f"User ID: {user_id}")
    project = project_manager.get_project(project_uuid)
    if not project:
        logger.error(f"Project not found: {project_uuid}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Project not found"
        )

    if project.created_by != user_id:
        logger.warning(
            f"Unauthorized access attempt to project {project_uuid} by user {user_id}"
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this project",
        )

    # Get the prompt
    logger.debug(f"Fetching prompt: {prompt_uuid}")
    prompt = prompt_manager.get_prompt(prompt_uuid)
    if not prompt:
        logger.error(f"Prompt not found: {prompt_uuid}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Prompt not found"
        )

    # Verify that the prompt belongs to the project
    if prompt.project_id != project_uuid:
        logger.error(f"Prompt {prompt_uuid} does not belong to project {project_uuid}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Prompt does not belong to this project",
        )

    logger.debug(
        f"Prompt found: id={prompt.id}, name={prompt.name}, version={getattr(prompt, 'version', 'N/A')}"
    )
    logger.debug(f"Prompt has versions attribute: {hasattr(prompt, 'versions')}")
    if hasattr(prompt, "versions"):
        logger.debug(f"Prompt versions count: {len(prompt.versions)}")

    # Process version history if available
    versions = []
    if hasattr(prompt, "versions") and prompt.versions:
        logger.info(
            f"Processing {len(prompt.versions)} versions for prompt {prompt_uuid}"
        )

        # Debug log for each version
        for i, version in enumerate(prompt.versions):
            logger.debug(
                f"Version {i+1}: id={version.id}, version={version.version}, "
                + f"parent_id={version.parent_id if hasattr(version, 'parent_id') else 'N/A'}, "
                + f"name={version.name}, is_active={getattr(version, 'is_active', None)}"
            )

            versions.append(
                {
                    "id": str(version.id),
                    "version": version.version,
                    "name": version.name,
                    "system_prompt": version.system_prompt,
                    "user_prompt": version.user_prompt,
                    "created_at": format_relative_time(version.created_at),
                    "created_by": (
                        version.creator.username
                        if hasattr(version, "creator") and version.creator
                        else "Unknown"
                    ),
                    "updated_at": (
                        format_relative_time(version.updated_at)
                        if version.updated_at
                        else None
                    ),
                    "updated_by": (
                        version.updater.username
                        if hasattr(version, "updater") and version.updater
                        else None
                    ),
                    "is_active": (
                        version.is_active if hasattr(version, "is_active") else False
                    ),
                }
            )
        # Sort versions by version number (descending)
        versions.sort(key=lambda v: v["version"], reverse=True)
        logger.debug(f"Sorted {len(versions)} versions by version number")

        # Additional debug info about version counting
        logger.debug(
            f"prompt.versions count: {len(prompt.versions)}, processed versions count: {len(versions)}"
        )
        logger.debug(f"Versions in array: {[v['version'] for v in versions]}")
    else:
        logger.info(f"No versions found for prompt {prompt_uuid}")

    logger.info(f"Rendering prompt detail template with {len(versions)} versions")
    # Return the template response
    # Log whether the prompt is active
    is_active = getattr(prompt, "is_active", None)
    logger.debug(
        f"Current prompt is_active status: {is_active} (type: {type(is_active)})"
    )

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
                "created_by": (
                    prompt.creator.username
                    if hasattr(prompt, "creator") and prompt.creator
                    else "Unknown"
                ),
                "updated_by": (
                    prompt.updater.username
                    if hasattr(prompt, "updater") and prompt.updater
                    else "Unknown"
                ),
                "enabled": prompt.is_active if hasattr(prompt, "is_active") else True,
                "is_active": prompt.is_active if hasattr(prompt, "is_active") else None,
                "version": prompt.version if hasattr(prompt, "version") else 1,
                "has_history": (
                    len(prompt.versions) > 1 if hasattr(prompt, "versions") else False
                ),
                "variables": prompt.variables if hasattr(prompt, "variables") else [],
                "last_used": (
                    format_relative_time(prompt.last_used)
                    if hasattr(prompt, "last_used") and prompt.last_used
                    else None
                ),
                "versions": versions,
            },
        },
    )


@router.post("/{project_id}/prompts/{prompt_id}", response_class=HTMLResponse)
@require_auth()
async def update_prompt(
    request: Request,
    project_id: str,
    prompt_id: str,
    name: str = Form(...),
    system_prompt: str = Form(...),
    user_prompt: str = Form(...),
    version_action: str = Form("update"),
    project_manager: ProjectManager = Depends(get_project_manager),
    prompt_manager: PromptManager = Depends(get_prompt_manager),
    activity_manager: ActivityManager = Depends(get_activity_manager),
):
    """Update a prompt"""
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
            detail="Not authorized to modify this project",
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

    # Determine if this is a new version or an update to the current version
    create_new_version = version_action == "new_version"

    # Update the prompt or create a new version
    updated_prompt, error = prompt_manager.update_prompt(
        prompt_id=prompt_uuid,
        name=name,
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        updated_by=user_id,
        create_new_version=create_new_version,
    )

    if error:
        # Return to the prompt detail page with an error message
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
                    "created_by": (
                        prompt.creator.username
                        if hasattr(prompt, "creator") and prompt.creator
                        else "Unknown"
                    ),
                    "updated_by": (
                        prompt.updater.username
                        if hasattr(prompt, "updater") and prompt.updater
                        else "Unknown"
                    ),
                    "enabled": (
                        prompt.is_active if hasattr(prompt, "is_active") else True
                    ),
                    "version": prompt.version if hasattr(prompt, "version") else 1,
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
                },
                "error": error,
                "form_data": {
                    "name": name,
                    "system_prompt": system_prompt,
                    "user_prompt": user_prompt,
                },
            },
        )

    # Get the ID to redirect to (might be a new prompt if a new version was created)
    redirect_prompt_id = updated_prompt.id if create_new_version else prompt_uuid

    # Log activity (activity is already logged in the update_prompt method)

    # Redirect back to the prompt detail page
    return RedirectResponse(
        url=f"/projects/{project_uuid}/prompts/{redirect_prompt_id}",
        status_code=status.HTTP_303_SEE_OTHER,
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

        variable_pattern = r"\{\{([a-zA-Z0-9_]+)\}\}"
        user_prompt_variables = re.findall(variable_pattern, prompt.user_prompt)
        system_prompt_variables = re.findall(
            variable_pattern, prompt.system_prompt or ""
        )
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


@router.post(
    "/{project_id}/prompts/{prompt_id}/toggle-enabled", response_class=HTMLResponse
)
@require_auth()
async def toggle_prompt_enabled(
    request: Request,
    project_id: str,
    prompt_id: str,
    project_manager: ProjectManager = Depends(get_project_manager),
    prompt_manager: PromptManager = Depends(get_prompt_manager),
    activity_manager: ActivityManager = Depends(get_activity_manager),
):
    """Toggle the enabled status of a prompt"""
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
            detail="Not authorized to modify this project",
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

    # Toggle is_active status
    current_status = prompt.is_active if hasattr(prompt, "is_active") else True
    new_status = not current_status

    # Update the prompt
    update_data = {
        "is_active": new_status,
        "updated_by": user_id,
    }

    updated_prompt, error = prompt_manager.update_prompt(
        prompt_id=prompt_uuid, **update_data
    )

    if error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to toggle prompt status: {error}",
        )

    # Log activity
    activity_manager.create_activity(
        user_id=user_id,
        activity_type=ActivityType.UPDATE_PROMPT,
        details={
            "prompt_id": str(prompt_uuid),
            "project_id": str(project_uuid),
            "name": prompt.name,
            "action": "enabled" if new_status else "disabled",
        },
    )

    # Redirect back to the prompt detail page
    return RedirectResponse(
        url=f"/projects/{project_uuid}/prompts/{prompt_uuid}",
        status_code=status.HTTP_303_SEE_OTHER,
    )


@router.get("/{project_id}/prompts/{prompt_id}/set-active", response_class=HTMLResponse)
@require_auth()
async def set_prompt_active(
    request: Request,
    project_id: str,
    prompt_id: str,
    version: Optional[int] = Query(None),
    project_manager: ProjectManager = Depends(get_project_manager),
    prompt_manager: PromptManager = Depends(get_prompt_manager),
    activity_manager: ActivityManager = Depends(get_activity_manager),
):
    """Set a prompt version as active"""
    logger.info(
        f"Setting prompt as active: project_id={project_id}, prompt_id={prompt_id}, version={version}"
    )

    try:
        project_uuid = uuid.UUID(project_id)
    except ValueError:
        logger.error(f"Invalid project ID format: {project_id}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid project ID format"
        )

    try:
        prompt_uuid = uuid.UUID(prompt_id)
    except ValueError:
        logger.error(f"Invalid prompt ID format: {prompt_id}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid prompt ID format"
        )

    # Verify project ownership
    user_id = uuid.UUID(request.session["user_id"])
    project = project_manager.get_project(project_uuid)
    if not project:
        logger.error(f"Project not found: {project_uuid}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Project not found"
        )

    if project.created_by != user_id:
        logger.warning(
            f"Unauthorized attempt to modify project {project_uuid} by user {user_id}"
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to modify this project",
        )

    # Get the prompt
    prompt = prompt_manager.get_prompt(prompt_uuid)
    if not prompt:
        logger.error(f"Prompt not found: {prompt_uuid}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Prompt not found"
        )

    # Verify that the prompt belongs to the project
    if prompt.project_id != project_uuid:
        logger.error(f"Prompt {prompt_uuid} does not belong to project {project_uuid}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Prompt does not belong to this project",
        )

    # Get all versions related to this prompt (including parent, siblings, and children at any level)
    all_related_prompts = prompt.versions if hasattr(prompt, "versions") else [prompt]
    logger.debug(f"Found {len(all_related_prompts)} related prompts")

    # Debug log all versions
    for i, related in enumerate(all_related_prompts):
        logger.debug(
            f"Related prompt {i+1}: id={related.id}, version={related.version}, is_active={getattr(related, 'is_active', False)}"
        )

    # First, deactivate all related prompts
    for related in all_related_prompts:
        if (
            related.id != prompt.id
            and hasattr(related, "is_active")
            and related.is_active
        ):
            logger.debug(
                f"Deactivating prompt: {related.id} (version {related.version})"
            )
            updated_related, error = prompt_manager.update_prompt(
                prompt_id=related.id, is_active=False, updated_by=user_id
            )

            if error:
                logger.error(f"Failed to deactivate prompt {related.id}: {error}")

    # Set the current prompt as active
    logger.info(f"Setting prompt {prompt.id} (version {prompt.version}) as active")
    updated_prompt, error = prompt_manager.update_prompt(
        prompt_id=prompt.id, is_active=True, updated_by=user_id
    )

    if error:
        logger.error(f"Failed to update prompt {prompt.id}: {error}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update prompt: {error}",
        )

    # Log activity
    activity_manager.create_activity(
        user_id=user_id,
        activity_type=ActivityType.UPDATE_PROMPT,
        details={
            "prompt_id": str(prompt.id),
            "project_id": str(project_uuid),
            "name": prompt.name,
            "action": "set_active",
            "version": prompt.version if hasattr(prompt, "version") else None,
        },
    )

    # Redirect back to the prompt detail page with a success message
    return RedirectResponse(
        url=f"/projects/{project_uuid}/prompts/{prompt_uuid}?message=Version+set+as+active+successfully",
        status_code=status.HTTP_303_SEE_OTHER,
    )
