from passlib.context import CryptContext
from crud.user import get_user_by_email
from utils.jwt import create_access_token, decode_token, create_refresh_token
from fastapi import HTTPException

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def authenticate_user(db, email, password):
    user = get_user_by_email(db, email)
    if not user or not pwd_context.verify(password, user.password):
        return None
    return user

def login_user(db, email, password):
    user = authenticate_user(db, email, password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    user_data = {
        "id": user.id,
        "sub": user.email,
        "role": user.user_group_identifier
    }

    access_token = create_access_token(user_data)
    refresh_token = create_refresh_token(user_data)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,  
        "token_type": "bearer"
    }

def refresh_access_token(refresh_token: str):
    payload = decode_token(refresh_token)
    if not payload or payload.get("type") != "refresh":
        return None
    return create_access_token({"sub": payload["sub"], "role": payload["role"]})
