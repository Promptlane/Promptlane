"""
Dashboard web routes
"""
from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from typing import List, Dict, Any
import uuid

from app.dependencies.auth import require_auth
from app.managers.activity_manager import ActivityManager
from app.managers.team_manager import TeamManager
from app.managers.project_manager import ProjectManager
from app.db import models
from app.models.activity import ActivityType

# Create router
router = APIRouter(tags=["dashboard-web"])

# Templates
templates = Jinja2Templates(directory="app/templates")

def get_activity_manager() -> ActivityManager:
    """Dependency to get activity manager instance"""
    return ActivityManager()

def get_team_manager() -> TeamManager:
    """Dependency to get team manager instance"""
    return TeamManager()

def get_project_manager() -> ProjectManager:
    """Dependency to get project manager instance"""
    return ProjectManager()

@router.get("", response_class=HTMLResponse)
@require_auth()
async def dashboard_page(
    request: Request,
    activity_manager: ActivityManager = Depends(get_activity_manager),
    team_manager: TeamManager = Depends(get_team_manager),
    project_manager: ProjectManager = Depends(get_project_manager)
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
    
    # Get projects count
    projects = project_manager.get_user_projects(user_id)
    project_count = len(projects)
    
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
            "stats": stats
        }
    ) 