from pydantic import BaseModel
from typing import Optional, Literal


class IssueCreate(BaseModel):
    title: str
    description: Optional[str] = None
    priority: Literal["low", "medium", "high", "critical"] = "medium"


class IssueUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[Literal["open", "in_progress", "resolved", "closed"]] = None
    priority: Optional[Literal["low", "medium", "high", "critical"]] = None
    assignee_id: Optional[int] = None


class IssueResponse(BaseModel):
    id: int
    project_id: int
    title: str
    description: Optional[str]
    status: str
    priority: str

    class Config:
        from_attributes = True