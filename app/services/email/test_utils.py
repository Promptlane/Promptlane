"""
Test utilities for the email service.
"""
import pytest
from typing import Dict, Any
from app.services.email.service import EmailService
from app.services.email.providers.base import EmailMessage

@pytest.fixture
def email_service():
    """Fixture for creating an email service instance."""
    return EmailService({
        "default_provider": "smtp",
        "dev_mode": True,
        "providers": {
            "smtp": {
                "host": "smtp.example.com",
                "port": 587,
                "username": "test@example.com",
                "password": "test_password",
                "use_tls": True,
                "default_sender": "test@example.com"
            }
        }
    })

@pytest.fixture
def sample_email_message():
    """Fixture for creating a sample email message."""
    return EmailMessage(
        recipient="test@example.com",
        subject="Test Email",
        html_content="<h1>Test HTML Content</h1>",
        text_content="Test Text Content"
    )

@pytest.fixture
def sample_template_context():
    """Fixture for creating a sample template context."""
    return {
        "subject": "Test Template Email",
        "recipient_name": "Test User",
        "message": "This is a test message",
        "action_url": "https://example.com/action",
        "additional_details": "Some additional information"
    }

@pytest.mark.asyncio
async def test_send_email(email_service, sample_email_message):
    """Test sending an email."""
    success = await email_service.send_email(
        recipient=sample_email_message.recipient,
        subject=sample_email_message.subject,
        html_content=sample_email_message.html_content,
        text_content=sample_email_message.text_content
    )
    assert success is True

@pytest.mark.asyncio
async def test_send_template_email(email_service, sample_template_context):
    """Test sending a template email."""
    success = await email_service.send_template_email(
        template_name="test_template",
        recipient="test@example.com",
        context=sample_template_context
    )
    assert success is True

@pytest.mark.asyncio
async def test_send_email_with_retry(email_service, sample_email_message):
    """Test sending an email with retry."""
    success = await email_service.send_email_with_retry(
        recipient=sample_email_message.recipient,
        subject=sample_email_message.subject,
        html_content=sample_email_message.html_content,
        text_content=sample_email_message.text_content,
        max_retries=3,
        delay=0.1
    )
    assert success is True

@pytest.mark.asyncio
async def test_validate_provider(email_service):
    """Test validating a provider."""
    valid = await email_service.validate_provider("smtp")
    assert valid is True

@pytest.mark.asyncio
async def test_get_provider_quota(email_service):
    """Test getting provider quota."""
    quota = await email_service.get_provider_quota("smtp")
    assert isinstance(quota, dict)
    assert "error" not in quota 