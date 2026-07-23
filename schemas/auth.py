from datetime import datetime

from pydantic import BaseModel, EmailStr

class UserRegistrationRequest(BaseModel):
    username: str
    email: EmailStr
    password: str

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