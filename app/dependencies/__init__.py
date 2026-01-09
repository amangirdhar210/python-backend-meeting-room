import boto3

from app.config.config import settings
from app.repositories.users_repo import UserRepository
from app.repositories.rooms_repo import RoomRepository
from app.repositories.bookings_repo import BookingRepository
from app.services.auth_service import AuthService
from app.services.users_service import UserService
from app.services.rooms_service import RoomService
from app.services.bookings_service import BookingService


def init_app_state(app_state):
    app_state.db_client = boto3.resource("dynamodb", region_name=settings.AWS_REGION)
    app_state.user_repo = UserRepository(
        app_state.db_client, settings.DYNAMODB_TABLE_NAME
    )
    app_state.room_repo = RoomRepository(
        app_state.db_client, settings.DYNAMODB_TABLE_NAME
    )
    app_state.booking_repo = BookingRepository(
        app_state.db_client, settings.DYNAMODB_TABLE_NAME
    )
    app_state.auth_service = AuthService(user_repository=app_state.user_repo)
    app_state.user_service = UserService(
        user_repository=app_state.user_repo, booking_repository=app_state.booking_repo
    )
    app_state.room_service = RoomService(room_repository=app_state.room_repo)
    app_state.booking_service = BookingService(
        booking_repository=app_state.booking_repo,
        room_repository=app_state.room_repo,
        user_repository=app_state.user_repo,
    )
