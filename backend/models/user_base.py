from sqlalchemy import Column, Integer, String
from database import Base

class UserBase(Base):
    __abstract__ = True  

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String(100))
    last_name = Column(String(100))
    email = Column(String(255), unique=True, index=True)
    password = Column(String(255))
    user_group_identifier = Column(String(20))

    def register(self): pass
    def login(self): pass
