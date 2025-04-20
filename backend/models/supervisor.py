from models.user_base import UserBase
from sqlalchemy import Column, String, Integer
from sqlalchemy.orm import relationship
from models.project import Project
from models.group import StudentGroup

class Supervisor(UserBase):
    __tablename__ = "supervisors"

    expertise = Column(String(100))
    faculty = Column(String(100))
    quota = Column(Integer)
    student_groups = relationship("StudentGroup", back_populates="supervisor", cascade="all, delete-orphan")

    projects = relationship("Project", back_populates="supervisor")


    def create_project(self):
        pass

    def remove_roject(self):
        pass

    def add_a_group(self):
        pass

    def score_project(self):
        pass

    def remove_agroup(self):
        pass
