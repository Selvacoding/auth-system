from fastapi.routing import APIRouter
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from services.auth import AuthService
from schemas.auth import LogoutRequest, UserRegistrationRequest, UserLoginRequest, ProfileResponse
from utils.auth import get_current_user, refresh_access_token

auth_router = APIRouter()
auth_service = AuthService()

@auth_router.post("/register")
def register(payload: UserRegistrationRequest):
    return auth_service.register(payload.username, payload.email, payload.password)
    
@auth_router.post("/login")
def login(payload: UserLoginRequest):
    return auth_service.login(
        payload.email,
        payload.password
    )

@auth_router.post("/logout")
def logout(payload: LogoutRequest):
    return auth_service.logout(
        payload.refresh_token
    )

@auth_router.post("/refresh")
def refresh_token(refresh_token: str):
    return refresh_access_token(refresh_token)

@auth_router.get("/profile", response_model=ProfileResponse)
def get_profile(current_user=Depends(get_current_user)):
    return {
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email,
        "created_at": current_user.created_at
    }
