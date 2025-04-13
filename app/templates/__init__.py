"""
Template configuration and initialization
"""
from fastapi.templating import Jinja2Templates
import os

# Get the directory where this file is located
current_dir = os.path.dirname(os.path.abspath(__file__))
# Go up one level to get the app directory
app_dir = os.path.dirname(current_dir)
# Set the templates directory
templates_dir = os.path.join(app_dir, "templates")

# Initialize Jinja2Templates
templates = Jinja2Templates(directory=templates_dir) 