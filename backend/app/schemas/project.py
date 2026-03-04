from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ProjectCreate(BaseModel):
    name: str
    key: str
    description: Optional[str] = None


class ProjectResponse(BaseModel):
    id: int
    name: str
    key: str
    description: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True