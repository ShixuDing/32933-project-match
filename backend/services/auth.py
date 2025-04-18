from passlib.context import CryptContext
from crud.user import get_user_by_email
from utils.jwt import create_access_token

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def authenticate_user(db, email, password):
    user = get_user_by_email(db, email)
    if not user or not pwd_context.verify(password, user.password):
        return None
    return user

def login_user(db, email, password):
    user = authenticate_user(db, email, password)
    if not user:
        return None

    token_data = {
        "sub": user.email,
        "role": user.user_group_identifier  # Extract from database
    }

    token = create_access_token(token_data)
    return token
