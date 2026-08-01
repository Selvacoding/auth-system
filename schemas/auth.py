from datetime import datetime
import re

from pydantic import BaseModel, EmailStr, Field, field_validator

class UserRegistrationRequest(BaseModel):
    username: str
    email: EmailStr
    password: str = Field(min_length=8)

    @field_validator("password")
    @classmethod
    def validate_password(cls, password: str):
        if not re.search(r"[A-Z]", password):
            raise ValueError("Password must contain at least one uppercase letter.")

        if not re.search(r"[a-z]", password):
            raise ValueError("Password must contain at least one lowercase letter.")

        if not re.search(r"\d", password):
            raise ValueError("Password must contain at least one digit.")

        if not re.search(r"[!@#$%^&*(),.?\":{}|<>_\-]", password):
            raise ValueError("Password must contain at least one special character.")

        return password

class UserLoginRequest(BaseModel):
    email: EmailStr
    password: str

class ProfileResponse(BaseModel):
    id: int
    username: str
    email: EmailStr
    created_at: datetime

class LogoutRequest(BaseModel):
    refresh_token: str

class RefreshTokenRequest(BaseModel):
    refresh_token: str
