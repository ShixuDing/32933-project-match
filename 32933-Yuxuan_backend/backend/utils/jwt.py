from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError

SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 15 
REFRESH_TOKEN_EXPIRE_DAYS = 7 

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    now = datetime.now(timezone.utc) 
    expire = now + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({
        "exp": expire,
        "type": "access",
        "iat": now.timestamp()
    })
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def create_refresh_token(data: dict):
    now = datetime.now(timezone.utc)  
    expire = now + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    data.update({
        "exp": expire,
        "type": "refresh",
        "iat": now.timestamp()  
    })
    return jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)

def decode_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        print("[✅ Token Decoded Successfully]")
        return payload
    except JWTError as e:
        print(f"[❌ Token Decode Error]: {e}")
        return None