"""
Template configuration and initialization
"""
from fastapi.templating import Jinja2Templates as BaseJinja2Templates
from app.config import settings
import os
from typing import Any, Dict

class Jinja2Templates(BaseJinja2Templates):
    """Custom Jinja2Templates class that always includes settings in the context"""
    
    def TemplateResponse(
        self, name: str, context: Dict[str, Any], *args: Any, **kwargs: Any
    ):
        """Override TemplateResponse to include settings in all templates"""
        # Always add settings to the context if not already present
        if "settings" not in context:
            context["settings"] = settings
        
        # Call the parent class's TemplateResponse
        return super().TemplateResponse(name, context, *args, **kwargs)

# Get the directory where this file is located
current_dir = os.path.dirname(os.path.abspath(__file__))
# Go up one level to get the app directory
app_dir = os.path.dirname(current_dir)
# Set the templates directory
templates_dir = os.path.join(app_dir, "templates")

# Initialize custom Jinja2Templates
templates = Jinja2Templates(directory=templates_dir) 