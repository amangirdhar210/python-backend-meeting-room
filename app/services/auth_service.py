from typing import Tuple, Optional
from app.models.models import User
from app.repositories.users_repo import UserRepository
from app.utils.errors import InvalidInputError, UnauthorizedError


class AuthService:

    def __init__(
        self, user_repository: UserRepository, token_generator, password_hasher
    ):
        self.user_repo = user_repository
        self.token_generator = token_generator
        self.password_hasher = password_hasher

    def login(self, email: str, password: str) -> Tuple[str, Optional[User]]:
        email = email.strip()
        password = password.strip()

        if not email or not password:
            raise InvalidInputError("Email and password are required")

        user = self.user_repo.find_by_email(email)
        if not user:
            raise UnauthorizedError("Invalid credentials")

        if not self.password_hasher.verify_password(user.password, password):
            raise UnauthorizedError("Invalid credentials")

        token = self.token_generator.generate_token(user.id, user.role)

        return token, user
