from sqlalchemy.orm import Session
from models.supervisor import Supervisor
from models.project import Project
from schemas.supervisor import ProjectCreate, SupervisorUpdate, ProjectUpdate
from models.group import Group


def create_project(db: Session, creator_id: int, project_data: ProjectCreate):
    """
    """
    new_project = Project(
        title=project_data.title,
        description=project_data.description,
        research_field=project_data.research_field,
        group_or_individual=project_data.group_or_individual.lower(),
        project_start_time=project_data.project_start_time,
        project_end_time=project_data.project_end_time,
        supervisor_id=creator_id  
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

def assign_group_to_supervisor(db: Session, supervisor_id: int, group_id: int):
    supervisor = db.query(Supervisor).filter(Supervisor.id == supervisor_id).first()
    group = db.query(Group).filter(Group.id == group_id).first()

    if not supervisor or not group:
        raise ValueError("Supervisor or Group not found.")

    # 
    managed_groups_count = db.query(Group).filter(Group.supervisor_id == supervisor_id).count()

    if managed_groups_count >= supervisor.quota:
        raise ValueError("Supervisor quota exceeded.")

    #
    group.supervisor_id = supervisor_id
    db.commit()
    return group

def remove_group_from_supervisor(db: Session, group_id: int):
    group = db.query(Group).filter(Group.id == group_id).first()
    if not group:
        raise ValueError("Group not found.")

    group.supervisor_id = None
    db.commit()
    return group