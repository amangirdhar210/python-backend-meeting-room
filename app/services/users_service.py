from typing import List
from app.models.models import User
from app.repositories.users_repo import UserRepository


class UserService:

    def __init__(self, user_repository: UserRepository, password_hasher):
        pass

    def register(self, user: User) -> None:
        pass

    def get_all_users(self) -> List[User]:
        pass

    def get_user_by_id(self, user_id: str) -> User:
        pass

    def delete_user_by_id(self, user_id: str) -> None:
        pass
