from fastapi import APIRouter, Request, Depends, HTTPException, status, Form
from sqlalchemy.orm import Session
import uuid

from app.db.models import ActivityType
from app.managers.user_manager import UserManager
from app.managers.activity_manager import ActivityManager
from app.dependencies.auth import require_auth

router = APIRouter()

@router.post("/login")
async def api_login(
    request: Request, 
    username: str = Form(...), 
    password: str = Form(...),
):
    """API endpoint for login"""
    user_manager = UserManager()
    activity_manager = ActivityManager()
    
    user = user_manager.verify_user(username, password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )
    
    # Log login activity
    activity_manager.create(
        type=ActivityType.LOGIN,
        description=f"User {username} logged in",
        user_id=user.id
    )
    
    # Generate JWT token
    token = user_manager.generate_token(user)
    
    # Set session data for web routes
    request.session["user_id"] = str(user.id)
    request.session["username"] = user.username
    request.session["user"] = {
        "id": str(user.id),
        "username": user.username,
        "is_admin": user.is_admin
    }
    
    # Return user info and token
    return {
        "id": str(user.id),
        "username": user.username,
        "email": user.email,
        "is_admin": user.is_admin,
        "token": token
    }

@router.post("/register")
async def api_register(
    request: Request, 
    username: str = Form(...), 
    email: str = Form(...), 
    password: str = Form(...),
):
    """API endpoint for registration"""
    user_manager = UserManager()
    activity_manager = ActivityManager()
    
    # Create user
    user, error = user_manager.create_user(username, email, password)
    if error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error
        )
    
    # Log registration activity
    activity_manager.create(
        type=ActivityType.REGISTER,
        description=f"User {username} registered",
        user_id=user.id
    )
    
    # Set session data
    request.session["user_id"] = str(user.id)
    request.session["username"] = user.username
    request.session["user"] = {
        "id": str(user.id),
        "username": user.username,
        "is_admin": user.is_admin
    }
    
    # Return user info
    return {
        "id": str(user.id),
        "username": user.username,
        "email": user.email,
        "is_admin": user.is_admin
    }

@router.post("/complete-registration")
async def complete_registration(
    request: Request,
    token: str = Form(...),
    password: str = Form(...),
    password_confirm: str = Form(...),
):
    """Complete registration with invitation token"""
    user_manager = UserManager()
    activity_manager = ActivityManager()
    
    # Validate passwords match
    if password != password_confirm:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Passwords do not match"
        )
    
    # Complete registration
    user, error = user_manager.complete_invitation(token, password)
    if error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error
        )
    
    # Log registration activity
    activity_manager.create(
        type=ActivityType.REGISTER,
        description=f"User {user.username} completed registration",
        user_id=user.id
    )
    
    # Set session data
    request.session["user_id"] = str(user.id)
    request.session["username"] = user.username
    request.session["user"] = {
        "id": str(user.id),
        "username": user.username,
        "is_admin": user.is_admin
    }
    
    # Return user info
    return {
        "id": str(user.id),
        "username": user.username,
        "email": user.email,
        "is_admin": user.is_admin
    }

@router.get("/me")
@require_auth()
async def get_current_user_info(request: Request):
    """Get current user information"""
    return request.session["user"]

@router.post("/logout")
@require_auth()
async def api_logout(request: Request):
    """API endpoint for logout"""
    activity_manager = ActivityManager()
    
    # Log logout activity
    user_id = request.session.get("user_id")
    username = request.session.get("username", "Unknown")
    if user_id:
        activity_manager.create(
            type=ActivityType.LOGOUT,
            description=f"User {username} logged out",
            user_id=uuid.UUID(user_id)
        )
    
    # Clear session
    request.session.clear()
    return {"message": "Logged out successfully"} 