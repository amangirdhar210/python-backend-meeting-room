from typing import List
import uuid
import time
from app.models.models import User
from app.repositories.users_repo import UserRepository
from app.utils.errors import InvalidInputError, NotFoundError, ConflictError
from app.utils.password_utils import PasswordHasher


class UserService:

    def __init__(
        self, user_repository: UserRepository, password_hasher: PasswordHasher
    ) -> None:
        self.user_repo: UserRepository = user_repository
        self.password_hasher: PasswordHasher = password_hasher

    async def register(self, user: User) -> None:
        if not user:
            raise InvalidInputError("User is required")

        user.email = user.email.strip()
        user.name = user.name.strip()
        user.role = user.role.strip()
        user.password = user.password.strip()

        if not user.email or not user.password or not user.name or not user.role:
            raise InvalidInputError("All fields are required")

        try:
            existing: User = await self.user_repo.find_by_email(user.email)
            if existing:
                raise ConflictError("User already exists")
        except NotFoundError:
            pass

        hashed: str = self.password_hasher.hash_password(user.password)
        user.id = str(uuid.uuid4())
        user.password = hashed
        user.created_at = int(time.time())
        user.updated_at = int(time.time())

        await self.user_repo.create(user)

    async def get_all_users(self) -> List[User]:
        users: List[User] = await self.user_repo.get_all()
        if not users:
            raise NotFoundError("No users found")
        return users

    async def get_user_by_id(self, user_id: str) -> User:
        if not user_id or len(user_id) < 10:
            raise InvalidInputError("Invalid user ID")
        return await self.user_repo.get_by_id(user_id)

    async def delete_user_by_id(self, user_id: str) -> None:
        if not user_id:
            raise InvalidInputError("User ID is required")
        await self.user_repo.delete_by_id(user_id)
