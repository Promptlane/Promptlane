"""
Admin routes package
"""
from fastapi import APIRouter
from .web import router as web_router
from .api import router as api_router

# Create main admin router with prefix
router = APIRouter(prefix="/admin")

# Include sub-routers
router.include_router(web_router)
router.include_router(api_router) 