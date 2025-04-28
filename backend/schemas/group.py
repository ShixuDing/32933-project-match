from pydantic import BaseModel
from typing import List, Optional

class GroupCreate(BaseModel):
    group_name: str

class GroupJoin(BaseModel):
    group_id: int

class GroupApplyProject(BaseModel):
    project_id: int
