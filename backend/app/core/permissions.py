from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.models.project_member import ProjectMember

def get_project_role(db: Session, project_id: int, user_id: int):
    membership = db.query(ProjectMember).filter(
        ProjectMember.project_id == project_id,
        ProjectMember.user_id == user_id
    ).first()

    if not membership:
        raise HTTPException(status_code=403, detail="Not a project member")

    return membership.role

def require_maintainer(role: str):
    if role != "maintainer":
        raise HTTPException(status_code=403, detail="Maintainer access required")