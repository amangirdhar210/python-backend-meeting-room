from typing import Tuple
from app.models.models import User
from app.repositories.users_repo import UserRepository
from app.utils.errors import InvalidInputError, UnauthorizedError
from app.utils.jwt_utils import JWTGenerator
from app.utils.password_utils import PasswordHasher


class AuthService:

    def __init__(
        self,
        user_repository: UserRepository,
        token_generator: JWTGenerator,
        password_hasher: PasswordHasher,
    ) -> None:
        self.user_repo: UserRepository = user_repository
        self.token_generator: JWTGenerator = token_generator
        self.password_hasher: PasswordHasher = password_hasher

    async def login(self, email: str, password: str) -> Tuple[str, User]:
        email = email.strip()
        password = password.strip()

        if not email or not password:
            raise InvalidInputError("Email and password are required")

        user: User = await self.user_repo.find_by_email(email)
        if not user:
            raise UnauthorizedError("Invalid credentials")

        if not self.password_hasher.verify_password(user.password, password):
            raise UnauthorizedError("Invalid credentials")

        token: str = self.token_generator.generate_token(user.id, user.role)

        return token, user
