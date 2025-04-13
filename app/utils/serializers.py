import json
import uuid
from datetime import datetime, date
from typing import Any, Dict, List, Union

class JSONEncoder(json.JSONEncoder):
    """
    Custom JSON encoder with support for:
    - UUID objects
    - datetime objects
    - date objects
    - custom objects with a to_dict method
    """
    def default(self, obj):
        if isinstance(obj, uuid.UUID):
            return str(obj)
        elif isinstance(obj, (datetime, date)):
            return obj.isoformat()
        elif hasattr(obj, 'to_dict') and callable(getattr(obj, 'to_dict')):
            return obj.to_dict()
        return json.JSONEncoder.default(self, obj)

def serialize_json(obj: Any) -> str:
    """
    Serialize an object to a JSON string with support for UUID and datetime objects.
    
    Args:
        obj: The object to serialize
        
    Returns:
        A JSON string
    """
    return json.dumps(obj, cls=JSONEncoder)

def deserialize_json(json_str: str) -> Any:
    """
    Deserialize a JSON string to a Python object.
    
    Args:
        json_str: The JSON string to deserialize
        
    Returns:
        The deserialized Python object
    """
    return json.loads(json_str)

def safe_json_dumps(obj: Any) -> Dict:
    """
    Convert an object to a JSON-safe dictionary by serializing and deserializing.
    This is useful for ensuring objects like UUIDs are properly converted to strings.
    
    Args:
        obj: The object to convert
        
    Returns:
        A JSON-safe dictionary
    """
    return json.loads(serialize_json(obj)) 