"""
Admin web routes
"""
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse
from app.managers.user_manager import UserManager
from app.managers.team_manager import TeamManager
from app.managers.project_manager import ProjectManager
from app.managers.activity_manager import ActivityManager
from app.managers.prompt_manager import PromptManager
from app.templates import templates
from .common import get_username, get_admin_user, check_admin_permissions
import uuid

router = APIRouter(prefix="/web")

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

@router.get("/", response_class=HTMLResponse)
async def admin_dashboard(
    request: Request,
    user_manager: UserManager = Depends(get_user_manager),
    team_manager: TeamManager = Depends(get_team_manager),
    project_manager: ProjectManager = Depends(get_project_manager)
):
    """Admin dashboard page"""
    try:
        # Check admin permissions
        check_admin_permissions(request)
        
        # Get stats
        total_users = user_manager.get_total_users()
        total_teams = team_manager.get_total_teams()
        total_projects = project_manager.get_total_projects()
        
        # Get recent activity
        activity = user_manager.get_recent_activity(limit=10)
        
        return templates.TemplateResponse(
            "admin/dashboard.html",
            {
                "request": request,
                "stats": {
                    "total_users": total_users,
                    "total_teams": total_teams,
                    "total_projects": total_projects
                },
                "activity": activity,
                "admin_user": get_admin_user(request)
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/users", response_class=HTMLResponse)
async def admin_users(
    request: Request,
    user_manager: UserManager = Depends(get_user_manager)
):
    """Admin users management page"""
    try:
        # Check admin permissions
        check_admin_permissions(request)
        
        # Get all users
        users = user_manager.get_all_users()
        
        return templates.TemplateResponse(
            "admin/users.html",
            {
                "request": request,
                "users": users,
                "admin_user": get_admin_user(request)
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/teams", response_class=HTMLResponse)
async def admin_teams(
    request: Request,
    team_manager: TeamManager = Depends(get_team_manager),
    user_manager: UserManager = Depends(get_user_manager)
):
    """Admin teams management page"""
    try:
        # Check admin permissions
        check_admin_permissions(request)
        
        # Get all teams with details
        teams = team_manager.get_all_teams()
        team_details = []
        for team in teams:
            members = team_manager.get_team_members(team.id)
            projects = team_manager.get_team_projects(team.id)
            team_details.append({
                "team": team,
                "members": members,
                "projects": projects
            })
        
        return templates.TemplateResponse(
            "admin/teams.html",
            {
                "request": request,
                "teams": team_details,
                "admin_user": get_admin_user(request)
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/projects", response_class=HTMLResponse)
async def admin_projects(
    request: Request,
    project_manager: ProjectManager = Depends(get_project_manager),
    user_manager: UserManager = Depends(get_user_manager)
):
    """Admin projects management page"""
    try:
        # Check admin permissions
        check_admin_permissions(request)
        
        # Get all projects with details
        projects = project_manager.get_all_projects()
        project_details = []
        for project in projects:
            creator = user_manager.get_user(project.created_by)
            project_details.append({
                "project": project,
                "creator": creator.username if creator else "Unknown"
            })
        
        return templates.TemplateResponse(
            "admin/projects.html",
            {
                "request": request,
                "projects": project_details,
                "admin_user": get_admin_user(request)
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/prompts", response_class=HTMLResponse)
async def admin_prompts(
    request: Request,
    prompt_manager: PromptManager = Depends(get_prompt_manager),
    user_manager: UserManager = Depends(get_user_manager)
):
    """Admin prompts management page"""
    try:
        # Check admin permissions
        check_admin_permissions(request)
        
        # Get all prompts with details
        prompts = prompt_manager.get_all_prompts()
        prompt_details = []
        for prompt in prompts:
            creator = user_manager.get_user(prompt.created_by)
            prompt_details.append({
                "prompt": prompt,
                "creator": creator.username if creator else "Unknown"
            })
        
        return templates.TemplateResponse(
            "admin/prompts.html",
            {
                "request": request,
                "prompts": prompt_details,
                "admin_user": get_admin_user(request)
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/logs", response_class=HTMLResponse)
async def admin_logs(
    request: Request,
    activity_manager: ActivityManager = Depends(get_activity_manager),
    user_manager: UserManager = Depends(get_user_manager)
):
    """Admin logs page"""
    try:
        # Check admin permissions
        check_admin_permissions(request)
        
        # Get recent activities
        activities = activity_manager.get_recent_activities(limit=100)
        
        # Format logs with usernames
        logs = []
        for activity in activities:
            username = user_manager.get_username(activity.user_id)
            logs.append({
                "id": str(activity.id),
                "user": username,
                "activity_type": activity.activity_type,
                "created_at": activity.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                "metadata": activity.details or {}
            })
        
        return templates.TemplateResponse(
            "admin/logs.html",
            {
                "request": request,
                "logs": logs,
                "admin_user": get_admin_user(request)
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 