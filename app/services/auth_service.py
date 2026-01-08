from typing import Tuple
from app.models.models import User
from app.repositories.users_repo import UserRepository
from app.utils.errors import InvalidInputError, UnauthorizedError
from app.utils import jwt_utils, password_utils


class AuthService:

    def __init__(self, user_repository: UserRepository) -> None:
        self.user_repo: UserRepository = user_repository

    async def login(self, email: str, password: str) -> Tuple[str, User]:
        email = email.strip()
        password = password.strip()

        if not email or not password:
            raise InvalidInputError("Email and password are required")

        user: User = await self.user_repo.find_by_email(email)
        if not user:
            raise UnauthorizedError("Invalid credentials")

        if not password_utils.verify_password(user.password, password):
            raise UnauthorizedError("Invalid credentials")

        token: str = jwt_utils.generate_token(user.id, user.role)

        return token, user
