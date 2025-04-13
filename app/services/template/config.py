"""
Template configuration for email templates.
"""
from typing import Dict, Any, Optional
from dataclasses import dataclass
from pathlib import Path

@dataclass
class TemplateConfig:
    """Configuration for an email template."""
    name: str
    description: str
    html_path: str
    text_path: Optional[str] = None
    required_variables: Optional[list[str]] = None
    default_variables: Optional[Dict[str, Any]] = None

# Template configurations
TEMPLATE_CONFIGS: Dict[str, TemplateConfig] = {
    "invitation": TemplateConfig(
        name="invitation",
        description="Invitation email template",
        html_path="emails/invitation.html",
        text_path="emails/invitation.txt",
        required_variables=[
            "recipient_name",
            "inviter_name",
            "account_type",
            "invitation_url",
            "expiry_date"
        ],
        default_variables={
            "personal_message": ""
        }
    ),
    "password_reset": TemplateConfig(
        name="password_reset",
        description="Password reset email template",
        html_path="emails/password_reset.html",
        text_path="emails/password_reset.txt",
        required_variables=[
            "recipient_name",
            "reset_url"
        ]
    ),
    "notification": TemplateConfig(
        name="notification",
        description="Notification email template",
        html_path="emails/notification.html",
        text_path="emails/notification.txt",
        required_variables=[
            "recipient_name",
            "notification_title",
            "notification_message"
        ],
        default_variables={
            "action_url": None,
            "additional_details": None
        }
    )
}

def get_template_config(template_name: str) -> TemplateConfig:
    """Get template configuration by name."""
    if template_name not in TEMPLATE_CONFIGS:
        raise ValueError(f"Template configuration not found: {template_name}")
    return TEMPLATE_CONFIGS[template_name]

def validate_template_variables(template_name: str, context: Dict[str, Any]) -> None:
    """Validate template variables against configuration."""
    config = get_template_config(template_name)
    
    # Check required variables
    if config.required_variables:
        missing_vars = [var for var in config.required_variables if var not in context]
        if missing_vars:
            raise ValueError(f"Missing required variables for template {template_name}: {missing_vars}")
    
    # Add default variables if not present
    if config.default_variables:
        for var, default_value in config.default_variables.items():
            if var not in context:
                context[var] = default_value 