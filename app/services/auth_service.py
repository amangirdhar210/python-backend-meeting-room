from typing import Tuple, Optional
from app.models.models import User
from app.repositories.users_repo import UserRepository


class AuthService:

    def __init__(
        self, user_repository: UserRepository, token_generator, password_hasher
    ):
        pass

    def login(self, email: str, password: str) -> Tuple[str, Optional[User]]:
        pass
