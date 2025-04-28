from pydantic import BaseModel

class ProjectStatusUpdate(BaseModel):
    status: str  # "Approved" or "Rejected"