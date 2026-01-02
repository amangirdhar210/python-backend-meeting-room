from fastapi import APIRouter, Depends
from app.services.auth_service import AuthService


auth_router = APIRouter()


@auth_router.post("/login")
def login(email: str, password: str):
    pass
