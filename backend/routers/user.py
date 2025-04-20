# routers/user.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from schemas.user import UserCreate
from crud.user import create_user
from database import get_db
from schemas.user import LoginRequest, RefreshTokenRequest, UserResponse
from services.auth import login_user, refresh_access_token 
from database import get_db    
from dependencies.auth import get_current_user      

router = APIRouter()

@router.post("/register")
def register(user: UserCreate, db: Session = Depends(get_db)):
    return create_user(db, user)

@router.post("/login")
def login(request: LoginRequest, db: Session = Depends(get_db)):
    return login_user(db, request.email, request.password)

@router.post("/refresh")
def refresh_token(request: RefreshTokenRequest):
    new_token = refresh_access_token(request.refresh_token)
    if not new_token:
        raise HTTPException(status_code=401, detail="Invalid refresh token")
    return {"access_token": new_token, "token_type": "bearer"}

@router.get("/me", response_model=UserResponse)
def get_me(user = Depends(get_current_user)):
    return user