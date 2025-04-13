"""
Test utilities for the template service.
"""
import pytest
from pathlib import Path
from typing import Dict, Any
from jinja2 import TemplateSyntaxError as Jinja2TemplateSyntaxError
from app.services.template import (
    render_template,
    render_text_template,
    TemplateNotFoundError,
    TemplateSyntaxError,
    TemplateContextError,
    TemplateRenderError,
    TemplateSecurityError
)

@pytest.fixture
def sample_template_context() -> Dict[str, Any]:
    """Fixture for creating a sample template context."""
    return {
        "recipient_name": "Test User",
        "subject": "Test Email",
        "message": "This is a test message",
        "action_url": "https://example.com/action",
        "additional_details": "Some additional information"
    }

@pytest.fixture
def invitation_context() -> Dict[str, Any]:
    """Fixture for creating an invitation template context."""
    return {
        "recipient_name": "Test User",
        "inviter_name": "Admin User",
        "account_type": "user",
        "personal_message": "Welcome to our platform!",
        "invitation_url": "https://example.com/invite",
        "expiry_date": "2024-12-31"
    }

@pytest.fixture
def password_reset_context() -> Dict[str, Any]:
    """Fixture for creating a password reset template context."""
    return {
        "recipient_name": "Test User",
        "reset_url": "https://example.com/reset"
    }

@pytest.fixture
def notification_context() -> Dict[str, Any]:
    """Fixture for creating a notification template context."""
    return {
        "recipient_name": "Test User",
        "notification_title": "Test Notification",
        "notification_message": "This is a test notification",
        "action_url": "https://example.com/action",
        "additional_details": "Some additional information"
    }

def test_render_template(sample_template_context: Dict[str, Any]):
    """Test rendering a template."""
    result = render_template("test_template.html", **sample_template_context)
    assert isinstance(result, str)
    assert sample_template_context["recipient_name"] in result
    assert sample_template_context["message"] in result

def test_render_template_not_found():
    """Test handling of non-existent template."""
    with pytest.raises(TemplateNotFoundError) as exc_info:
        render_template("non_existent_template.html")
    assert "Template 'non_existent_template.html' not found" in str(exc_info.value)
    assert exc_info.value.template_name == "non_existent_template.html"

def test_render_template_syntax_error():
    """Test handling of template syntax error."""
    # Create a template with syntax error
    template_path = Path(__file__).parent.parent / "templates" / "syntax_error.html"
    template_path.write_text("{% if condition %}\n{{ variable }\n{% endif %}")
    
    with pytest.raises(TemplateSyntaxError) as exc_info:
        render_template("syntax_error.html")
    assert "Syntax error in template 'syntax_error.html'" in str(exc_info.value)
    assert exc_info.value.template_name == "syntax_error.html"
    
    # Clean up
    template_path.unlink()

def test_render_template_context_error():
    """Test handling of missing required variables."""
    # Create a template that requires a variable
    template_path = Path(__file__).parent.parent / "templates" / "requires_variable.html"
    template_path.write_text("{{ required_variable }}")
    
    with pytest.raises(TemplateContextError) as exc_info:
        render_template("requires_variable.html")
    assert "Missing required variables in template 'requires_variable.html'" in str(exc_info.value)
    assert exc_info.value.template_name == "requires_variable.html"
    
    # Clean up
    template_path.unlink()

def test_render_template_security_error():
    """Test handling of security-related errors."""
    # Create a template with potentially dangerous content
    template_path = Path(__file__).parent.parent / "templates" / "dangerous.html"
    template_path.write_text("{{ config.__class__.__init__.__globals__ }}")
    
    with pytest.raises(TemplateSecurityError) as exc_info:
        render_template("dangerous.html")
    assert "Security error in template 'dangerous.html'" in str(exc_info.value)
    assert exc_info.value.template_name == "dangerous.html"
    
    # Clean up
    template_path.unlink()

def test_render_text_template_invitation(invitation_context: Dict[str, Any]):
    """Test rendering an invitation text template."""
    result = render_text_template("invitation.html", **invitation_context)
    assert isinstance(result, str)
    assert invitation_context["recipient_name"] in result
    assert invitation_context["invitation_url"] in result

def test_render_text_template_password_reset(password_reset_context: Dict[str, Any]):
    """Test rendering a password reset text template."""
    result = render_text_template("password_reset.html", **password_reset_context)
    assert isinstance(result, str)
    assert password_reset_context["recipient_name"] in result
    assert password_reset_context["reset_url"] in result

def test_render_text_template_notification(notification_context: Dict[str, Any]):
    """Test rendering a notification text template."""
    result = render_text_template("notification.html", **notification_context)
    assert isinstance(result, str)
    assert notification_context["recipient_name"] in result
    assert notification_context["notification_message"] in result

def test_render_text_template_generic(sample_template_context: Dict[str, Any]):
    """Test rendering a generic text template."""
    result = render_text_template("generic.html", **sample_template_context)
    assert isinstance(result, str)
    assert sample_template_context["recipient_name"] in result
    assert sample_template_context["message"] in result

def test_template_type_detection():
    """Test template type detection."""
    from app.services.template import _get_template_type
    
    assert _get_template_type("invitation.html") == "invitation"
    assert _get_template_type("password_reset.html") == "password_reset"
    assert _get_template_type("notification.html") == "notification"
    assert _get_template_type("other.html") == "generic" 