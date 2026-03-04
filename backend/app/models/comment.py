from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.sql import func
from app.db.base import Base

class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)
    issue_id = Column(Integer, ForeignKey("issues.id", ondelete="CASCADE"))
    author_id = Column(Integer, ForeignKey("users.id"))
    body = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())