"""
Shared utility functions for database operations
"""
import json
import uuid
from typing import Dict, Any

# Add custom JSON encoder for UUID objects
class UUIDEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, uuid.UUID):
            # Convert UUID to string
            return str(obj)
        # Let the base class handle other types or raise TypeError
        return json.JSONEncoder.default(self, obj)

def serialize_details(details: Dict[str, Any]) -> Dict[str, Any]:
    """
    Serialize a details dictionary to ensure it can be stored in JSON
    
    Args:
        details: Dictionary with details to serialize
        
    Returns:
        JSON-safe dictionary with UUID values converted to strings
    """
    if details:
        details_json = json.dumps(details, cls=UUIDEncoder)
        return json.loads(details_json)
    return details 