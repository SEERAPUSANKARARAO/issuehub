from pydantic import BaseModel
from datetime import datetime


class CommentCreate(BaseModel):
    body: str


class CommentResponse(BaseModel):
    id: int
    issue_id: int
    author_id: int
    body: str
    created_at: datetime

    class Config:
        from_attributes = True