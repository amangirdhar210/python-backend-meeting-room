from typing import Annotated, Any
from fastapi import Depends, Request
from app.repositories.users_repo import UserRepository
from app.repositories.rooms_repo import RoomRepository
from app.repositories.bookings_repo import BookingRepository
from app.services.auth_service import AuthService
from app.services.users_service import UserService
from app.services.rooms_service import RoomService
from app.services.bookings_service import BookingService


def get_dynamodb_client(request: Request) -> Any:
    return request.app.state.db_client


def get_user_repository(request: Request) -> UserRepository:
    return request.app.state.user_repo


def get_room_repository(request: Request) -> RoomRepository:
    return request.app.state.room_repo


def get_booking_repository(request: Request) -> BookingRepository:
    return request.app.state.booking_repo


def get_auth_service(request: Request) -> AuthService:
    return request.app.state.auth_service


def get_user_service(request: Request) -> UserService:
    return request.app.state.user_service


def get_room_service(request: Request) -> RoomService:
    return request.app.state.room_service


def get_booking_service(request: Request) -> BookingService:
    return request.app.state.booking_service


DynamoDBResource = Annotated[Any, Depends(get_dynamodb_client)]
UserRepoInstance = Annotated[UserRepository, Depends(get_user_repository)]
RoomRepoInstance = Annotated[RoomRepository, Depends(get_room_repository)]
BookingRepoInstance = Annotated[BookingRepository, Depends(get_booking_repository)]
AuthServiceInstance = Annotated[AuthService, Depends(get_auth_service)]
UserServiceInstance = Annotated[UserService, Depends(get_user_service)]
RoomServiceInstance = Annotated[RoomService, Depends(get_room_service)]
BookingServiceInstance = Annotated[BookingService, Depends(get_booking_service)]
