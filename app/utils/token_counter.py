from typing import Dict, List
import tiktoken

def count_tokens(text: str) -> int:
    """Count the number of tokens in a text string using tiktoken.
    
    Args:
        text: The text to count tokens for
        
    Returns:
        Number of tokens in the text
    """
    if not text:
        return 0
        
    # Use the cl100k_base encoding which is used by GPT-4 and GPT-3.5-turbo
    encoding = tiktoken.get_encoding("cl100k_base")
    return len(encoding.encode(text))

def count_prompt_tokens(prompt: Dict) -> Dict[str, int]:
    """Count tokens for system and user prompts.
    
    Args:
        prompt: Dictionary containing system_prompt and user_prompt
        
    Returns:
        Dictionary with system_tokens and user_tokens counts
    """
    return {
        "system_tokens": count_tokens(prompt.get("system_prompt", "")),
        "user_tokens": count_tokens(prompt.get("user_prompt", ""))
    } 