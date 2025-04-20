from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from schemas.user import UserCommon

class ProjectCreate(BaseModel):
    title: str
    description: str
    research_field: str
    group_or_individual: str
    project_start_time: datetime
    project_end_time: datetime

class ProjectOut(BaseModel):
    id: int
    title: str

    class Config:
        orm_mode = True

class SupervisorOut(UserCommon):
    faculty: Optional[str]
    expertise: Optional[str]
    quota: Optional[int]

class ProjectUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    research_field: Optional[str] = None
    group_or_individual: Optional[str] = None
    project_start_time: Optional[datetime] = None
    project_end_time: Optional[datetime] = None
    project_grade: Optional[str] = None

class SupervisorUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    expertise: Optional[str] = None
    faculty: Optional[str] = None
    quota: Optional[int] = None