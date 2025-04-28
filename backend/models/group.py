from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.mysql import JSON  
from database import Base


class Group(Base):
    __tablename__ = "groups"

    id = Column(Integer, primary_key=True, index=True)
    group_name = Column(String(100), unique=True, nullable=False)
    member_ids = Column(JSON, nullable=False, default=[])
    project_id = Column(Integer, ForeignKey('projects.id'), nullable=True)

    # 
    supervisor_id = Column(Integer, ForeignKey('supervisors.id'), nullable=True)

    # 
    supervisor = relationship("Supervisor", back_populates="groups")
    members = relationship("Student", back_populates="group")
    project = relationship("Project", back_populates="applied_groups")
