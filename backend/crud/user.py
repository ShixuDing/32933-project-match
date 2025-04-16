from sqlalchemy.orm import Session
from models.student import Student
from models.supervisor import Supervisor
from schemas.user import UserCreate
from models.user_base import UserBase

def generate_unique_email(db: Session, first: str, last: str, domain: str) -> str:
    base_prefix = f"{first}.{last}"
    suffix = f"@{domain}"
    email = base_prefix + suffix
    count = 1

    # 尝试查重（在 student 和 supervisor 两个表中查 email）
    while (
        db.query(Student).filter(Student.email == email).first()
        or db.query(Supervisor).filter(Supervisor.email == email).first()
    ):
        email = f"{base_prefix}-{count}{suffix}"
        count += 1

    return email

def create_user(db: Session, user: UserCreate):
    first = user.first_name.lower()
    last = user.last_name.lower()

    # 判断邮箱所属域名
    domain = "student.uts.edu.au" if "student" in user.email else "uts.edu.au"
    final_email = generate_unique_email(db, first, last, domain)

    user_group = "student" if "student" in final_email else "supervisor"

    if user_group == "student":
        db_user = Student(
            first_name=first,
            last_name=last,
            email=final_email,
            password=user.password,
            user_group_identifier=user_group
        )
    else:
        db_user = Supervisor(
            first_name=first,
            last_name=last,
            email=final_email,
            password=user.password,
            user_group_identifier=user_group
        )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user
