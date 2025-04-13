from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import uuid

from app.dependencies.auth import require_auth
from app.managers.activity_manager import ActivityManager

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

def get_activity_manager() -> ActivityManager:
    """Dependency to get ActivityManager instance"""
    return ActivityManager()

@router.get("/dashboard", response_class=HTMLResponse)
@require_auth()
async def activity_dashboard(
    request: Request,
    activity_manager: ActivityManager = Depends(get_activity_manager)
):
    """Render the activity dashboard for the current user"""
    user_id = uuid.UUID(request.session["user_id"])
    
    stats = activity_manager.get_user_stats(user_id)
    recent_activities = activity_manager.get_user_activities(user_id, limit=5)
    activities_by_date = activity_manager.count_user_activities_by_date(user_id, days=7)
    activities_by_type = activity_manager.count_user_activities_by_type(user_id)
    
    # Convert to the expected format
    formatted_by_date = [
        {"date": activity["date"], "count": activity["count"]} 
        for activity in activities_by_date
    ]
    
    formatted_by_type = [
        {"type": activity["type"], "count": activity["count"]} 
        for activity in activities_by_type
    ]
    
    return templates.TemplateResponse(
        "activity_dashboard.html",
        {
            "request": request,
            "stats": stats,
            "recent_activities": recent_activities,
            "activities_by_date": formatted_by_date,
            "activities_by_type": formatted_by_type
        }
    ) 