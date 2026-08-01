
from datetime import datetime, timedelta, timezone
from uuid import uuid4

import jwt
from pwdlib import PasswordHash
from fastapi import Depends
from fastapi.exceptions import HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

import CONFIG
from db.database import get_user_by_id

password_hash = PasswordHash.recommended()
security = HTTPBearer()

SECRET_KEY = CONFIG.SECRET_KEY
ALGORITHM = CONFIG.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = CONFIG.ACCESS_TOKEN_EXPIRE_MINUTES
REFRESH_TOKEN_EXPIRE_DAYS = CONFIG.REFRESH_TOKEN_EXPIRE_DAYS

def hash_password(password: str):
    return password_hash.hash(password)

def verify_password(password: str, hashed_password: str):
    return password_hash.verify(password, hashed_password)

def create_access_token(data: dict, expires_delta: timedelta = None, token_type: str = "access"):
    to_encode = data.copy()
    now = datetime.now(timezone.utc)
    
    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(minutes=15)

    to_encode.update(
        {
            "exp": expire,
            "iat": now,
            "jti": str(uuid4()),
            "type": token_type
        }
    )

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        token_type = payload.get("type")

        if user_id is None:
            raise HTTPException(status_code=401,detail="Invalid token.")
        
        if token_type != "access":
            raise HTTPException(status_code=401, detail="Access token required.")

    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token.")

    user = get_user_by_id(int(user_id))

    if user is None:
        raise HTTPException(status_code=401, detail="User not found.")

    return user
