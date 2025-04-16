"""
Dashboard API routes
"""
from fastapi import APIRouter, Depends, HTTPException, Request
from typing import List, Dict, Any
from datetime import datetime, timedelta
import uuid

from app.dependencies.auth import require_auth
from app.managers.activity_manager import ActivityManager
from app.db import models
from app.models.activity import Activity, ActivitySummary, UserStats, ActivityResponse, ActivityType

# Create router
router = APIRouter(tags=["dashboard-api"])

def get_activity_manager() -> ActivityManager:
    """Dependency to get activity manager instance"""
    return ActivityManager()

@router.get("/stats", response_model=Dict[str, Any])
@require_auth()
async def get_dashboard_stats(
    request: Request,
    activity_manager: ActivityManager = Depends(get_activity_manager)
):
    """Get dashboard statistics for the current user"""
    user_id = uuid.UUID(request.session["user_id"])
    
    # Log the dashboard view activity
    activity_manager.log_activity(
        user_id=user_id,
        activity_type=ActivityType.view_dashboard,
        details={"description": "Viewed dashboard"}
    )
    
    # Get user stats
    stats = activity_manager.get_user_stats(user_id)
    return stats

@router.get("/activities", response_model=List[Dict[str, Any]])
@require_auth()
async def get_user_activities_endpoint(
    request: Request,
    limit: int = 10,
    activity_manager: ActivityManager = Depends(get_activity_manager)
):
    """Get recent activities for the current user"""
    user_id = uuid.UUID(request.session["user_id"])
    activities = activity_manager.get_user_activities(user_id, limit=limit)
    
    # Transform model objects to dictionaries
    result = []
    for activity in activities:
        result.append({
            "id": str(activity.id),
            "user_id": str(activity.user_id),
            "activity_type": activity.activity_type,
            "description": activity.activity_type.replace("_", " ").title(),
            "timestamp": activity.timestamp,
            "details": activity.details
        })
    
    return result

@router.get("/activity-by-type", response_model=List[Dict[str, Any]])
@require_auth()
async def get_activity_by_type_endpoint(
    request: Request,
    activity_manager: ActivityManager = Depends(get_activity_manager)
):
    """Get activity breakdown by type for the current user"""
    user_id = uuid.UUID(request.session["user_id"])
    activity_counts = activity_manager.count_user_activities_by_type(user_id)
    
    # Return data directly as a list of dictionaries
    return [
        {"label": item["activity_type"], "count": item["count"]} 
        for item in activity_counts
    ]

@router.get("/activity-by-date", response_model=List[Dict[str, Any]])
@require_auth()
async def get_activity_by_date_endpoint(
    request: Request,
    days: int = 30,
    activity_manager: ActivityManager = Depends(get_activity_manager)
):
    """Get activity counts by date for the current user"""
    user_id = uuid.UUID(request.session["user_id"])
    activity_by_date = activity_manager.count_user_activities_by_date(user_id, days)
    
    # Return data directly as a list of dictionaries
    return [
        {"label": item["date"], "count": item["count"]} 
        for item in activity_by_date
    ] 