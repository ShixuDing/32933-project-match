from sqlalchemy import Column, Integer, ForeignKey, String
from sqlalchemy.orm import relationship
from database import Base

class StudentGroup(Base):
    __tablename__ = "student_groups"

    id = Column(Integer, primary_key=True, index=True)
    group_name = Column(String(100), unique=True)
    supervisor_id = Column(Integer, ForeignKey("supervisors.id"))
    # group should have a project ID
    # group should have a project ID
    # group should have a project ID
    supervisor = relationship("Supervisor", back_populates="student_groups")