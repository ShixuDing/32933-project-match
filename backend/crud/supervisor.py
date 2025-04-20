from sqlalchemy.orm import Session
from models.supervisor import Supervisor
from models.project import Project
from schemas.supervisor import ProjectCreate, SupervisorUpdate, ProjectUpdate


def create_project_for_supervisor(db: Session, supervisor_id: int, project_data: ProjectCreate):
    supervisor = db.query(Supervisor).filter(Supervisor.id == supervisor_id).first()
    if not supervisor:
        return None

    new_project = Project(
        title=project_data.title,
        description=project_data.description,
        research_field=project_data.research_field,
        group_or_individual=project_data.group_or_individual,
        project_start_time=project_data.project_start_time,
        project_end_time=project_data.project_end_time,
        supervisor_id=supervisor.id
    )
    db.add(new_project)
    db.commit()
    db.refresh(new_project)
    return new_project

def update_project_for_supervisor(db: Session, supervisor_id: int, project_id: int, update_data: ProjectUpdate):
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.supervisor_id == supervisor_id
    ).first()

    if not project:
        return None

    for field, value in update_data.dict(exclude_unset=True).items():
        setattr(project, field, value)

    db.commit()
    db.refresh(project)
    return project

def delete_project_for_supervisor(db: Session, supervisor_id: int, project_id: int):
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.supervisor_id == supervisor_id
    ).first()

    if not project:
        return False 

    db.delete(project)
    db.commit()
    return True

def update_supervisor_info(db: Session, supervisor_id: int, data: SupervisorUpdate):
    supervisor = db.query(Supervisor).filter(Supervisor.id == supervisor_id).first()
    if not supervisor:
        return None

    for key, value in data.dict(exclude_unset=True).items():
        setattr(supervisor, key, value)

    db.commit()
    db.refresh(supervisor)
    return supervisor
