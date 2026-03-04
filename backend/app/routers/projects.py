from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.project import Project
from app.models.project_member import ProjectMember
from app.models.user import User
from app.schemas.project import ProjectCreate, ProjectResponse
from app.core.dependencies import get_current_user
from app.core.permissions import get_project_role, require_maintainer

router = APIRouter()


@router.post("/", response_model=ProjectResponse)
def create_project(
    data: ProjectCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if db.query(Project).filter(Project.key == data.key).first():
        raise HTTPException(status_code=400, detail="Project key already exists")

    project = Project(
        name=data.name,
        key=data.key,
        description=data.description,
    )

    db.add(project)
    db.commit()
    db.refresh(project)

    # Creator becomes maintainer
    member = ProjectMember(
        project_id=project.id,
        user_id=current_user.id,
        role="maintainer",
    )

    db.add(member)
    db.commit()

    return project


@router.get("/", response_model=List[ProjectResponse])
def list_projects(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    memberships = db.query(ProjectMember).filter(
        ProjectMember.user_id == current_user.id
    ).all()

    project_ids = [m.project_id for m in memberships]

    return db.query(Project).filter(Project.id.in_(project_ids)).all()


@router.post("/{project_id}/members")
def add_member(
    project_id: int,
    user_id: int,
    role: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    current_role = get_project_role(db, project_id, current_user.id)
    require_maintainer(current_role)

    db.add(ProjectMember(project_id=project_id, user_id=user_id, role=role))
    db.commit()

    return {"message": "Member added"}