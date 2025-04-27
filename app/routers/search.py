from fastapi import APIRouter, Request, Depends, Query
from app.templates import templates
from typing import Optional
from app.dependencies.auth import require_auth
from app.db.database import session_scope
from app.managers.search_manager import SearchManager

router = APIRouter(tags=["Search"])

@router.get("/search")
@require_auth()
async def search(
    request: Request,
    q: Optional[str] = Query(None),
    type: str = Query("all"),
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=100)
):
    """Search for projects and prompts with pagination and efficient querying"""
    with session_scope() as session:
        search_manager = SearchManager(session)
        projects, prompts, pagination = search_manager.search(
            query=q,
            search_type=type,
            page=page,
            per_page=per_page
        )
        
        return templates.TemplateResponse(
            "search_results.html",
            {
                "request": request,
                "query": q or "",
                "search_type": type,
                "projects": projects,
                "prompts": prompts,
                "pagination": pagination
            }
        ) 