import pytest
from unittest.mock import Mock
from fastapi import Request
from app.dependencies.dependencies import (
    get_dynamodb_client,
    get_user_repository,
    get_room_repository,
    get_booking_repository,
    get_auth_service,
    get_user_service,
    get_room_service,
    get_booking_service,
)
from app.repositories.users_repo import UserRepository
from app.repositories.rooms_repo import RoomRepository
from app.repositories.bookings_repo import BookingRepository
from app.services.auth_service import AuthService
from app.services.users_service import UserService
from app.services.rooms_service import RoomService
from app.services.bookings_service import BookingService


class TestDependencies:

    def test_get_dynamodb_client(self):
        request = Mock(spec=Request)
        mock_client = Mock()
        request.app.state.db_client = mock_client

        result = get_dynamodb_client(request)

        assert result == mock_client

    def test_get_user_repository(self):
        request = Mock(spec=Request)
        mock_repo = Mock(spec=UserRepository)
        request.app.state.user_repo = mock_repo

        result = get_user_repository(request)

        assert result == mock_repo
        assert isinstance(result, type(mock_repo))

    def test_get_room_repository(self):
        request = Mock(spec=Request)
        mock_repo = Mock(spec=RoomRepository)
        request.app.state.room_repo = mock_repo

        result = get_room_repository(request)

        assert result == mock_repo
        assert isinstance(result, type(mock_repo))

    def test_get_booking_repository(self):
        request = Mock(spec=Request)
        mock_repo = Mock(spec=BookingRepository)
        request.app.state.booking_repo = mock_repo

        result = get_booking_repository(request)

        assert result == mock_repo
        assert isinstance(result, type(mock_repo))

    def test_get_auth_service(self):
        request = Mock(spec=Request)
        mock_service = Mock(spec=AuthService)
        request.app.state.auth_service = mock_service

        result = get_auth_service(request)

        assert result == mock_service
        assert isinstance(result, type(mock_service))

    def test_get_user_service(self):
        request = Mock(spec=Request)
        mock_service = Mock(spec=UserService)
        request.app.state.user_service = mock_service

        result = get_user_service(request)

        assert result == mock_service
        assert isinstance(result, type(mock_service))

    def test_get_room_service(self):
        request = Mock(spec=Request)
        mock_service = Mock(spec=RoomService)
        request.app.state.room_service = mock_service

        result = get_room_service(request)

        assert result == mock_service
        assert isinstance(result, type(mock_service))

    def test_get_booking_service(self):
        request = Mock(spec=Request)
        mock_service = Mock(spec=BookingService)
        request.app.state.booking_service = mock_service

        result = get_booking_service(request)

        assert result == mock_service
        assert isinstance(result, type(mock_service))
