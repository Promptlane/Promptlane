"""
Development tools for PromptLane.

This module contains endpoints that are only available in development mode.
"""

import os
from typing import Dict, Any, Optional
from fastapi import APIRouter, Request, Response, Depends, HTTPException, status
from fastapi.responses import HTMLResponse, PlainTextResponse
from pydantic import BaseModel

# Only import these in development mode
import importlib
if os.getenv("ENVIRONMENT", "development").lower() != "production":
    from app.services.template import render_template, render_text_template

# Create router (only available in development mode)
dev_router = APIRouter(prefix="/dev", tags=["Development"])

class EmailPreviewRequest(BaseModel):
    """Request body for email preview."""
    template_name: str
    context: Dict[str, Any]
    format: str = "html"  # html or text

@dev_router.post("/preview-email")
async def preview_email(
    preview_request: EmailPreviewRequest
) -> Response:
    """
    Preview an email template with the given context.
    This endpoint is only available in development mode.
    
    Args:
        preview_request: Request body containing template name, context and format
        
    Returns:
        The rendered template as HTML or plain text
    """
    # Check if we're in production mode
    if os.getenv("ENVIRONMENT", "development").lower() == "production":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="This endpoint is only available in development mode"
        )
    
    try:
        # Validate template name to prevent path traversal
        if not preview_request.template_name.startswith("email/") or ".." in preview_request.template_name:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid template name. Must start with 'email/' and not contain '..'"
            )
        
        # Choose format (HTML or text)
        if preview_request.format.lower() == "text":
            content = render_text_template(preview_request.template_name, **preview_request.context)
            return PlainTextResponse(content)
        else:
            content = render_template(preview_request.template_name, **preview_request.context)
            return HTMLResponse(content)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to render template: {str(e)}"
        )

@dev_router.get("/email-templates")
async def list_email_templates() -> Dict[str, Any]:
    """
    List all available email templates.
    This endpoint is only available in development mode.
    
    Returns:
        Dictionary with template information
    """
    # Check if we're in production mode
    if os.getenv("ENVIRONMENT", "development").lower() == "production":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="This endpoint is only available in development mode"
        )
    
    try:
        # Get the templates directory
        from pathlib import Path
        templates_path = Path(__file__).parent.parent / "templates" / "email"
        
        # List HTML templates
        html_templates = list(templates_path.glob("*.html"))
        
        # List text templates
        text_templates = list(templates_path.glob("*.txt"))
        
        # Create example templates with context
        examples = {
            "email/invitation.html": {
                "recipient_name": "John Doe",
                "inviter_name": "Admin User",
                "account_type": "standard user",
                "invitation_url": "https://example.com/invite/abc123",
                "expiry_date": "January 1, 2023 at 12:00 PM UTC",
                "personal_message": "We'd love to have you join our team!"
            },
            "email/password_reset.html": {
                "recipient_name": "John Doe",
                "reset_url": "https://example.com/reset/abc123"
            },
            "email/notification.html": {
                "recipient_name": "John Doe",
                "notification_title": "New Comment",
                "notification_message": "Someone commented on your prompt.",
                "action_url": "https://example.com/prompts/123",
                "action_text": "View Comment",
                "additional_details": "Comment by: Jane Smith"
            }
        }
        
        return {
            "html_templates": [t.name for t in html_templates],
            "text_templates": [t.name for t in text_templates],
            "examples": examples
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list templates: {str(e)}"
        ) 