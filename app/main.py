"""
Main application entry point
"""
# Standard library imports
import os
from typing import List, Dict, Type

# Third-party imports
from fastapi import FastAPI, APIRouter, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from app.templates import templates
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException
import uvicorn

# Local application imports
from app.config import settings
from app.logger import get_logger
from app.middleware import LoggingMiddleware, AuthRedirectMiddleware, SettingsContextMiddleware
from app.error_handlers import not_found_error, server_error

# Router registry
ROUTER_REGISTRY: Dict[str, Type[APIRouter]] = {
    "auth": "app.routers.auth.router",
    "projects": "app.routers.projects.router",
    "prompts": "app.routers.prompts.router",
    "search": "app.routers.search.router",
    "dashboard": "app.routers.dashboard.router",
    "teams": "app.routers.teams.router",
    "activities": "app.routers.activities.router",
    "admin": "app.routers.admin.router",
    "common": "app.routers.common.router"
}

# Initialize logger
logger = get_logger(__name__)
# Development imports (conditional)
if settings.ENVIRONMENT.lower() != "production":
    ROUTER_REGISTRY["dev"] = "app.routers.dev.dev_router"
    logger.info("Dev router loaded (available only in development mode)")

def get_router(router_name: str) -> APIRouter:
    """Dynamically import and return a router from the registry"""
    module_path, router_name = ROUTER_REGISTRY[router_name].rsplit(".", 1)
    module = __import__(module_path, fromlist=[router_name])
    return getattr(module, router_name)

def create_app() -> FastAPI:
    """Create and configure the FastAPI application"""
    app = FastAPI(
        title=settings.APP.NAME,
        description=settings.APP.DESCRIPTION,
        version=settings.APP.VERSION,
        debug=settings.DEBUG,
    )

    # Add middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.API.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(
        SessionMiddleware,
        secret_key=settings.SECURITY.JWT_SECRET_KEY,
        session_cookie=settings.SECURITY.SESSION_COOKIE_NAME,
        max_age=settings.SECURITY.SESSION_MAX_AGE,
        same_site=settings.SECURITY.SESSION_SAME_SITE,
        https_only=settings.SECURITY.SESSION_HTTPS_ONLY
    )
    app.add_middleware(LoggingMiddleware)
    app.add_middleware(AuthRedirectMiddleware)
    app.add_middleware(SettingsContextMiddleware)

    # Mount static files
    app.mount("/static", StaticFiles(directory="app/static"), name="static")
    
    # Register error handlers
    app.add_exception_handler(404, not_found_error)
    app.add_exception_handler(StarletteHTTPException, not_found_error)
    app.add_exception_handler(Exception, server_error)

    # API routes
    api_routers = [get_router(name) for name in ROUTER_REGISTRY.keys()]
    
    # UI routes (exclude dev router from UI)
    ui_routers = [get_router(name) for name in ROUTER_REGISTRY.keys() 
                 if name != "dev" or settings.DEBUG]

    # Mount API routers with prefix
    for router in api_routers:
        app.include_router(router, prefix=settings.API.V1_PREFIX)

    # Mount UI routers without prefix
    for router in ui_routers:
        app.include_router(router)

    # Add debug routes if in debug mode
    if settings.DEBUG:
        @app.get("/test-404")
        async def test_404():
            raise HTTPException(status_code=404, detail="Test 404 error")
            
        @app.get("/test-500")
        async def test_500():
            raise ValueError("Test server error")

    return app

# Create the application
app = create_app()

# Run the application if executed directly
if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.SERVER.HOST,
        port=settings.SERVER.PORT,
        reload=settings.SERVER.RELOAD,
        workers=settings.SERVER.WORKERS
    ) 