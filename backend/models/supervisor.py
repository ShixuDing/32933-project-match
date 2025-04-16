from models.user_base import UserBase
from sqlalchemy import Column, String, Integer
from sqlalchemy.orm import relationship
from models.project import Project

class Supervisor(UserBase):
    __tablename__ = "supervisors"

    expertise = Column(String(100))
    faculty = Column(String(100))
    quota = Column(Integer)
    student_project_list = Column(String(100))

    projects = relationship("Project", back_populates="supervisor")


    def create_project(self):
        pass

    def remove_or_end_project(self):
        pass

    def grade_project(self):
        pass
