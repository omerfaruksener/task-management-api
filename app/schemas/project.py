from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime

class ProjectCreate(BaseModel):
    name: str
    description: Optional[str] = None

class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None

class ProjectResponse(ProjectCreate):
    id: int
    owner_id:int
    created_at:datetime
    updated_at:datetime

    model_config = ConfigDict(from_attributes=True)