"""
Admin API routes
"""
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks, Body, Request
from sqlalchemy.orm import Session
import logging
import uuid
from datetime import datetime

from app.db import models
from app.managers.user_manager import UserManager
from app.managers.team_manager import TeamManager
from app.managers.project_manager import ProjectManager
from app.managers.activity_manager import ActivityManager
from app.managers.prompt_manager import PromptManager
from app.routers.admin.common import (
    get_username,
    get_admin_user,
    check_admin_permissions
)
from app.services.email import send_invitation_email
from app.utils.serializers import safe_json_dumps
from app.models.admin import AdminStatusUpdate, UserInvite
from app.models.activity import ActivityType
from app.exceptions import UserNotFoundError, TeamNotFoundError, ProjectNotFoundError, PromptNotFoundError

router = APIRouter(
    prefix="/api/admin",
    tags=["Admin API"],
)

logger = logging.getLogger(__name__)

def get_user_manager() -> UserManager:
    return UserManager()

def get_team_manager() -> TeamManager:
    return TeamManager()

def get_project_manager() -> ProjectManager:
    return ProjectManager()

def get_activity_manager() -> ActivityManager:
    return ActivityManager()

def get_prompt_manager() -> PromptManager:
    return PromptManager()

@router.get("/dashboard/stats")
async def api_dashboard_stats(
    request: Request,
    user_manager: UserManager = Depends(get_user_manager),
    project_manager: ProjectManager = Depends(get_project_manager),
    prompt_manager: PromptManager = Depends(get_prompt_manager)
):
    """API endpoint to get dashboard stats"""
    try:
        # Check admin permissions
        check_admin_permissions(request)
        
        # Get basic stats
        total_users = len(user_manager.get_all_users())
        total_projects = len(project_manager.get_all_projects())
        active_users = len(user_manager.get_active_users(days=7))
        
        # Get prompt count
        total_prompts = len(prompt_manager.get_all_prompts())
        
        # Calculate stats changes (mock data for now)
        return {
            "active_users": active_users,
            "total_users": total_users,
            "total_projects": total_projects,
            "total_prompts": total_prompts,
            "storage_used": "1.2 GB",
            "storage_percentage": 24,
            "user_change": 12,
            "project_change": 8,
            "prompt_change": 15
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/users")
async def api_get_users(
    request: Request,
    user_manager: UserManager = Depends(get_user_manager)
):
    """API endpoint to get all users"""
    try:
        # Check admin permissions
        check_admin_permissions(request)
        
        users = user_manager.get_all_users()
        
        return [
            {
                "id": str(user.id),
                "username": user.username,
                "email": user.email,
                "created_at": user.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                "is_admin": user.is_admin
            }
            for user in users
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/activities")
async def api_get_activities(
    request: Request,
    limit: int = 10,
    activity_manager = Depends(get_activity_manager),
    user_manager: UserManager = Depends(get_user_manager)
):
    """API endpoint to get recent activities"""
    try:
        # Check admin permissions
        check_admin_permissions(request)
        
        activities = activity_manager.get_recent_activities(limit=limit)
        
        return [
            {
                "id": str(activity.id),
                "user_id": str(activity.user_id),
                "username": user_manager.get_username(activity.user_id),
                "activity_type": activity.activity_type,
                "created_at": activity.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                "metadata": activity.details or {}
            }
            for activity in activities
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/users/{user_id}/admin")
async def toggle_admin_status(
    request: Request,
    user_id: str,
    data: AdminStatusUpdate,
    user_manager: UserManager = Depends(get_user_manager),
    activity_manager = Depends(get_activity_manager)
):
    """Toggle admin status for a user"""
    try:
        # Check admin permissions
        check_admin_permissions(request)
        
        logger.info(f"Admin status change request received for user ID: {user_id}, new status: {data.is_admin_status}")
        
        # Parse UUID
        try:
            user_uuid = uuid.UUID(user_id)
        except ValueError:
            logger.warning(f"Invalid user ID format: {user_id}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid user ID format"
            )
        
        # Get user to update
        user = user_manager.get_user(user_uuid)
        if not user:
            logger.warning(f"User not found with ID: {user_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with ID {user_id} not found"
            )
        
        # Check if status is already the requested value
        if user.is_admin == data.is_admin_status:
            logger.info(f"User {user.username} already has is_admin={data.is_admin_status}, no change needed")
            return {"success": True, "message": f"No change needed - user is already {'an admin' if data.is_admin_status else 'not an admin'}"}
        
        # Update user
        user_manager.update_user_admin_status(user, data.is_admin_status)
        
        status_text = "granted" if data.is_admin_status else "removed"
        logger.info(f"Admin status {status_text} for user {user.username} (ID: {user.id})")
        
        # Create activity details with UUID-safe serialization
        activity_details = safe_json_dumps({
            "user_id": user.id,
            "username": user.username,
            "admin_status": data.is_admin_status,
            "action": f"Admin privileges {status_text}"
        })
        
        # Log activity using ActivityManager
        activity_manager.create(
            user_id=user.id,
            action=ActivityType.register,
            resource_type="user",
            resource_id=str(user.id),
            metadata=activity_details
        )
        
        return {"success": True, "message": f"Admin status {status_text} for user {user.username}"}
    except Exception as e:
        logger.exception(f"Error toggling admin status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/users")
async def create_user(
    request: Request,
    username: str,
    email: str,
    password: str,
    is_admin: bool = False,
    user_manager: UserManager = Depends(get_user_manager)
):
    """Create a new user"""
    try:
        # Check admin permissions
        check_admin_permissions(request)
        
        # Create user
        user, error = user_manager.create_user(username, email, password, is_admin)
        if error:
            raise HTTPException(status_code=400, detail=error)
        
        return {
            "message": "User created successfully",
            "user": {
                "id": str(user.id),
                "username": user.username,
                "email": user.email,
                "is_active": user.is_active,
                "is_admin": user.is_admin
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/users/{user_id}")
async def update_user(
    request: Request,
    user_id: str,
    username: str = None,
    email: str = None,
    password: str = None,
    is_active: bool = None,
    is_admin: bool = None,
    user_manager: UserManager = Depends(get_user_manager)
):
    """Update a user"""
    try:
        # Check admin permissions
        check_admin_permissions(request)
        
        # Update user
        user = user_manager.update_user(
            user_id,
            username=username,
            email=email,
            password=password,
            is_active=is_active,
            is_admin=is_admin
        )
        
        return {
            "message": "User updated successfully",
            "user": {
                "id": str(user.id),
                "username": user.username,
                "email": user.email,
                "is_active": user.is_active,
                "is_admin": user.is_admin
            }
        }
    except UserNotFoundError:
        raise HTTPException(status_code=404, detail="User not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/users/{user_id}")
async def delete_user(
    request: Request,
    user_id: str,
    user_manager: UserManager = Depends(get_user_manager)
):
    """Delete a user"""
    try:
        # Check admin permissions
        check_admin_permissions(request)
        
        # Delete user
        user_manager.delete_user(user_id)
        
        return {"message": "User deleted successfully"}
    except UserNotFoundError:
        raise HTTPException(status_code=404, detail="User not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/teams")
async def create_team(
    request: Request,
    name: str,
    description: str = None,
    team_manager: TeamManager = Depends(get_team_manager)
):
    """Create a new team"""
    try:
        # Check admin permissions
        check_admin_permissions(request)
        
        # Create team
        team = team_manager.create_team(name, description)
        
        return {
            "message": "Team created successfully",
            "team": {
                "id": str(team.id),
                "name": team.name,
                "description": team.description
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/teams/{team_id}")
async def update_team(
    request: Request,
    team_id: str,
    name: str = None,
    description: str = None,
    team_manager: TeamManager = Depends(get_team_manager)
):
    """Update a team"""
    try:
        # Check admin permissions
        check_admin_permissions(request)
        
        # Update team
        team = team_manager.update_team(team_id, name=name, description=description)
        
        return {
            "message": "Team updated successfully",
            "team": {
                "id": str(team.id),
                "name": team.name,
                "description": team.description
            }
        }
    except TeamNotFoundError:
        raise HTTPException(status_code=404, detail="Team not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/teams/{team_id}")
async def delete_team(
    request: Request,
    team_id: str,
    team_manager: TeamManager = Depends(get_team_manager)
):
    """Delete a team"""
    try:
        # Check admin permissions
        check_admin_permissions(request)
        
        # Delete team
        team_manager.delete_team(team_id)
        
        return {"message": "Team deleted successfully"}
    except TeamNotFoundError:
        raise HTTPException(status_code=404, detail="Team not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/projects")
async def create_project(
    request: Request,
    name: str,
    description: str = None,
    project_manager: ProjectManager = Depends(get_project_manager)
):
    """Create a new project"""
    try:
        # Check admin permissions
        check_admin_permissions(request)
        
        # Create project
        project = project_manager.create_project(name, description)
        
        return {
            "message": "Project created successfully",
            "project": {
                "id": str(project.id),
                "name": project.name,
                "description": project.description
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/projects/{project_id}")
async def update_project(
    request: Request,
    project_id: str,
    name: str = None,
    description: str = None,
    project_manager: ProjectManager = Depends(get_project_manager)
):
    """Update a project"""
    try:
        # Check admin permissions
        check_admin_permissions(request)
        
        # Update project
        project = project_manager.update_project(project_id, name=name, description=description)
        
        return {
            "message": "Project updated successfully",
            "project": {
                "id": str(project.id),
                "name": project.name,
                "description": project.description
            }
        }
    except ProjectNotFoundError:
        raise HTTPException(status_code=404, detail="Project not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/projects/{project_id}")
async def delete_project(
    request: Request,
    project_id: str,
    project_manager: ProjectManager = Depends(get_project_manager)
):
    """Delete a project"""
    try:
        # Check admin permissions
        check_admin_permissions(request)
        
        # Delete project
        project_manager.delete_project(project_id)
        
        return {"message": "Project deleted successfully"}
    except ProjectNotFoundError:
        raise HTTPException(status_code=404, detail="Project not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/prompts")
async def create_prompt(
    request: Request,
    name: str,
    content: str,
    prompt_manager: PromptManager = Depends(get_prompt_manager)
):
    """Create a new prompt"""
    try:
        # Check admin permissions
        check_admin_permissions(request)
        
        # Create prompt
        prompt = prompt_manager.create_prompt(name, content)
        
        return {
            "message": "Prompt created successfully",
            "prompt": {
                "id": str(prompt.id),
                "name": prompt.name,
                "content": prompt.content
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/prompts/{prompt_id}")
async def update_prompt(
    request: Request,
    prompt_id: str,
    name: str = None,
    content: str = None,
    prompt_manager: PromptManager = Depends(get_prompt_manager)
):
    """Update a prompt"""
    try:
        # Check admin permissions
        check_admin_permissions(request)
        
        # Update prompt
        prompt = prompt_manager.update_prompt(prompt_id, name=name, content=content)
        
        return {
            "message": "Prompt updated successfully",
            "prompt": {
                "id": str(prompt.id),
                "name": prompt.name,
                "content": prompt.content
            }
        }
    except PromptNotFoundError:
        raise HTTPException(status_code=404, detail="Prompt not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/prompts/{prompt_id}")
async def delete_prompt(
    request: Request,
    prompt_id: str,
    prompt_manager: PromptManager = Depends(get_prompt_manager)
):
    """Delete a prompt"""
    try:
        # Check admin permissions
        check_admin_permissions(request)
        
        # Delete prompt
        prompt_manager.delete_prompt(prompt_id)
        
        return {"message": "Prompt deleted successfully"}
    except PromptNotFoundError:
        raise HTTPException(status_code=404, detail="Prompt not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/users/invite")
async def invite_user(
    request: Request,
    background_tasks: BackgroundTasks,
    user_data: UserInvite,
    user_manager: UserManager = Depends(get_user_manager),
    activity_manager = Depends(get_activity_manager)
):
    """Send an invitation to a new user"""
    try:
        # Check admin permissions
        check_admin_permissions(request)
        
        logger.info(f"Invitation request received for username: {user_data.username}, email: {user_data.email}")
        
        user, error, token = user_manager.create_invitation(
            username=user_data.username,
            email=user_data.email,
            is_admin=user_data.is_admin,
            expiry_hours=user_data.expiry_hours
        )
        
        if error:
            logger.error(f"Invitation creation failed: {error}")
            
            # Add more specific error message with context
            if error == "Username already exists":
                error_detail = f"Username '{user_data.username}' already exists. Please choose a different username."
            elif error == "Email already exists":
                error_detail = f"Email '{user_data.email}' is already registered in the system."
            else:
                error_detail = error
                
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error_detail
            )
        
        logger.info(f"Invitation created successfully for {user.username} with id {user.id}")
        
        # Generate invitation URL (in real app, use a frontend URL)
        invitation_url = f"/accept-invitation?token={token}"
        
        # Send email in background
        logger.info(f"Scheduling invitation email to {user.email}")
        background_tasks.add_task(
            send_invitation_email,
            recipient_email=user.email,
            recipient_name=user.username,
            invitation_url=invitation_url,
            inviter_name=get_admin_user(request),
            is_admin=user.is_admin,
            expiry_hours=user_data.expiry_hours,
            personal_message=user_data.personal_message
        )
        
        # Create activity details with UUID-safe serialization
        activity_details = safe_json_dumps({
            "invited_user": user.id,
            "invited_email": user.email
        })
        
        # Log activity using ActivityManager
        activity_manager.create(
            user_id=user.id,
            action=ActivityType.register,
            resource_type="user",
            resource_id=str(user.id),
            metadata=activity_details
        )
        
        logger.info(f"Invitation process completed successfully for {user.email}")
        return {"message": f"Invitation sent to {user.email} successfully", "user_id": str(user.id)}
    except Exception as e:
        logger.exception(f"Unexpected error during invitation process: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/users/{user_id}/resend-invite")
async def resend_invitation(
    request: Request,
    background_tasks: BackgroundTasks,
    user_id: str,
    expiry_hours: int = Body(48),
    user_manager: UserManager = Depends(get_user_manager),
    activity_manager = Depends(get_activity_manager)
):
    """Resend invitation to an invited user"""
    try:
        # Check admin permissions
        check_admin_permissions(request)
        
        logger.info(f"Resend invitation request received for user ID: {user_id}")
        
        try:
            user_uuid = uuid.UUID(user_id)
        except ValueError:
            logger.warning(f"Invalid user ID format provided: {user_id}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid user ID format"
            )
        
        # Reset invitation
        user, error, token = user_manager.reset_invitation(
            user_id=user_uuid,
            expiry_hours=expiry_hours
        )
        
        if error:
            logger.error(f"Invitation reset failed: {error}")
            
            # Add more specific error message with context
            if error == "User not found":
                error_detail = f"User with ID '{user_id}' not found"
            elif error == "User is not in invited status":
                error_detail = f"User cannot be re-invited because they are not in 'invited' status"
            else:
                error_detail = error
                
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error_detail
            )
        
        logger.info(f"Invitation reset successfully for {user.username} with id {user.id}")
        
        # Generate invitation URL (in real app, use a frontend URL)
        invitation_url = f"/accept-invitation?token={token}"
        
        # Send email in background
        logger.info(f"Scheduling invitation email to {user.email}")
        background_tasks.add_task(
            send_invitation_email,
            recipient_email=user.email,
            recipient_name=user.username,
            invitation_url=invitation_url,
            inviter_name=get_admin_user(request),
            is_admin=user.is_admin,
            expiry_hours=expiry_hours,
            personal_message=f"Your previous invitation has been renewed by {get_admin_user(request)}."
        )
        
        # Create activity details with UUID-safe serialization
        activity_details = safe_json_dumps({
            "resent_invitation": user.id,
            "recipient_email": user.email
        })
        
        # Log activity using ActivityManager
        activity_manager.create(
            user_id=user.id,
            action=ActivityType.register,
            resource_type="user",
            resource_id=str(user.id),
            metadata=activity_details
        )
        
        logger.info(f"Invitation resend process completed successfully for {user.email}")
        return {"message": f"Invitation resent to {user.email} successfully"}
    except Exception as e:
        logger.exception(f"Unexpected error during invitation resend process: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e)) 