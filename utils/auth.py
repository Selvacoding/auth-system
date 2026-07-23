
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

import jwt
from pwdlib import PasswordHash
from fastapi import Depends, Header
from fastapi.responses import JSONResponse
from fastapi.exceptions import HTTPException
from fastapi.security import HTTPBearer, OAuth2PasswordBearer, HTTPAuthorizationCredentials

import CONFIG
from db.database import get_user_by_email, create_user, save_refresh_token, revoke_refresh_token

password_hash = PasswordHash.recommended()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")
security = HTTPBearer()

SECRET_KEY = CONFIG.SECRET_KEY
ALGORITHM = CONFIG.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = CONFIG.ACCESS_TOKEN_EXPIRE_MINUTES
REFRESH_TOKEN_EXPIRE_DAYS = CONFIG.REFRESH_TOKEN_EXPIRE_DAYS

def hash_password(password: str):
    return password_hash.hash(password)

def verify_password(password: str, hashed_password: str):
    return password_hash.verify(password, hashed_password)

def is_user_exists(email: str):
    return get_user_by_email(email) is not None

def create_user_in_db(username: str, email: str, password: str):
    if is_user_exists(email):
        raise HTTPException(status_code=409, detail="User with this email already exists.")
    hashed_password = hash_password(password)
    create_user(username, email, hashed_password)
    return JSONResponse(status_code=201, content={"message": "User created successfully."})

def create_access_token(data: dict, expires_delta: timedelta = None, token_type: str = "access"):
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)

    to_encode.update({"exp": expire, "type": token_type})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
    
def login_user(email: str, password: str):
    user = get_user_by_email(email)

    if not user:
        raise HTTPException(status_code=401, detail="User not found. Please register first.")

    result = verify_password(password, user.password)

    if not result:
        raise HTTPException(status_code=401, detail="Invalid password.")

    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES), token_type="access"
        )

    refresh_token = create_access_token(
        data={"sub": user.email}, expires_delta=timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS), token_type="refresh"
        )
    save_refresh_token(user.id, refresh_token, datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS))
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials

    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        email = payload.get("sub")
        token_type = payload.get("type")

        if email is None:
            raise HTTPException(status_code=401,detail="Invalid token.")
        
        if token_type != "access":
            raise HTTPException(status_code=401, detail="Access token required.")

    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token.")

    user = get_user_by_email(email)

    if user is None:
        raise HTTPException(status_code=401, detail="User not found.")

    return user

def refresh_access_token(refresh_token: str):
    try:
        payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])

        email = payload.get("sub")
        token_type = payload.get("type")

        if email is None:
            raise HTTPException(status_code=401, detail="Invalid refresh token.")

        if token_type != "refresh":
            raise HTTPException(status_code=401, detail="Invalid token type.")

    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token.")

    user = get_user_by_email(email)

    if user is None:
        raise HTTPException(status_code=401, detail="User not found.")

    new_access_token = create_access_token(data={"sub": email},
                                            expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES), 
                                            token_type="access")

    return {
        "access_token": new_access_token,
        "token_type": "bearer"
    }

def logout_user(refresh_token: str):
    result  = revoke_refresh_token(refresh_token)

    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="Refresh token not found.")

    return {
        "message": "Logged out successfully."
    }