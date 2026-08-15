from fastapi import FastAPI

from router.auth import auth_router
from router.sample import sample_router
from exceptions.handlers import register_exception_handlers

app = FastAPI()

register_exception_handlers(app)

app.include_router(auth_router, prefix="/auth", tags=["Authentication"])
app.include_router(sample_router, prefix="/sample", tags=["Sample"])

@app.get("/")
def root():
    return {"message": "Auth Service is running"}
