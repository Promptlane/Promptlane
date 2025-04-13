"""
Custom exceptions for email service
"""
class EmailError(Exception):
    """Base exception for all email-related errors"""
    pass

class EmailProviderError(EmailError):
    """Base exception for provider-specific errors"""
    def __init__(self, provider: str, message: str):
        super().__init__(f"Provider {provider}: {message}")
        self.provider = provider

class EmailConfigurationError(EmailError):
    """Exception for configuration-related errors"""
    pass

class EmailValidationError(EmailError):
    """Exception for email validation errors"""
    pass

class EmailQuotaError(EmailProviderError):
    """Exception for quota-related errors"""
    pass

class EmailAuthenticationError(EmailProviderError):
    """Exception for authentication-related errors"""
    pass

class EmailConnectionError(EmailProviderError):
    """Exception for connection-related errors"""
    pass

class EmailSendError(EmailProviderError):
    """Exception for email sending errors"""
    def __init__(self, provider: str, recipient: str, message: str):
        super().__init__(provider, f"Failed to send email to {recipient}: {message}")
        self.recipient = recipient 