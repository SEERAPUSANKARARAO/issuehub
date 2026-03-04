from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional, List

from app.database import get_db
from app.models.issue import Issue
from app.models.project_member import ProjectMember
from app.models.user import User
from app.schemas.issue import IssueCreate, IssueUpdate, IssueResponse
from app.core.dependencies import get_current_user
from app.core.permissions import get_project_role

router = APIRouter()


# -----------------------------
# Create Issue
# -----------------------------
@router.post("/project/{project_id}", response_model=IssueResponse)
def create_issue(
    project_id: int,
    data: IssueCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    membership = db.query(ProjectMember).filter(
        ProjectMember.project_id == project_id,
        ProjectMember.user_id == current_user.id,
    ).first()

    if not membership:
        raise HTTPException(status_code=403, detail="Not a project member")

    issue = Issue(
        project_id=project_id,
        title=data.title,
        description=data.description,
        priority=data.priority,
        reporter_id=current_user.id,
    )

    db.add(issue)
    db.commit()
    db.refresh(issue)

    return issue


# -----------------------------
# List Issues By Project
# -----------------------------
@router.get("/project/{project_id}", response_model=List[IssueResponse])
def list_issues(
    project_id: int,
    status: Optional[str] = None,
    priority: Optional[str] = None,
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    membership = db.query(ProjectMember).filter(
        ProjectMember.project_id == project_id,
        ProjectMember.user_id == current_user.id,
    ).first()

    if not membership:
        raise HTTPException(status_code=403)

    query = db.query(Issue).filter(Issue.project_id == project_id)

    if status:
        query = query.filter(Issue.status == status)

    if priority:
        query = query.filter(Issue.priority == priority)

    return query.offset(skip).limit(limit).all()


# -----------------------------
# 🔥 Get Single Issue (NEW)
# -----------------------------
@router.get("/{issue_id}", response_model=IssueResponse)
def get_issue(
    issue_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    issue = db.query(Issue).filter(Issue.id == issue_id).first()

    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found")

    # Check membership
    membership = db.query(ProjectMember).filter(
        ProjectMember.project_id == issue.project_id,
        ProjectMember.user_id == current_user.id,
    ).first()

    if not membership:
        raise HTTPException(status_code=403, detail="Not authorized")

    return issue


# -----------------------------
# Update Issue
# -----------------------------
@router.patch("/{issue_id}", response_model=IssueResponse)
def update_issue(
    issue_id: int,
    data: IssueUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    issue = db.query(Issue).filter(Issue.id == issue_id).first()

    if not issue:
        raise HTTPException(status_code=404)

    role = get_project_role(db, issue.project_id, current_user.id)

    if role != "maintainer" and issue.reporter_id != current_user.id:
        raise HTTPException(status_code=403)

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(issue, field, value)

    db.commit()
    db.refresh(issue)

    return issue


# -----------------------------
# Delete Issue
# -----------------------------
@router.delete("/{issue_id}")
def delete_issue(
    issue_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    issue = db.query(Issue).filter(Issue.id == issue_id).first()

    if not issue:
        raise HTTPException(status_code=404)

    role = get_project_role(db, issue.project_id, current_user.id)

    if role != "maintainer" and issue.reporter_id != current_user.id:
        raise HTTPException(status_code=403)

    db.delete(issue)
    db.commit()

    return {"message": "Issue deleted"}