import re
import uuid
from typing import List, Dict, Any

def extract_variables(prompt_text: str) -> List[str]:
    """Extract variable names from a prompt template"""
    # Find all instances of {{variable_name}}
    matches = re.findall(r'{{(.*?)}}', prompt_text)
    
    # Return unique variable names
    result = []
    for match in matches:
        var_name = match.strip()
        if var_name and var_name not in result:
            result.append(var_name)
    
    return result

def apply_variables(template: str, variables: Dict[str, Any]) -> str:
    """Apply variables to a template string
    
    Args:
        template (str): The template string with {{variable}} placeholders
        variables (Dict[str, Any]): Dict of variable names and values
        
    Returns:
        str: The template with all variables replaced
    """
    result = template
    
    # Replace each variable
    for var_name, var_value in variables.items():
        # Create the placeholder pattern
        placeholder = "{{" + var_name + "}}"
        
        # Replace all occurrences
        result = result.replace(placeholder, str(var_value))
    
    return result

def generate_key_from_name(name: str) -> str:
    """Generate a URL-friendly key from a name"""
    # Convert to lowercase
    key = name.lower()
    
    # Replace spaces with underscores
    key = key.replace(" ", "_")
    
    # Remove special characters
    key = re.sub(r'[^a-z0-9_]', '', key)
    
    # Ensure it starts with a letter
    if key and not key[0].isalpha():
        key = f"p_{key}"
    
    # If empty after processing, use a generic key
    if not key:
        key = f"proj_{uuid.uuid4().hex[:8]}"
    
    return key

def generate_uuid_str() -> str:
    """Generate a new UUID as string"""
    return str(uuid.uuid4()) 