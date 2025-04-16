from pydantic import BaseModel, EmailStr, field_validator
import re

class UserCreate(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    password: str

    @field_validator("email")
    @classmethod
    def validate_email_format(cls, v, values):
        first = values.data.get("first_name", "").lower()
        last = values.data.get("last_name", "").lower()

        base_pattern = rf"^{first}\.{last}(-\d+)?@(student\.)?uts\.edu\.au$"
        if not re.match(base_pattern, v.lower()):
            raise ValueError("Email must match: firstname.lastname@student.uts.edu.au or firstname.lastname@uts.edu.au")
        return v.lower()
