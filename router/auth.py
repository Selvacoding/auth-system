from fastapi.routing import APIRouter
from fastapi import Depends

from services.auth import AuthService
from repositories.auth_repository import AuthRepository
from schemas.auth import LogoutRequest, RefreshTokenRequest, UserRegistrationRequest, UserLoginRequest, ProfileResponse
from utils.auth import get_current_user

auth_router = APIRouter()

def get_auth_repository():
    return AuthRepository()

def get_auth_service(repository: AuthRepository = Depends(get_auth_repository)):
    return AuthService(repository)

@auth_router.post("/register")
def register(payload: UserRegistrationRequest, auth_service=Depends(get_auth_service)):
    return auth_service.register(payload.username, payload.email, payload.password)
    
@auth_router.post("/login")
def login(payload: UserLoginRequest, auth_service=Depends(get_auth_service)):
    return auth_service.login(payload.email, payload.password)

@auth_router.post("/logout")
def logout(payload: LogoutRequest, current_user=Depends(get_current_user), auth_service=Depends(get_auth_service)):
    return auth_service.logout(current_user.id, payload.refresh_token)

@auth_router.post("/refresh")
def refresh_token(payload: RefreshTokenRequest, auth_service=Depends(get_auth_service)):
    return auth_service.refresh(payload.refresh_token)

@auth_router.get("/profile", response_model=ProfileResponse)
def get_profile(current_user=Depends(get_current_user), auth_service=Depends(get_auth_service)):
    return {
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email,
        "created_at": current_user.created_at
    }
