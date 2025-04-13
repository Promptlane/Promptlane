from datetime import datetime, timedelta
from typing import Optional, Union

def format_date(date_obj: Union[datetime, str, None], format_str: str = "%b %d, %Y") -> str:
    """
    Format a date object or string as a human-readable string.
    
    Args:
        date_obj: A datetime object, ISO format string, or None
        format_str: The format string to use (default: "%b %d, %Y")
        
    Returns:
        A formatted date string, or empty string if date_obj is None
    """
    if date_obj is None:
        return ""
    
    if isinstance(date_obj, str):
        try:
            date_obj = datetime.fromisoformat(date_obj.replace('Z', '+00:00'))
        except ValueError:
            return date_obj  # Return the original string if parsing fails
    
    return date_obj.strftime(format_str)

def format_datetime(date_obj: Union[datetime, str, None], format_str: str = "%b %d, %Y %I:%M %p") -> str:
    """
    Format a datetime object or string as a human-readable string with time.
    
    Args:
        date_obj: A datetime object, ISO format string, or None
        format_str: The format string to use (default: "%b %d, %Y %I:%M %p")
        
    Returns:
        A formatted datetime string, or empty string if date_obj is None
    """
    return format_date(date_obj, format_str)

def format_relative_time(date_obj: Union[datetime, str, None]) -> str:
    """
    Format a datetime as a relative time string (e.g., "2 hours ago", "5 days ago").
    
    Args:
        date_obj: A datetime object, ISO format string, or None
        
    Returns:
        A relative time string, or empty string if date_obj is None
    """
    if date_obj is None:
        return ""
    
    if isinstance(date_obj, str):
        try:
            date_obj = datetime.fromisoformat(date_obj.replace('Z', '+00:00'))
        except ValueError:
            return date_obj
    
    now = datetime.utcnow()
    diff = now - date_obj
    
    seconds = diff.total_seconds()
    
    if seconds < 60:
        return "just now"
    elif seconds < 3600:
        minutes = int(seconds // 60)
        return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
    elif seconds < 86400:
        hours = int(seconds // 3600)
        return f"{hours} hour{'s' if hours != 1 else ''} ago"
    elif seconds < 604800:
        days = int(seconds // 86400)
        return f"{days} day{'s' if days != 1 else ''} ago"
    elif seconds < 2592000:
        weeks = int(seconds // 604800)
        return f"{weeks} week{'s' if weeks != 1 else ''} ago"
    else:
        return format_date(date_obj) 