from fastapi import APIRouter, Depends

from utils.auth import get_current_user

sample_router = APIRouter()

@sample_router.get("/sample")
def sample_endpoint(current_user=Depends(get_current_user)):
    return {"message": "This is a sample endpoint."}


