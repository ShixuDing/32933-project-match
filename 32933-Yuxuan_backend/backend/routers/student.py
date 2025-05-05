from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from schemas.supervisor import ProjectCreate  
from crud.project import create_project
from dependencies import get_db
from dependencies.auth import get_current_user

router = APIRouter(
    prefix="/student",
    tags=["Student Projects"]
)

@router.post("/projects/create")
def create_project_for_student(
    project_data: ProjectCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):

    new_project = create_project(db=db, creator_id=current_user["id"], project_data=project_data)
    return new_project
