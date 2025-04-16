from fastapi import APIRouter, Request, Depends, Query
from app.templates import templates
from typing import Dict, List, Optional
import app.db as db
from app.utils import format_date, extract_variables
from app.dependencies.auth import require_auth

router = APIRouter(tags=["Search"])

@router.get("/search")
@require_auth()
async def search(
    request: Request,
    q: Optional[str] = Query(None),
    type: str = Query("all")
):
    """Search for projects and prompts"""
    projects = []
    prompts = []
    query = q or ""
    search_type = type

    if search_type in ["all", "projects"]:
        # Search projects
        all_projects = db.get_all_projects()
        for project_id, project in all_projects.items():
            # Skip projects that don't match the search query
            if query and query.lower() not in project["name"].lower() and query.lower() not in project.get("description", "").lower():
                continue
            
            # Format project for display
            prompt_count = len(project.get("prompts", {}))
            created_at = format_date(project.get("created_at"))
            updated_at = format_date(project.get("updated_at"))
            created_by = db.get_username(project.get("created_by"))
            
            projects.append({
                "id": project_id,
                "name": project["name"],
                "description": project.get("description", ""),
                "prompt_count": prompt_count,
                "created_at": created_at,
                "updated_at": updated_at,
                "created_by": created_by
            })
    
    if search_type in ["all", "prompts"]:
        # Search prompts
        all_projects = db.get_all_projects()
        for project_id, project in all_projects.items():
            project_name = project["name"]
            for prompt_id, prompt in project.get("prompts", {}).items():
                # Skip prompts that don't match the search query
                if query and query.lower() not in prompt["name"].lower() and \
                   query.lower() not in prompt.get("system_prompt", "").lower() and \
                   query.lower() not in prompt.get("user_prompt", "").lower():
                    continue
                
                # Format prompt for display
                variables = extract_variables(prompt.get("system_prompt", "") + prompt.get("user_prompt", ""))
                created_at = format_date(prompt.get("created_at"))
                updated_at = format_date(prompt.get("updated_at"))
                created_by = db.get_username(prompt.get("created_by"))
                
                prompts.append({
                    "id": prompt_id,
                    "name": prompt["name"],
                    "project_id": project_id,
                    "project_name": project_name,
                    "variables": variables,
                    "created_at": created_at,
                    "updated_at": updated_at,
                    "created_by": created_by
                })
    
    return templates.TemplateResponse(
        "search_results.html",
        {
            "request": request,
            "query": query,
            "search_type": search_type,
            "projects": projects,
            "prompts": prompts
        }
    ) 