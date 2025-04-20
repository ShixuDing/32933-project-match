from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from utils.jwt import decode_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def get_current_user(token: str = Depends(oauth2_scheme)):
    user_data = decode_token(token)
    if not user_data:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    if user_data.get("type") != "access":
        raise HTTPException(status_code=401, detail="Access token required")

    return {
        "id": user_data["id"],
        "email": user_data["sub"],
        "role": user_data["role"]
    }

def require_student(user=Depends(get_current_user)):
    if user["role"] != "student":
        raise HTTPException(status_code=403, detail="Students only")
    return user

def require_supervisor(user=Depends(get_current_user)):
    if user["role"] != "supervisor":
        raise HTTPException(status_code=403, detail="Supervisors only")
    return user


