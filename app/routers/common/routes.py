"""
Common routes and error handlers
"""
import os
import traceback
import json
from fastapi import APIRouter, Request, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy import text
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.config import settings
from app.db.database import get_db
from app.logger import get_logger
from app.utils import JSONEncoder

# Initialize router and templates
router = APIRouter()
templates = Jinja2Templates(directory="app/templates")
logger = get_logger(__name__)

# Custom JSONResponse that uses our UUID-aware encoder
class CustomJSONResponse(JSONResponse):
    def render(self, content) -> bytes:
        return json.dumps(
            content,
            ensure_ascii=False,
            allow_nan=False,
            indent=None,
            separators=(",", ":"),
            cls=JSONEncoder,
        ).encode("utf-8")

# Route handlers
@router.get("/healthcheck")
async def healthcheck(db: Session = Depends(get_db)):
    # Check database connection
    try:
        db.execute(text("SELECT 1"))
        return {"status": "healthy"}
    except Exception as e:
        logger.error(f"Healthcheck failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database connection failed"
        )

@router.get("/")
async def root(request: Request):
    # Check if user is logged in
    if "user" in request.session:
        return templates.TemplateResponse(
            "home.html",
            {"request": request, "user": request.session["user"]}
        )
    return templates.TemplateResponse(
        "home.html",
        {"request": request}
    ) 