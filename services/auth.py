from datetime import datetime, timedelta, timezone

from fastapi import HTTPException
import jwt

import CONFIG
from repositories.auth_repository import AuthRepository
from utils.auth import (
    hash_password,
    verify_password,
    create_access_token
)

class AuthService:
    def __init__(self, repository: AuthRepository):
        self.repository = repository

    def register(self, username: str, email: str, password: str):
        user = self.repository.get_user_by_email(email)

        if user is not None:
            raise HTTPException(status_code=409, detail="User with this email already exists.")
        
        hashed_password = hash_password(password)
        # user = self.repository.create_user(username, email, hashed_password)
        
        # publish_user_registered(user.id, user.username, user.email)
        self.repository.create_user_with_outbox(username, email, hashed_password)

        return {"message": "User created successfully."}

    def login(self, email: str, password: str):
        user = self.repository.get_user_by_email(email)

        if user is None:
            raise HTTPException(status_code=401, detail="User not found. Please register first.")

        if not verify_password(password, user.password):
            raise HTTPException(status_code=401, detail="Invalid password.")

        access_token = create_access_token(
            data={
                "sub": str(user.id),
                "email": user.email
            },
            expires_delta=timedelta(
                minutes=CONFIG.ACCESS_TOKEN_EXPIRE_MINUTES
            ),
            token_type="access"
        )

        refresh_token = create_access_token(
            data={
                "sub": str(user.id),
                "email": user.email
            },
            expires_delta=timedelta(
                days=CONFIG.REFRESH_TOKEN_EXPIRE_DAYS
            ),
            token_type="refresh"
        )

        refresh_token_expires_at = (datetime.now(timezone.utc) + timedelta(days=CONFIG.REFRESH_TOKEN_EXPIRE_DAYS))

        self.repository.save_refresh_token(user.id, refresh_token, refresh_token_expires_at)

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer"
        }
        
    def logout(self, user_id: int, refresh_token: str):
        result = self.repository.revoke_refresh_token(user_id, refresh_token)
        if not result:
            raise HTTPException(status_code=404, detail="Refresh token not found or already revoked.")

        return {"message": "Logged out successfully."}
    
    def refresh(self, refresh_token: str):
        try:
            payload = jwt.decode(refresh_token, CONFIG.SECRET_KEY, algorithms=[CONFIG.ALGORITHM])
            user_id = payload.get("sub")
            token_type = payload.get("type")

            if user_id is None:
                raise HTTPException(status_code=401, detail="Invalid refresh token.")

            if token_type != "refresh":
                raise HTTPException(status_code=401, detail="Invalid token type.")

        except jwt.PyJWTError:
            raise HTTPException(status_code=401, detail="Invalid or expired refresh token.")

        user = self.repository.get_user_by_id(int(user_id))

        if user is None:
            raise HTTPException(status_code=401, detail="User not found.")

        new_access_token = create_access_token(
            data={
                "sub": str(user.id),
                "email": user.email
            },
            expires_delta=timedelta(
                minutes=CONFIG.ACCESS_TOKEN_EXPIRE_MINUTES
            ),
            token_type="access"
        )

        new_refresh_token = create_access_token(
            data={
                "sub": str(user.id),
                "email": user.email
            },
            expires_delta=timedelta(
                days=CONFIG.REFRESH_TOKEN_EXPIRE_DAYS
            ),
            token_type="refresh"
        )

        refresh_token_expires_at = (datetime.now(timezone.utc) + timedelta(days=CONFIG.REFRESH_TOKEN_EXPIRE_DAYS))

        result = self.repository.rotate_refresh_token(user.id, refresh_token, new_refresh_token, refresh_token_expires_at)

        if not result:
            raise HTTPException(status_code=401, detail="Refresh token has been revoked or does not exist.")

        return {
            "access_token": new_access_token,
            "refresh_token": new_refresh_token,
            "token_type": "bearer"
        }
