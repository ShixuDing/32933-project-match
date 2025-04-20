from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from crud import supervisor as supervisor_crud
from crud.supervisor import update_project_for_supervisor, delete_project_for_supervisor, update_supervisor_info
from models.supervisor import Supervisor
from schemas.supervisor import ProjectCreate, ProjectOut, ProjectUpdate, SupervisorOut, SupervisorUpdate
from dependencies.auth import require_supervisor
from models.project import Project
from typing import List
from schemas.user import UserResponse

router = APIRouter(
    prefix="/supervisors",
    tags=["supervisors"]
)

@router.post("/{supervisor_id}/projects", response_model=ProjectOut)
def create_project(
    supervisor_id: int,
    project: ProjectCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_supervisor)  
):
    result = supervisor_crud.create_project_for_supervisor(db, supervisor_id, project)
    if not result:
        raise HTTPException(status_code=404, detail="Supervisor not found")
    return result

@router.put("/{supervisor_id}/projects/{project_id}", response_model=ProjectOut)
def update_project(
    supervisor_id: int,
    project_id: int,
    update_data: ProjectUpdate,
    db: Session = Depends(get_db),
    user=Depends(require_supervisor)
):
    if user["email"] is None or user["role"] != "supervisor":
        raise HTTPException(status_code=403, detail="Unauthorized")

    updated_project = update_project_for_supervisor(db, supervisor_id, project_id, update_data)
    if not updated_project:
        raise HTTPException(status_code=404, detail="Project not found or access denied")

    return updated_project

@router.get("/me/projects", response_model=List[ProjectOut])
def get_my_projects(
    db: Session = Depends(get_db),
    user=Depends(require_supervisor)
):
    return db.query(Project).filter(Project.supervisor_id == user["id"]).all()

@router.delete("/{supervisor_id}/projects/{project_id}", status_code=204)
def delete_project(
    supervisor_id: int,
    project_id: int,
    db: Session = Depends(get_db),
    user = Depends(require_supervisor)
):
    # supervisor itself deleting projects
    if user["id"] != supervisor_id:
        raise HTTPException(status_code=403, detail="You can only delete your own projects")

    success = delete_project_for_supervisor(db, supervisor_id, project_id)
    if not success:
        raise HTTPException(status_code=404, detail="Project not found")

    return  # 204 


@router.put("/me", response_model=UserResponse)  
def update_my_info(
    update_data: SupervisorUpdate,
    db: Session = Depends(get_db),
    user = Depends(require_supervisor)
):
    updated = update_supervisor_info(db, user["id"], update_data)
    if not updated:
        raise HTTPException(status_code=404, detail="Supervisor not found")

    return {
        "id": updated.id,
        "email": updated.email,
        "first_name": updated.first_name,
        "last_name": updated.last_name,
        "role": updated.user_group_identifier
    }

@router.get("/me", response_model=SupervisorOut)
def get_my_profile(
    db: Session = Depends(get_db),
    user = Depends(require_supervisor)
):
    return db.query(Supervisor).filter(Supervisor.id == user["id"]).first()
# @router.get("/me/project", response_model=ProjectOut)
# def get_my_project(
#     db: Session = Depends(get_db),
#     user=Depends(require_student)
# ):
#     # student find project by query
#     group = db.query(StudentGroup).filter(StudentGroup.student_email == user["email"]).first()
#     if not group:
#         raise HTTPException(status_code=404, detail="No group/project found")
    
#     project = db.query(Project).filter(Project.id == group.project_id).first()
#     return project
