# models/project.py
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from database import Base


class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(100))
    description = Column(String(100))
    research_field = Column(String(100))
    group_or_individual = Column(String(100))
    project_start_time = Column(DateTime)
    project_end_time = Column(DateTime)
    project_grade = Column(String(10), default="")
    status = Column(String(20), default="Pending")

    supervisor_id = Column(Integer, ForeignKey("supervisors.id"))
    supervisor = relationship("Supervisor", back_populates="projects")

    applied_groups = relationship("Group", back_populates="project")
