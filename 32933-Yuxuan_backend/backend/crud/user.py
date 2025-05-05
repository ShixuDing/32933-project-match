from sqlalchemy.orm import Session
from models.student import Student
from models.supervisor import Supervisor
from schemas.user import UserCreate
from models.user_base import UserBase
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def generate_unique_email(db: Session, first: str, last: str, domain: str) -> str:
    base_prefix = f"{first}.{last}"
    suffix = f"@{domain}"
    email = base_prefix + suffix
    count = 1

    # check repeated name
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

    domain = user.email.split('@')[-1]

    final_email = generate_unique_email(db, first, last, domain)

    user_group = user.user_group_identifier.lower()

    if user_group == "student":
        db_user = Student(
            first_name=first,
            last_name=last,
            email=final_email,
            password=hash_password(user.password),
            user_group_identifier=user_group
        )
    else:
        db_user = Supervisor(
            first_name=first,
            last_name=last,
            email=final_email,
            password=hash_password(user.password),
            user_group_identifier=user_group
        )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user
def get_user_by_email(db: Session, email: str):
    user = db.query(Supervisor).filter(Supervisor.email == email).first()
    if not user:
        user = db.query(Student).filter(Student.email == email).first()
    return user