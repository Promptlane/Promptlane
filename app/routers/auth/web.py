from fastapi import APIRouter, Request, Depends, status, Form
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
import uuid

from app.db.database import get_db
from app.db.models import ActivityType
from app.managers.user_manager import UserManager
from app.managers.activity_manager import ActivityManager

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    """Render login page"""
    # If user is already logged in, redirect to home
    if "user_id" in request.session:
        # If next parameter is provided, redirect there instead
        next_url = request.query_params.get("next")
        if next_url:
            return RedirectResponse(url=next_url, status_code=status.HTTP_303_SEE_OTHER)
        return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
    
    return templates.TemplateResponse(
        "login.html", 
        {
            "request": request, 
            "error": None,
            "next": request.query_params.get("next", "/")
        }
    )

@router.post("/login", response_class=HTMLResponse)
async def login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    next: str = Form("/"),
    db: Session = Depends(get_db)
):
    """Process login form"""
    user_manager = UserManager()
    activity_manager = ActivityManager()
    
    # Try to verify user
    user = user_manager.verify_user(username, password)
    if not user:
        return templates.TemplateResponse(
            "login.html",
            {
                "request": request, 
                "error": "Invalid username or password",
                "next": next
            }
        )
    
    # Set session data
    request.session["user_id"] = str(user.id)
    request.session["username"] = user.username
    request.session["user"] = {
        "id": str(user.id),
        "username": user.username,
        "is_admin": user.is_admin
    }
    
    # Log login activity
    activity_manager.create_activity(
        user_id=user.id,
        activity_type=ActivityType.LOGIN,
        details={"username": username}
    )
    
    # Redirect to the next URL or home page
    return RedirectResponse(url=next, status_code=status.HTTP_303_SEE_OTHER)

@router.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    """Render registration page"""
    # If user is already logged in, redirect to home
    if "user_id" in request.session:
        return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
    
    return templates.TemplateResponse(
        "register.html", 
        {"request": request, "error": None}
    )

@router.post("/register", response_class=HTMLResponse)
async def register(
    request: Request,
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    confirm_password: str = Form(...),
):
    """Process registration form"""
    user_manager = UserManager()
    activity_manager = ActivityManager()
    
    # Validate input
    if password != confirm_password:
        return templates.TemplateResponse(
            "register.html",
            {"request": request, "error": "Passwords do not match"}
        )
    
    # Create user
    user, error = user_manager.create_user(username, email, password)
    if error:
        return templates.TemplateResponse(
            "register.html",
            {"request": request, "error": error}
        )
    
    # Set session data
    request.session["user_id"] = str(user.id)
    request.session["username"] = user.username
    request.session["user"] = {
        "id": str(user.id),
        "username": user.username,
        "is_admin": user.is_admin
    }
    
    # Log registration activity
    activity_manager.create(
        type=ActivityType.REGISTER,
        description=f"User {username} registered",
        user_id=user.id
    )
    
    # Redirect to home page
    return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)

@router.get("/logout")
async def logout(request: Request):
    """Log out user"""
    activity_manager = ActivityManager()
    
    # Log logout activity if user is logged in
    user_id = request.session.get("user_id")
    if user_id:
        try:
            user_uuid = uuid.UUID(user_id)
            username = request.session.get("username", "Unknown")
            activity_manager.create(
                type=ActivityType.LOGOUT,
                description=f"User {username} logged out",
                user_id=user_uuid
            )
        except:
            pass
    
    request.session.clear()
    return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)

@router.get("/accept-invitation", response_class=HTMLResponse)
async def accept_invitation_page(
    request: Request,
    token: str
):
    """Render the invitation acceptance page"""
    user_manager = UserManager()
    
    # Check if token is valid
    user = user_manager.get_user_by_invitation_token(token)
    if not user:
        return templates.TemplateResponse(
            "errors/404.html",
            {"request": request, "message": "Invalid or expired invitation"},
            status_code=404
        )
    
    # If user is already logged in, log them out first
    if "user_id" in request.session:
        request.session.clear()
    
    return templates.TemplateResponse(
        "auth/accept_invitation.html",
        {
            "request": request,
            "token": token,
            "email": user.email,
            "error": None
        }
    ) 