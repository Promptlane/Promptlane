"""
Common functionality and dependencies for admin routes
"""
from fastapi import HTTPException, Request
import logging
from typing import Dict, Any
import uuid

from app.managers.user_manager import UserManager
from app.managers.activity_manager import ActivityManager
from app.utils import format_date

logger = logging.getLogger(__name__)

def get_activity_manager() -> ActivityManager:
    """Dependency to get ActivityManager instance"""
    return ActivityManager()

def format_activity_title(activity: Any, user_manager: UserManager) -> str:
    """Format activity title for display"""
    username = get_username(activity.user_id, user_manager)
    activity_type = activity.activity_type
    details = activity.details or {}
    
    if activity_type == "create_project":
        return f"{username} created a new project: {details.get('project_name', 'Unknown')}"
    elif activity_type == "update_project":
        return f"{username} updated project: {details.get('project_name', 'Unknown')}"
    elif activity_type == "delete_project":
        return f"{username} deleted project: {details.get('project_name', 'Unknown')}"
    elif activity_type == "create_prompt":
        return f"{username} created a new prompt: {details.get('prompt_name', 'Unknown')}"
    elif activity_type == "update_prompt":
        return f"{username} updated prompt: {details.get('prompt_name', 'Unknown')}"
    elif activity_type == "delete_prompt":
        return f"{username} deleted prompt: {details.get('prompt_name', 'Unknown')}"
    elif activity_type == "create_team":
        return f"{username} created a new team: {details.get('team_name', 'Unknown')}"
    elif activity_type == "add_team_member":
        return f"{username} added member to team: {details.get('team_name', 'Unknown')}"
    else:
        return f"{username} performed {activity_type}"

def get_username(user_id: uuid.UUID, user_manager: UserManager) -> str:
    """Get username by user ID"""
    try:
        user = user_manager.get_user(user_id)
        return user.username
    except Exception:
        return "Unknown User"

def get_admin_user(request: Request) -> str:
    """Get admin username from request"""
    user = request.session.get("user", {})
    return user.get("username", "Unknown Admin")

def check_admin_permissions(request: Request) -> None:
    """Check if user has admin permissions"""
    user = request.session.get("user", {})
    if not user or not user.get("is_admin", False):
        raise HTTPException(
            status_code=403,
            detail="Admin permissions required"
        ) 