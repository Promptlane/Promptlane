"""
Template rendering service for Promptlane.

This module provides template rendering functionality for email content,
with support for both HTML and text templates. It uses Jinja2 as the
templating engine and includes helper functions for common email templates.
"""

import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, Union
from jinja2 import Environment, FileSystemLoader, select_autoescape, TemplateNotFound, TemplateError, TemplateSyntaxError

from ..config import get_template_config, validate_template_variables

logger = logging.getLogger(__name__)

class TemplateError(Exception):
    """Base exception for template-related errors."""
    def __init__(self, message: str, template_name: Optional[str] = None, context: Optional[Dict[str, Any]] = None):
        self.message = message
        self.template_name = template_name
        self.context = context
        super().__init__(self.message)

class TemplateNotFoundError(TemplateError):
    """Raised when a template file cannot be found."""
    def __init__(self, template_name: str, search_paths: Optional[list[str]] = None):
        message = f"Template '{template_name}' not found"
        if search_paths:
            message += f" in paths: {', '.join(search_paths)}"
        super().__init__(message, template_name=template_name)

class TemplateSyntaxError(TemplateError):
    """Raised when there's a syntax error in the template."""
    def __init__(self, template_name: str, line_number: int, message: str):
        super().__init__(
            f"Syntax error in template '{template_name}' at line {line_number}: {message}",
            template_name=template_name
        )

class TemplateContextError(TemplateError):
    """Raised when there's an error with the template context."""
    def __init__(self, template_name: str, missing_variables: list[str]):
        super().__init__(
            f"Missing required variables in template '{template_name}': {', '.join(missing_variables)}",
            template_name=template_name
        )

class TemplateRenderError(TemplateError):
    """Raised when there's an error rendering a template."""
    def __init__(self, template_name: str, error: str, context: Optional[Dict[str, Any]] = None):
        super().__init__(
            f"Error rendering template '{template_name}': {error}",
            template_name=template_name,
            context=context
        )

class TemplateSecurityError(TemplateError):
    """Raised when there's a security-related error in template rendering."""
    def __init__(self, template_name: str, message: str):
        super().__init__(
            f"Security error in template '{template_name}': {message}",
            template_name=template_name
        )

# Set up Jinja2 environment for email templates
templates_path = Path(__file__).parent.parent / "templates"
env = Environment(
    loader=FileSystemLoader(templates_path),
    autoescape=select_autoescape(['html', 'xml']),
    trim_blocks=True,
    lstrip_blocks=True
)

def render_template(template_name: str, **context) -> str:
    """
    Render a template with the given context.
    
    Args:
        template_name: Name of the template (e.g., 'invitation', 'password_reset')
        **context: Variables to pass to the template
        
    Returns:
        str: Rendered template as a string
        
    Raises:
        TemplateNotFoundError: If the template file cannot be found
        TemplateSyntaxError: If there's a syntax error in the template
        TemplateContextError: If required variables are missing
        TemplateRenderError: If there's an error rendering the template
        TemplateSecurityError: If there's a security-related error
    """
    try:
        # Get template configuration
        config = get_template_config(template_name)
        
        # Validate and prepare context
        validate_template_variables(template_name, context)
        
        # Add current year to context for copyright notices
        if 'current_year' not in context:
            context['current_year'] = datetime.utcnow().year
            
        # Render template
        template = env.get_template(config.html_path)
        return template.render(**context)
    except TemplateNotFound as e:
        search_paths = [str(path) for path in env.loader.searchpath]
        raise TemplateNotFoundError(template_name, search_paths) from e
    except TemplateSyntaxError as e:
        raise TemplateSyntaxError(template_name, e.lineno, str(e)) from e
    except TemplateError as e:
        raise TemplateRenderError(template_name, str(e), context) from e
    except Exception as e:
        logger.error(f"Unexpected error rendering template {template_name}: {str(e)}")
        raise TemplateRenderError(template_name, f"Unexpected error: {str(e)}", context) from e

def render_text_template(template_name: str, **context) -> str:
    """
    Render a text version of an email template.
    
    This function first tries to find a corresponding .txt template.
    If not found, it falls back to the HTML template with text conversion.
    
    Args:
        template_name: Name of the template (e.g., 'invitation', 'password_reset')
        **context: Variables to pass to the template
        
    Returns:
        str: Rendered text template as a string
        
    Raises:
        TemplateNotFoundError: If neither the text template nor HTML template can be found
        TemplateSyntaxError: If there's a syntax error in the template
        TemplateContextError: If required variables are missing
        TemplateRenderError: If there's an error rendering the template
        TemplateSecurityError: If there's a security-related error
    """
    try:
        # Get template configuration
        config = get_template_config(template_name)
        
        # Validate and prepare context
        validate_template_variables(template_name, context)
        
        # Add current year to context for copyright notices
        if 'current_year' not in context:
            context['current_year'] = datetime.utcnow().year
            
        # Try to use text template if available
        if config.text_path and env.loader.exists(env.loader.join_path(config.text_path)):
            template = env.get_template(config.text_path)
            return template.render(**context)
        
        # Fall back to HTML template with text conversion
        template = env.get_template(config.html_path)
        html_content = template.render(**context)
        
        # Convert HTML to text (you might want to use a proper HTML-to-text converter)
        # This is a simple implementation - consider using a library like html2text
        text_content = html_content.replace('<br>', '\n').replace('<br/>', '\n')
        text_content = text_content.replace('<p>', '\n\n').replace('</p>', '\n\n')
        text_content = text_content.replace('<h1>', '\n\n# ').replace('</h1>', '\n\n')
        text_content = text_content.replace('<h2>', '\n\n## ').replace('</h2>', '\n\n')
        text_content = text_content.replace('<h3>', '\n\n### ').replace('</h3>', '\n\n')
        text_content = text_content.replace('<ul>', '\n').replace('</ul>', '\n')
        text_content = text_content.replace('<li>', '- ').replace('</li>', '\n')
        text_content = text_content.replace('<a href="', '').replace('">', ': ').replace('</a>', '')
        
        # Remove HTML tags
        import re
        text_content = re.sub(r'<[^>]+>', '', text_content)
        
        # Clean up whitespace
        text_content = re.sub(r'\n\s*\n', '\n\n', text_content)
        text_content = text_content.strip()
        
        return text_content
    except TemplateNotFound as e:
        search_paths = [str(path) for path in env.loader.searchpath]
        raise TemplateNotFoundError(template_name, search_paths) from e
    except TemplateSyntaxError as e:
        raise TemplateSyntaxError(template_name, e.lineno, str(e)) from e
    except TemplateContextError as e:
        raise TemplateContextError(template_name, e.missing_variables) from e
    except TemplateError as e:
        raise TemplateRenderError(template_name, str(e), context) from e
    except Exception as e:
        logger.error(f"Unexpected error rendering text template {template_name}: {str(e)}")
        raise TemplateRenderError(template_name, f"Unexpected error: {str(e)}", context) from e 