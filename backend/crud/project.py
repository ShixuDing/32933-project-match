from sqlalchemy.orm import Session
from models.supervisor import Supervisor
from models.project import Project
from schemas.supervisor import ProjectCreate, SupervisorUpdate, ProjectUpdate

def update_project_status(db: Session, project_id: int, status: str):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise ValueError("Project not found.")

    project.status = status
    db.commit()
    db.refresh(project)
    return project
