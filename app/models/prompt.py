from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Union
from datetime import datetime
import uuid

class PromptBase(BaseModel):
    name: str
    system_prompt: str
    user_prompt: str
    
class PromptCreate(PromptBase):
    pass

class PromptUpdate(PromptBase):
    pass

class PromptDB(PromptBase):
    id: uuid.UUID
    key: str
    version: int
    is_active: bool
    project_id: uuid.UUID
    created_by: uuid.UUID
    updated_by: Optional[uuid.UUID] = None
    parent_id: Optional[uuid.UUID] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    model_config = {
        "from_attributes": True
    }

class PromptVersionInfo(BaseModel):
    version: int
    name: str
    system_prompt: Optional[str] = None
    user_prompt: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    created_by: Optional[str] = None
    updated_by: Optional[str] = None
    is_active: bool = False

class PromptResponse(BaseModel):
    id: str
    project_id: str
    name: str
    system_prompt: Optional[str] = None
    user_prompt: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    created_by: Optional[str] = None
    updated_by: Optional[str] = None
    variables: List[str] = []
    version: int = 1
    is_active: bool = True
    versions: Optional[List[PromptVersionInfo]] = None
    
    model_config = {
        "from_attributes": True
    }
        
class PromptVersionResponse(BaseModel):
    id: str  # UUID as string for JSON compatibility
    key: str
    name: str
    version: int
    is_active: bool
    created_at: datetime
    
    model_config = {
        "from_attributes": True
    } 