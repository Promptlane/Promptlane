from fastapi import APIRouter, Depends, Request
from typing import List
import uuid

from app.db import models
from app.models.activity import Activity, ActivitySummary, UserStats
from app.dependencies.auth import require_auth
from app.managers.activity_manager import ActivityManager

router = APIRouter()

def get_activity_manager() -> ActivityManager:
    """Dependency to get ActivityManager instance"""
    return ActivityManager()

@router.get("/recent", response_model=List[Activity])
@require_auth()
async def get_user_recent_activities(
    request: Request,
    limit: int = 10,
    activity_manager: ActivityManager = Depends(get_activity_manager)
):
    """Get recent activities for the current user"""
    user_id = uuid.UUID(request.session["user_id"])
    activities = activity_manager.get_user_activities(user_id, limit=limit)
    return activities

@router.get("/by-date", response_model=List[ActivitySummary])
@require_auth()
async def get_user_activities_by_date(
    request: Request,
    days: int = 30,
    activity_manager: ActivityManager = Depends(get_activity_manager)
):
    """Get user activities grouped by date for the last N days"""
    user_id = uuid.UUID(request.session["user_id"])
    activities_by_date = activity_manager.count_user_activities_by_date(user_id, days)
    
    # Convert to ActivitySummary format
    return [
        ActivitySummary(label=activity["date"], count=activity["count"]) 
        for activity in activities_by_date
    ]

@router.get("/by-type", response_model=List[ActivitySummary])
@require_auth()
async def get_user_activities_by_type(
    request: Request,
    activity_manager: ActivityManager = Depends(get_activity_manager)
):
    """Get user activities grouped by type"""
    user_id = uuid.UUID(request.session["user_id"])
    activities_by_type = activity_manager.count_user_activities_by_type(user_id)
    
    # Convert to ActivitySummary format
    return [
        ActivitySummary(label=activity["type"], count=activity["count"]) 
        for activity in activities_by_type
    ]

@router.get("/stats", response_model=UserStats)
@require_auth()
async def get_current_user_stats(
    request: Request,
    activity_manager: ActivityManager = Depends(get_activity_manager)
):
    """Get statistics for the current user"""
    user_id = uuid.UUID(request.session["user_id"])
    stats = activity_manager.get_user_stats(user_id)
    return stats 