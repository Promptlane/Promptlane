"""
Dashboard web routes
"""
from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from app.templates import templates
from typing import List, Dict, Any
import uuid
from datetime import datetime, timedelta

from app.dependencies.auth import require_auth
from app.managers.activity_manager import ActivityManager
from app.managers.team_manager import TeamManager
from app.managers.project_manager import ProjectManager
from app.managers.prompt_manager import PromptManager
from app.db import models
from app.models.activity import ActivityType
from app.utils.format_date import format_relative_time

# Create router
router = APIRouter(tags=["dashboard-web"])

def get_activity_manager() -> ActivityManager:
    """Dependency to get activity manager instance"""
    return ActivityManager()

def get_team_manager() -> TeamManager:
    """Dependency to get team manager instance"""
    return TeamManager()

def get_project_manager() -> ProjectManager:
    """Dependency to get project manager instance"""
    return ProjectManager()

def get_prompt_manager() -> PromptManager:
    """Dependency to get prompt manager instance"""
    return PromptManager()

@router.get("", response_class=HTMLResponse)
@require_auth()
async def dashboard_page(
    request: Request,
    activity_manager: ActivityManager = Depends(get_activity_manager),
    team_manager: TeamManager = Depends(get_team_manager),
    project_manager: ProjectManager = Depends(get_project_manager),
    prompt_manager: PromptManager = Depends(get_prompt_manager)
):
    """Render the dashboard page"""
    user_id = uuid.UUID(request.session["user_id"])
    
    # Log the dashboard view
    activity_manager.create_activity(
        user_id=user_id,
        activity_type=ActivityType.view_dashboard,
        details={"description": "Viewed dashboard"}
    )
    
    # Get user stats
    user_stats = activity_manager.get_user_stats(user_id)
    
    # Get teams count
    teams = team_manager.get_user_teams(user_id)
    team_count = len(teams)
    
    # Get recent projects (limit to 3)
    projects = project_manager.get_user_projects(user_id)
    project_count = len(projects)
    recent_projects = projects[:3]
    
    # Get recent prompts (limit to 6)
    recent_prompts = prompt_manager.get_recent_prompts(user_id, limit=6)
    
    # Format projects data
    formatted_projects = [
        {
            "id": str(project.id),
            "name": project.name,
            "description": project.description,
            "created_at": format_relative_time(project.created_at)
        }
        for project in recent_projects
    ]
    
    # Format prompts data
    formatted_prompts = [
        {
            "id": str(prompt.id),
            "name": prompt.name,
            "description": prompt.description,
            "project_id": str(prompt.project_id),
            "project_name": next(
                (p.name for p in projects if p.id == prompt.project_id),
                "Unknown Project"
            ),
            "version": getattr(prompt, "version", "1"),
            "created_at": format_relative_time(prompt.created_at)
        }
        for prompt in recent_prompts
    ]
    
    # Create simplified stats object for template
    stats = {
        "total_projects": project_count,
        "total_teams": team_count,
        "recent_activity_count": user_stats.get("total_activities", 0)
    }
    
    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            "user": request.session["user"],
            "stats": stats,
            "recent_projects": formatted_projects,
            "recent_prompts": formatted_prompts
        }
    ) 