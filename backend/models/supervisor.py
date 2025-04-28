from sqlalchemy import Column, Integer, String
from database import Base
from sqlalchemy.orm import relationship

class Supervisor(Base):
    __tablename__ = "supervisors"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String(50))
    last_name = Column(String(50))
    email = Column(String(100), unique=True, index=True)
    password = Column(String(100))
    user_group_identifier = Column(String(20), default="supervisor")

    quota = Column(Integer, default=3)  

    
    groups = relationship("Group", back_populates="supervisor")

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

    def approve_or_reject_project(self):
        pass
