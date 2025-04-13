"""
Teams API routes
"""
from fastapi import APIRouter, Request, HTTPException, status, Depends, Query
from typing import List, Dict, Any, Optional
import uuid
from datetime import datetime
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db import models
from app.models.team import (
    TeamCreate, TeamUpdate, TeamResponse, TeamDetailResponse,
    TeamMemberCreate, TeamMemberUpdate, TeamMemberResponse, TeamRole
)
from app.models.user import UserResponse
from app.dependencies.auth import require_auth
from app.models.activity import ActivityType
from app.managers.team_manager import TeamManager
from app.managers.activity_manager import ActivityManager
from app.managers.user_manager import UserManager

# Create router
router = APIRouter(tags=["teams-api"])

def get_team_manager() -> TeamManager:
    """Dependency to get team manager instance"""
    return TeamManager()

def get_activity_manager() -> ActivityManager:
    """Dependency to get activity manager instance"""
    return ActivityManager()

def get_user_manager() -> UserManager:
    """Dependency to get user manager instance"""
    return UserManager()

@router.post("/", response_model=Dict[str, Any])
@require_auth()
async def create_team(
    request: Request,
    team_data: Dict[str, Any],
    team_manager: TeamManager = Depends(get_team_manager),
    activity_manager: ActivityManager = Depends(get_activity_manager)
):
    """Create a new team"""
    user_id = uuid.UUID(request.session["user_id"])
    
    # Create team
    team = team_manager.create_team(
        name=team_data["name"],
        description=team_data.get("description", ""),
        created_by=user_id
    )
    
    # Log activity
    activity_manager.create(
        type=ActivityType.TEAM_CREATED,
        description=f"Created team: {team.name}",
        user_id=user_id
    )
    
    return {
        "id": str(team.id),
        "name": team.name,
        "description": team.description,
        "created_at": team.created_at,
        "updated_at": team.updated_at
    }

@router.get("/", response_model=List[Dict[str, Any]])
@require_auth()
async def get_teams(
    request: Request,
    team_manager: TeamManager = Depends(get_team_manager)
):
    """Get all teams for the current user"""
    user_id = uuid.UUID(request.session["user_id"])
    teams = team_manager.get_user_teams(user_id)
    
    return [
        {
            "id": str(team.id),
            "name": team.name,
            "description": team.description,
            "created_at": team.created_at,
            "updated_at": team.updated_at
        }
        for team in teams
    ]

@router.get("/{team_id}", response_model=Dict[str, Any])
@require_auth()
async def get_team(
    request: Request,
    team_id: str,
    team_manager: TeamManager = Depends(get_team_manager)
):
    """Get team details"""
    user_id = uuid.UUID(request.session["user_id"])
    team = team_manager.get_team(team_id)
    
    # Verify team ownership or membership
    if not team_manager.is_team_member(team_id, user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this team"
        )
    
    return {
        "id": str(team.id),
        "name": team.name,
        "description": team.description,
        "created_at": team.created_at,
        "updated_at": team.updated_at
    }

@router.put("/{team_id}", response_model=Dict[str, Any])
@require_auth()
async def update_team(
    request: Request,
    team_id: str,
    team_data: Dict[str, Any],
    team_manager: TeamManager = Depends(get_team_manager),
    activity_manager: ActivityManager = Depends(get_activity_manager)
):
    """Update team details"""
    user_id = uuid.UUID(request.session["user_id"])
    
    # Verify team ownership
    if not team_manager.is_team_owner(team_id, user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this team"
        )
    
    # Update team
    team = team_manager.update_team(
        team_id=team_id,
        name=team_data["name"],
        description=team_data.get("description", "")
    )
    
    # Log activity
    activity_manager.create(
        type=ActivityType.TEAM_UPDATED,
        description=f"Updated team: {team.name}",
        user_id=user_id
    )
    
    return {
        "id": str(team.id),
        "name": team.name,
        "description": team.description,
        "created_at": team.created_at,
        "updated_at": team.updated_at
    }

@router.delete("/{team_id}")
@require_auth()
async def delete_team(
    request: Request,
    team_id: str,
    team_manager: TeamManager = Depends(get_team_manager),
    activity_manager: ActivityManager = Depends(get_activity_manager)
):
    """Delete a team"""
    user_id = uuid.UUID(request.session["user_id"])
    
    # Verify team ownership
    if not team_manager.is_team_owner(team_id, user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this team"
        )
    
    # Get team name for logging
    team = team_manager.get_team(team_id)
    
    # Delete team
    team_manager.delete_team(team_id)
    
    # Log activity
    activity_manager.create(
        type=ActivityType.TEAM_DELETED,
        description=f"Deleted team: {team.name}",
        user_id=user_id
    )
    
    return {"message": "Team deleted successfully"}

@router.post("/{team_id}/members", response_model=TeamMemberResponse)
@require_auth()
async def add_member_to_team(
    request: Request,
    team_id: str,
    member_create: TeamMemberCreate,
    team_manager: TeamManager = Depends(get_team_manager),
    activity_manager: ActivityManager = Depends(get_activity_manager)
):
    """Add a member to a team"""
    try:
        team_uuid = uuid.UUID(team_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid team ID format"
        )
    
    team = team_manager.get_team(team_uuid)
    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team not found"
        )
    
    # Verify team membership
    user_id = uuid.UUID(request.session["user_id"])
    if not team_manager.is_user_in_team(user_id, team_uuid):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to manage team members"
        )
    
    # Add member
    member = team_manager.add_team_member(
        team_id=team_uuid,
        user_id=member_create.user_id,
        role=member_create.role
    )
    
    # Log activity
    activity_manager.create(
        type=ActivityType.TEAM_MEMBER_ADDED,
        description=f"Member added to team {team.name}",
        user_id=user_id
    )
    
    return TeamMemberResponse.from_orm(member)

@router.put("/{team_id}/members/{user_id}", response_model=TeamMemberResponse)
@require_auth()
async def update_team_member(
    request: Request,
    team_id: str,
    user_id: str,
    member_update: TeamMemberUpdate,
    team_manager: TeamManager = Depends(get_team_manager),
    activity_manager: ActivityManager = Depends(get_activity_manager)
):
    """Update a team member's role"""
    try:
        team_uuid = uuid.UUID(team_id)
        member_uuid = uuid.UUID(user_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid ID format"
        )
    
    team = team_manager.get_team(team_uuid)
    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team not found"
        )
    
    # Verify team membership
    user_id = uuid.UUID(request.session["user_id"])
    if not team_manager.is_user_in_team(user_id, team_uuid):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to manage team members"
        )
    
    # Update member role
    updated_member = team_manager.update_team_member(
        team_id=team_uuid,
        user_id=member_uuid,
        role=member_update.role
    )
    
    # Log activity
    activity_manager.create(
        type=ActivityType.TEAM_MEMBER_UPDATED,
        description=f"Member role updated in team {team.name}",
        user_id=user_id
    )
    
    return TeamMemberResponse.from_orm(updated_member)

@router.delete("/{team_id}/members/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
@require_auth()
async def remove_member_from_team(
    request: Request,
    team_id: str,
    user_id: str,
    team_manager: TeamManager = Depends(get_team_manager),
    activity_manager: ActivityManager = Depends(get_activity_manager)
):
    """Remove a member from a team"""
    try:
        team_uuid = uuid.UUID(team_id)
        member_uuid = uuid.UUID(user_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid ID format"
        )
    
    team = team_manager.get_team(team_uuid)
    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team not found"
        )
    
    # Verify team membership
    user_id = uuid.UUID(request.session["user_id"])
    if not team_manager.is_user_in_team(user_id, team_uuid):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to manage team members"
        )
    
    # Remove member
    team_manager.remove_team_member(team_uuid, member_uuid)
    
    # Log activity
    activity_manager.create(
        type=ActivityType.TEAM_MEMBER_REMOVED,
        description=f"Member removed from team {team.name}",
        user_id=user_id
    )

@router.get("/users/search", response_model=List[UserResponse])
@require_auth()
async def search_users(
    query: str = Query(..., min_length=2),
    user_manager: UserManager = Depends(get_user_manager)
):
    """Search for users by username or email"""
    users = user_manager.search_users(query)
    return [UserResponse.from_orm(user) for user in users]

@router.post("/{team_id}/projects", status_code=status.HTTP_201_CREATED)
@require_auth()
async def add_project_to_team(
    request: Request,
    team_id: str,
    project_data: Dict,
    team_manager: TeamManager = Depends(get_team_manager),
    activity_manager: ActivityManager = Depends(get_activity_manager)
):
    """Add a project to a team"""
    try:
        team_uuid = uuid.UUID(team_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid team ID format"
        )
    
    team = team_manager.get_team(team_uuid)
    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team not found"
        )
    
    # Verify team membership
    user_id = uuid.UUID(request.session["user_id"])
    if not team_manager.is_user_in_team(user_id, team_uuid):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to manage team projects"
        )
    
    # Create project
    project = team_manager.create_project(
        team_id=team_uuid,
        name=project_data["name"],
        description=project_data.get("description"),
        user_id=user_id
    )
    
    # Log activity
    activity_manager.create(
        type=ActivityType.PROJECT_CREATED,
        description=f"Project {project.name} created in team {team.name}",
        user_id=user_id
    )
    
    return {
        "id": str(project.id),
        "name": project.name,
        "description": project.description,
        "team_id": str(project.team_id),
        "created_by": str(project.created_by),
        "created_at": project.created_at,
        "updated_at": project.updated_at
    } 