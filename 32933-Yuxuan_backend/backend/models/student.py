from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from models.user_base import UserBase  

class Student(UserBase):
    __tablename__ = "students"

    major = Column(String(100))
    faculty = Column(String(100))
    group_id = Column(Integer, ForeignKey('groups.id'), nullable=True)

    group = relationship("Group", back_populates="members")
