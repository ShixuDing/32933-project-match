from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ProjectBase(BaseModel):
    title: str
    description: Optional[str] = None
    research_field: Optional[str] = None
    group_or_individual: Optional[str] = None
    project_start_time: Optional[datetime] = None
    project_end_time: Optional[datetime] = None
    project_grade: Optional[str] = None
    status: Optional[str] = None

class ProjectCreate(ProjectBase):
    pass

class ProjectUpdate(ProjectBase):
    pass

class ProjectOut(ProjectBase):
    id: int
    supervisor_id: int

    class Config:
        orm_mode = True

class ProjectStatusUpdate(BaseModel):
    status: str  # "Approved" or "Rejected"
