"""
Team web routes
"""
from fastapi import APIRouter, Depends, HTTPException, Request, Path
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.managers.team_manager import TeamManager
from app.managers.user_manager import UserManager
from app.managers.activity_manager import ActivityManager
from app.models.team import TeamRole
from app.templates import templates
import uuid

from app.dependencies.auth import require_auth

router = APIRouter(tags=["teams-web"])

def get_team_manager() -> TeamManager:
    return TeamManager()

def get_user_manager() -> UserManager:
    return UserManager()

def get_activity_manager() -> ActivityManager:
    return ActivityManager()

@router.get("/", response_class=HTMLResponse)
@require_auth()
async def teams_page(
    request: Request,
    team_manager: TeamManager = Depends(get_team_manager),
    user_manager: UserManager = Depends(get_user_manager)
):
    """Team management page"""
    try:
        # Get current user
        current_user = request.state.user
        if not current_user:
            raise HTTPException(status_code=401, detail="Not authenticated")
            
        # Get user's teams
        teams = team_manager.get_user_teams(current_user.id)
        
        # Get team members and projects for each team
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
            "teams/list.html",
            {
                "request": request,
                "teams": team_details,
                "current_user": current_user
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/my", response_class=HTMLResponse)
@require_auth()
async def my_teams_page(
    request: Request,
    team_manager: TeamManager = Depends(get_team_manager),
    user_manager: UserManager = Depends(get_user_manager)
):
    """User's teams page"""
    try:
        # Get current user
        current_user = request.state.user
        if not current_user:
            raise HTTPException(status_code=401, detail="Not authenticated")
            
        # Get user's teams
        teams = team_manager.get_user_teams(current_user.id)
        
        # Get team details for each team
        team_details = []
        for team in teams:
            members = team_manager.get_team_members(team.id)
            projects = team_manager.get_team_projects(team.id)
            permissions = team_manager.check_team_permissions(team.id, current_user.id)
            team_details.append({
                "team": team,
                "members": members,
                "projects": projects,
                "permissions": permissions
            })
            
        return templates.TemplateResponse(
            "teams/my_teams.html",
            {
                "request": request,
                "teams": team_details,
                "current_user": current_user
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{team_id}", response_class=HTMLResponse)
@require_auth()
async def team_detail(
    request: Request,
    team_id: uuid.UUID,
    team_manager: TeamManager = Depends(get_team_manager),
    user_manager: UserManager = Depends(get_user_manager),
    activity_manager: ActivityManager = Depends(get_activity_manager)
):
    """Team detail page"""
    try:
        # Get current user
        current_user = request.state.user
        if not current_user:
            raise HTTPException(status_code=401, detail="Not authenticated")
            
        # Get team
        team = team_manager.get_team(team_id)
        if not team:
            raise HTTPException(status_code=404, detail="Team not found")
            
        # Check permissions
        permissions = team_manager.check_team_permissions(team_id, current_user.id)
        if not permissions["can_view"]:
            raise HTTPException(status_code=403, detail="Not authorized")
            
        # Get team details
        members = team_manager.get_team_members(team_id)
        projects = team_manager.get_team_projects(team_id)
        activity = team_manager.get_team_activity(team_id)
        
        return templates.TemplateResponse(
            "teams/detail.html",
            {
                "request": request,
                "team": team,
                "members": members,
                "projects": projects,
                "activity": activity,
                "permissions": permissions,
                "current_user": current_user
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/create", response_class=HTMLResponse)
@require_auth()
async def create_team_page(request: Request):
    """Team creation page"""
    try:
        # Get current user
        current_user = request.state.user
        if not current_user:
            raise HTTPException(status_code=401, detail="Not authenticated")
            
        return templates.TemplateResponse(
            "teams/create.html",
            {
                "request": request,
                "current_user": current_user
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{team_id:uuid}")
async def team_legacy_redirect(
    team_id: uuid.UUID,
    request: Request
):
    """Redirect legacy team URLs to the new format"""
    return RedirectResponse(url=f"/teams/id/{team_id}")

@router.get("/view/{team_id_or_my}")
async def team_view_redirect(
    team_id_or_my: str,
    request: Request
):
    """Redirect old view URLs to the new format"""
    if team_id_or_my == "my":
        return RedirectResponse(url="/teams/my")
    try:
        team_id = uuid.UUID(team_id_or_my)
        return RedirectResponse(url=f"/teams/id/{team_id}")
    except ValueError:
        return templates.TemplateResponse(
            "errors/404.html",
            {"request": request, "message": "Invalid team ID"},
            status_code=404
        ) 