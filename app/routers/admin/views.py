"""
Admin view handlers - Template rendering logic for admin routes
"""
from fastapi import Request, Depends, HTTPException, status, APIRouter
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from typing import Dict, List, Optional
from datetime import datetime
import uuid

from app.db.database import get_db
from app.db import models
from app.managers.user_manager import UserManager
from app.managers.team_manager import TeamManager
from app.managers.project_manager import ProjectManager
from app.managers.prompt_manager import PromptManager
from app.managers.activity_manager import ActivityManager
from app.routers.auth import get_current_user, is_admin
from app.utils import format_date

# Initialize templates
templates = Jinja2Templates(directory="app/templates")

router = APIRouter(tags=["Admin Views"])

# Admin dashboard
async def dashboard_view(
    request: Request,
    current_user: models.User = Depends(get_current_user),
    is_admin_user: bool = Depends(is_admin),
    db: Session = Depends(get_db)
):
    """Admin dashboard page"""
    if not is_admin_user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access admin area"
        )
    
    # Initialize managers
    user_manager = UserManager()
    project_manager = ProjectManager()
    prompt_manager = PromptManager()
    activity_manager = ActivityManager()
    
    # Get basic stats
    total_users = len(user_manager.get_all_users())
    total_projects = len(project_manager.get_all_projects())
    active_users = len(user_manager.get_active_users(days=7))
    
    # Get prompt count
    total_prompts = len(prompt_manager.get_all_prompts())
    
    # Get recent activities
    recent_activities = activity_manager.get_recent_activities(limit=10)
    formatted_activities = []
    
    for activity in recent_activities:
        activity_type = activity.activity_type
        icon = "person" if "user" in activity_type else "kanban" if "project" in activity_type else "chat-left-text" if "prompt" in activity_type else "people-fill" if "team" in activity_type else "gear"
        
        formatted_activities.append({
            "type": activity_type.split("_")[0].lower(),
            "icon": f"bi-{icon}",
            "title": format_activity_title(activity, db),
            "user": user_manager.get_username(activity.user_id),
            "time": format_date(activity.timestamp)
        })
    
    # Calculate stats changes (mock data for now)
    stats = {
        "active_users": active_users,
        "total_projects": total_projects,
        "total_prompts": total_prompts,
        "user_change": 12,
        "project_change": 8,
        "prompt_change": 15
    }
    
    return templates.TemplateResponse(
        "admin/dashboard.html",
        {
            "request": request,
            "user": current_user,
            "stats": stats,
            "recent_activities": formatted_activities,
            "active_page": "dashboard"
        }
    )

# Admin Users management
async def users_view(
    request: Request,
    current_user: models.User = Depends(get_current_user),
    is_admin_user: bool = Depends(is_admin),
    db: Session = Depends(get_db)
):
    """Admin users management page"""
    if not is_admin_user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access admin area"
        )
    
    # Get all users using UserManager
    user_manager = UserManager()
    users = user_manager.get_all_users()
    
    return templates.TemplateResponse(
        "admin/users.html",
        {
            "request": request,
            "user": current_user,
            "users": users,
            "active_page": "users"
        }
    )

# Admin Teams management
async def teams_view(
    request: Request,
    current_user: models.User = Depends(get_current_user),
    is_admin_user: bool = Depends(is_admin),
    db: Session = Depends(get_db)
):
    """Admin teams management page"""
    if not is_admin_user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access admin area"
        )
    
    # Get all teams using TeamManager
    team_manager = TeamManager()
    teams = team_manager.get_all_teams()
    
    # Enhance teams with user data for members
    team_data = []
    for team in teams:
        # Create team dict with extra data
        team_dict = {
            "id": team.id,
            "name": team.name,
            "description": team.description,
            "created_at": team.created_at,
            "updated_at": team.updated_at,
            "created_by": team.created_by,
            "projects": team.projects,
            "members": []
        }
        
        # Add enhanced member objects with username included
        if team.members:
            for member in team.members:
                user = team_manager.get_team_member_user(member.user_id)
                if user:
                    # Create member dict with user information
                    member_dict = {
                        "id": member.id,
                        "user_id": member.user_id,
                        "team_id": member.team_id,
                        "role": member.role,
                        "created_at": member.created_at,
                        "updated_at": member.updated_at,
                        "username": user.username,
                        "email": user.email
                    }
                    team_dict["members"].append(member_dict)
        
        team_data.append(team_dict)
    
    return templates.TemplateResponse(
        "admin/teams.html",
        {
            "request": request,
            "user": current_user,
            "teams": team_data,
            "active_page": "teams"
        }
    )

# Admin Projects management
async def projects_view(
    request: Request,
    current_user: models.User = Depends(get_current_user),
    is_admin_user: bool = Depends(is_admin),
    db: Session = Depends(get_db)
):
    """Admin projects management page"""
    if not is_admin_user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access admin area"
        )
    
    # Get all projects using ProjectManager
    project_manager = ProjectManager()
    projects = project_manager.get_all_projects()
    
    return templates.TemplateResponse(
        "admin/projects.html",
        {
            "request": request,
            "user": current_user,
            "projects": projects,
            "active_page": "projects"
        }
    )

# Admin Prompts management
async def prompts_view(
    request: Request,
    current_user: models.User = Depends(get_current_user),
    is_admin_user: bool = Depends(is_admin),
    db: Session = Depends(get_db)
):
    """Admin prompts management page"""
    if not is_admin_user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access admin area"
        )
    
    # Get all prompts using PromptManager
    prompt_manager = PromptManager()
    all_prompts = prompt_manager.get_all_prompts()
    
    # Format prompts with project information
    formatted_prompts = []
    for prompt in all_prompts:
        formatted_prompts.append({
            "id": prompt.id,
            "name": prompt.name,
            "project_name": prompt.project.name,
            "project_id": prompt.project.id,
            "version": prompt.version,
            "created_by": prompt.created_by_user.username,
            "created_at": format_date(prompt.created_at)
        })
    
    return templates.TemplateResponse(
        "admin/prompts.html",
        {
            "request": request,
            "user": current_user,
            "prompts": formatted_prompts,
            "active_page": "prompts"
        }
    )

# Admin Reports page
async def reports_view(
    request: Request,
    current_user: models.User = Depends(get_current_user),
    is_admin_user: bool = Depends(is_admin),
    db: Session = Depends(get_db)
):
    """Admin reports page"""
    if not is_admin_user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access admin area"
        )
    
    return templates.TemplateResponse(
        "admin/reports.html",
        {
            "request": request,
            "user": current_user,
            "active_page": "reports"
        }
    )

# Admin Logs page
async def logs_view(
    request: Request,
    current_user: models.User = Depends(get_current_user),
    is_admin_user: bool = Depends(is_admin),
    db: Session = Depends(get_db)
):
    """Admin logs page"""
    if not is_admin_user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access admin area"
        )
    
    # Get all activities using ActivityManager
    activity_manager = ActivityManager()
    activities = activity_manager.get_recent_activities(limit=100)
    
    # Format activities for display
    logs = []
    for activity in activities:
        logs.append({
            "id": str(activity.id),
            "user": activity.user.username,
            "activity_type": activity.activity_type,
            "created_at": format_date(activity.timestamp),
            "metadata": activity.metadata or {}
        })
    
    return templates.TemplateResponse(
        "admin/logs.html",
        {
            "request": request,
            "user": current_user,
            "logs": logs,
            "active_page": "logs"
        }
    )

# Admin Settings page
async def settings_view(
    request: Request,
    current_user: models.User = Depends(get_current_user),
    is_admin_user: bool = Depends(is_admin),
    db: Session = Depends(get_db)
):
    """Admin settings page"""
    if not is_admin_user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access admin area"
        )
    
    # Get settings (placeholder for now)
    settings = {
        "app_name": "PromptLane",
        "registration_enabled": True,
        "max_storage_per_user": "5GB",
        "default_prompt_limit": 100,
        "default_project_limit": 20
    }
    
    return templates.TemplateResponse(
        "admin/settings.html",
        {
            "request": request,
            "user": current_user,
            "settings": settings,
            "active_page": "settings"
        }
    )

# Admin Security page
async def security_view(
    request: Request,
    current_user: models.User = Depends(get_current_user),
    is_admin_user: bool = Depends(is_admin),
    db: Session = Depends(get_db)
):
    """Admin security page"""
    if not is_admin_user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access admin area"
        )
    
    # Get security settings (placeholder for now)
    security_settings = {
        "password_min_length": 8,
        "require_special_chars": True,
        "session_timeout_minutes": 30,
        "failed_login_limit": 5,
        "two_factor_required": False
    }
    
    return templates.TemplateResponse(
        "admin/security.html",
        {
            "request": request,
            "user": current_user,
            "security_settings": security_settings,
            "active_page": "security"
        }
    )

# Admin Help page
async def help_view(
    request: Request,
    current_user: models.User = Depends(get_current_user),
    is_admin_user: bool = Depends(is_admin)
):
    """Admin help page"""
    if not is_admin_user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access admin area"
        )
    
    return templates.TemplateResponse(
        "admin/help.html",
        {
            "request": request,
            "user": current_user,
            "active_page": "help"
        }
    )

# Helper functions
def format_activity_title(activity: models.Activity, db: Session) -> str:
    """Format activity title based on activity type and data"""
    if activity.activity_type == "user_created":
        return f"New user {activity.data.get('username', '')} joined"
    elif activity.activity_type == "project_created":
        return f"New project {activity.data.get('name', '')} created"
    elif activity.activity_type == "prompt_created":
        return f"New prompt {activity.data.get('name', '')} created"
    elif activity.activity_type == "team_created":
        return f"New team {activity.data.get('name', '')} created"
    elif activity.activity_type == "team_member_added":
        return f"New member added to team {activity.data.get('team_name', '')}"
    else:
        return activity.activity_type.replace("_", " ").title() 