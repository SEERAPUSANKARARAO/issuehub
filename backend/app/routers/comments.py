from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.comment import Comment
from app.models.issue import Issue
from app.models.project_member import ProjectMember
from app.schemas.comment import CommentCreate, CommentResponse
from app.models.user import User
from app.core.dependencies import get_current_user

router = APIRouter()


@router.post("/issue/{issue_id}", response_model=CommentResponse)
def add_comment(
    issue_id: int,
    data: CommentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    issue = db.query(Issue).filter(Issue.id == issue_id).first()

    if not issue:
        raise HTTPException(status_code=404)

    membership = db.query(ProjectMember).filter(
        ProjectMember.project_id == issue.project_id,
        ProjectMember.user_id == current_user.id,
    ).first()

    if not membership:
        raise HTTPException(status_code=403)

    comment = Comment(
        issue_id=issue_id,
        author_id=current_user.id,
        body=data.body,
    )

    db.add(comment)
    db.commit()
    db.refresh(comment)

    return comment


@router.get("/issue/{issue_id}", response_model=List[CommentResponse])
def list_comments(
    issue_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    issue = db.query(Issue).filter(Issue.id == issue_id).first()

    if not issue:
        raise HTTPException(status_code=404)

    membership = db.query(ProjectMember).filter(
        ProjectMember.project_id == issue.project_id,
        ProjectMember.user_id == current_user.id,
    ).first()

    if not membership:
        raise HTTPException(status_code=403)

    return db.query(Comment).filter(Comment.issue_id == issue_id).all()