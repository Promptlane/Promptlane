from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
import uuid

class ProjectBase(BaseModel):
    name: str
    description: Optional[str] = None
    
class ProjectCreate(ProjectBase):
    key: Optional[str] = None  # If not provided, will be generated from name
    
class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    
class ProjectDB(ProjectBase):
    id: uuid.UUID
    key: str
    created_by: uuid.UUID
    updated_by: Optional[uuid.UUID] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    model_config = {
        "from_attributes": True
    }
        
class ProjectResponse(ProjectBase):
    id: str  # UUID as string for JSON compatibility
    key: str
    created_by: str  # UUID as string for JSON compatibility
    updated_by: Optional[str] = None  # UUID as string for JSON compatibility
    created_at: datetime
    updated_at: Optional[datetime] = None
    prompt_count: Optional[int] = 0
    
    model_config = {
        "from_attributes": True
    } 