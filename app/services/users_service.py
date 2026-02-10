from typing import List, Optional
import uuid
import time
from app.models.models import User
from app.repositories.users_repo import UserRepository
from app.repositories.bookings_repo import BookingRepository
from app.utils.errors import ApplicationError, ErrorCode
from app.utils import password_utils
from app.config.config import settings


class UserService:

    def __init__(
        self,
        user_repository: UserRepository,
        booking_repository: BookingRepository = None,
    ) -> None:
        self.user_repo: UserRepository = user_repository
        self.booking_repo: BookingRepository = booking_repository

    async def register(self, user: User) -> None:
        existing: User | None = None
        try:
            existing = await self.user_repo.find_by_email(user.email)
        except ApplicationError as e:
            if e.error_code != ErrorCode.USER_NOT_FOUND:
                raise

        if existing:
            raise ApplicationError(ErrorCode.USER_ALREADY_EXISTS)

        hashed: str = password_utils.hash_password(user.password)
        user.id = str(uuid.uuid4())
        user.password = hashed
        user.created_at = int(time.time())
        user.updated_at = int(time.time())

        await self.user_repo.create(user)

    async def get_all_users(self) -> List[User]:
        users: List[User] = await self.user_repo.get_all()
        if users:
            users = [user for user in users if user.role != "superadmin"]
        return users if users else []

    async def get_user_by_id(self, user_id: str) -> User:
        return await self.user_repo.get_by_id(user_id)

    async def update_user(
        self, user_id: str, update_data, current_user_id: Optional[str] = None
    ) -> None:
        user: User = await self.user_repo.get_by_id(user_id)
        old_email = user.email

        if current_user_id and user_id == current_user_id:
            raise ApplicationError(
                ErrorCode.INVALID_INPUT, message="You cannot edit your own account"
            )

        if user.role == "superadmin":
            raise ApplicationError(
                ErrorCode.INVALID_INPUT, message="Superadmin accounts cannot be updated"
            )

        update_dict = update_data.model_dump(exclude_unset=True)
        
        if "email" in update_dict and update_dict["email"] != user.email:
            existing: User | None = None
            try:
                existing = await self.user_repo.find_by_email(update_dict["email"])
            except ApplicationError as e:
                if e.error_code != ErrorCode.USER_NOT_FOUND:
                    raise

            if existing:
                raise ApplicationError(
                    ErrorCode.USER_ALREADY_EXISTS, message="Email already in use"
                )
        
        for field, value in update_dict.items():
            setattr(user, field, value)

        user.updated_at = int(time.time())
        await self.user_repo.update(user, old_email=old_email)

    async def delete_user_by_id(
        self, user_id: str, current_user_id: Optional[str] = None
    ) -> None:
        if current_user_id and user_id == current_user_id:
            raise ApplicationError(
                ErrorCode.INVALID_INPUT, message="You cannot delete yourself"
            )

        user_to_delete: User = await self.user_repo.get_by_id(user_id)
        
        if user_to_delete.role == "superadmin":
            raise ApplicationError(
                ErrorCode.INVALID_INPUT, message="Superadmin accounts cannot be deleted"
            )

        if self.booking_repo:
            await self.booking_repo.delete_by_user_id(user_id)

        await self.user_repo.delete_by_id(user_id)
