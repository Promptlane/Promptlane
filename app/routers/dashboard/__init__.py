"""
Dashboard router package
"""
from fastapi import APIRouter
from .api import router as api_router
from .web import router as web_router

# Create main router
router = APIRouter(tags=["dashboard"])

# Include sub-routers with their respective prefixes
router.include_router(api_router, prefix="/api/dashboard")
router.include_router(web_router, prefix="/dashboard") 