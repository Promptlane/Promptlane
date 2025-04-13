"""
AWS SES email provider implementation
"""
from typing import Dict, Any
import boto3
from botocore.exceptions import ClientError, NoCredentialsError, EndpointConnectionError

from ..exceptions import (
    EmailConfigurationError,
    EmailAuthenticationError,
    EmailConnectionError,
    EmailSendError,
    EmailQuotaError
)
from .base import BaseEmailProvider, EmailMessage

class AWSSESProvider(BaseEmailProvider):
    """AWS SES email provider implementation"""
    
    def __init__(self, config: Dict[str, Any]):
        try:
            self.region = config.get("region", "us-east-1")
            self.access_key = config.get("access_key")
            if not self.access_key:
                raise EmailConfigurationError("AWS access key not configured")
            
            self.secret_key = config.get("secret_key")
            if not self.secret_key:
                raise EmailConfigurationError("AWS secret key not configured")
            
            self.default_sender = config.get("default_sender")
            if not self.default_sender:
                raise EmailConfigurationError("AWS SES default sender not configured")
            
            self.client = boto3.client(
                "ses",
                region_name=self.region,
                aws_access_key_id=self.access_key,
                aws_secret_access_key=self.secret_key
            )
        except Exception as e:
            raise EmailConfigurationError(f"Invalid AWS SES configuration: {str(e)}")
    
    async def send_email(self, message: EmailMessage) -> bool:
        """Send email using AWS SES"""
        try:
            response = self.client.send_email(
                Source=message.sender or self.default_sender,
                Destination={
                    "ToAddresses": [message.recipient],
                    "CcAddresses": [message.cc] if message.cc else [],
                    "BccAddresses": [message.bcc] if message.bcc else []
                },
                Message={
                    "Subject": {
                        "Data": message.subject,
                        "Charset": "UTF-8"
                    },
                    "Body": {
                        "Text": {
                            "Data": message.text_content,
                            "Charset": "UTF-8"
                        },
                        "Html": {
                            "Data": message.html_content,
                            "Charset": "UTF-8"
                        }
                    }
                },
                ReplyToAddresses=[message.reply_to] if message.reply_to else []
            )
            return True
        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            if error_code == "InvalidClientTokenId":
                raise EmailAuthenticationError("aws_ses", "Invalid AWS credentials")
            elif error_code == "MessageRejected":
                raise EmailSendError("aws_ses", message.recipient, "Message rejected by AWS SES")
            elif error_code == "QuotaExceeded":
                raise EmailQuotaError("aws_ses", "Sending quota exceeded")
            else:
                raise EmailSendError("aws_ses", message.recipient, str(e))
        except NoCredentialsError:
            raise EmailAuthenticationError("aws_ses", "AWS credentials not found")
        except EndpointConnectionError:
            raise EmailConnectionError("aws_ses", "Could not connect to AWS SES endpoint")
        except Exception as e:
            raise EmailSendError("aws_ses", message.recipient, f"Unexpected error: {str(e)}")
    
    async def validate_credentials(self) -> bool:
        """Validate AWS SES credentials"""
        try:
            self.client.get_send_quota()
            return True
        except ClientError as e:
            if e.response["Error"]["Code"] == "InvalidClientTokenId":
                raise EmailAuthenticationError("aws_ses", "Invalid AWS credentials")
            raise EmailConnectionError("aws_ses", f"Could not validate credentials: {str(e)}")
        except NoCredentialsError:
            raise EmailAuthenticationError("aws_ses", "AWS credentials not found")
        except Exception as e:
            raise EmailConnectionError("aws_ses", f"Unexpected error: {str(e)}")
    
    async def get_quota(self) -> Dict[str, Any]:
        """Get AWS SES quota information"""
        try:
            quota = self.client.get_send_quota()
            return {
                "provider": "aws_ses",
                "max_24_hour_send": quota["Max24HourSend"],
                "max_send_rate": quota["MaxSendRate"],
                "sent_last_24_hours": quota["SentLast24Hours"]
            }
        except ClientError as e:
            if e.response["Error"]["Code"] == "QuotaExceeded":
                raise EmailQuotaError("aws_ses", "Quota exceeded")
            raise EmailQuotaError("aws_ses", f"Failed to get quota information: {str(e)}")
        except Exception as e:
            raise EmailQuotaError("aws_ses", f"Unexpected error getting quota: {str(e)}") 