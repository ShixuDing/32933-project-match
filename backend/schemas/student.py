from schemas.user import UserCommon
from typing import Optional

class StudentOut(UserCommon):
    group_id: Optional[int]  
    degree_type: Optional[str]