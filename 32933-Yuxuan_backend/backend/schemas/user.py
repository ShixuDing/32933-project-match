from pydantic import BaseModel, EmailStr, field_validator
import re
from typing import Optional

class UserCreate(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    password: str
    user_group_identifier: str

    @field_validator("email")
    @classmethod
    def validate_email_format(cls, v, values):
        first = values.data.get("first_name", "").lower()
        last = values.data.get("last_name", "").lower()
        base_pattern = rf"^{first}\.{last}(-\d+)?@(student\.)?uts\.edu\.au$"
        if not re.match(base_pattern, v.lower()):
            raise ValueError("Email must match: firstname.lastname@student.uts.edu.au or firstname.lastname@uts.edu.au")
        return v.lower()
    
    @field_validator('user_group_identifier')
    def validate_role(cls, v):
        allowed_roles = ['student', 'supervisor']
        if v not in allowed_roles:
            raise ValueError('Role must be "student" or "supervisor"')
        return v

class LoginRequest(BaseModel):
    email: str
    password: str

class RefreshTokenRequest(BaseModel):
    refresh_token: str

class UserResponse(BaseModel):
    id: int
    email: EmailStr
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    user_group_identifier: str

    class Config:
        orm_mode = True

class UserCommon(BaseModel):
    id: int
    email: EmailStr
    first_name: Optional[str]
    last_name: Optional[str]
    user_group_identifier: str

    class Config:
        orm_mode = True