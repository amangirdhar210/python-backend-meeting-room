import boto3
from typing import Any
from functools import lru_cache
from app.config.config import settings
from app.repositories.users_repo import UserRepository
from app.repositories.rooms_repo import RoomRepository
from app.repositories.bookings_repo import BookingRepository
from app.services.auth_service import AuthService
from app.services.users_service import UserService
from app.services.rooms_service import RoomService
from app.services.bookings_service import BookingService


@lru_cache()
def get_dynamodb_client() -> Any:
    return boto3.resource("dynamodb", region_name=settings.AWS_REGION)


@lru_cache()
def get_user_repository() -> UserRepository:
    dynamodb: Any = get_dynamodb_client()
    return UserRepository(dynamodb, settings.DYNAMODB_TABLE_NAME)


@lru_cache()
def get_room_repository() -> RoomRepository:
    dynamodb: Any = get_dynamodb_client()
    return RoomRepository(dynamodb, settings.DYNAMODB_TABLE_NAME)


@lru_cache()
def get_booking_repository() -> BookingRepository:
    dynamodb: Any = get_dynamodb_client()
    return BookingRepository(dynamodb, settings.DYNAMODB_TABLE_NAME)


@lru_cache()
def get_auth_service() -> AuthService:
    return AuthService(get_user_repository())


@lru_cache()
def get_user_service() -> UserService:
    return UserService(get_user_repository(), get_booking_repository())


@lru_cache()
def get_room_service() -> RoomService:
    return RoomService(get_room_repository())


@lru_cache()
def get_booking_service() -> BookingService:
    return BookingService(
        get_booking_repository(), get_room_repository(), get_user_repository()
    )
