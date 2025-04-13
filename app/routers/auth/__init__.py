"""
Auth router package
"""
from fastapi import APIRouter

from .api import router as api_router
from .web import router as web_router

# Create a combined router for auth
router = APIRouter(tags=["auth"])

# Include both API and web routers
router.include_router(api_router, prefix="/api")
router.include_router(web_router)

# Export dependencies
__all__ = ["router"] 