from fastapi import APIRouter, Depends
from app.services.users_service import UserService
from app.models.models import User


users_router = APIRouter()


@users_router.post("/register")
def register(user: User):
    pass


@users_router.get("/users")
def get_all_users():
    pass


@users_router.get("/users/{user_id}")
def get_user_by_id(user_id: str):
    pass


@users_router.delete("/users/{id}")
def delete_user_by_id(id: str):
    pass
