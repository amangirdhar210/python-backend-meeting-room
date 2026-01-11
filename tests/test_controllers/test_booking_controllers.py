import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, MagicMock
from app.models.models import Booking, RoomScheduleResponse, ScheduleSlot
from app.utils.errors import (
    InvalidInputError,
    NotFoundError,
    RoomUnavailableError,
    TimeRangeInvalidError,
)


class TestBookingsControllers:

    @pytest.fixture
    def mock_booking_service(self):
        return MagicMock()

    @pytest.fixture
    def client(self, mock_booking_service):
        from fastapi import FastAPI, Request
        from app.controllers.bookings_controllers import bookings_router
        from app.dependencies.dependencies import get_booking_service
        from app.middleware.auth_middleware import set_current_user, require_admin_state
        from app.utils.exception_handlers import (
            invalid_input_exception_handler,
            not_found_exception_handler,
            room_unavailable_exception_handler,
            time_range_invalid_exception_handler,
            general_exception_handler,
        )

        app = FastAPI()
        app.include_router(bookings_router)

        app.add_exception_handler(InvalidInputError, invalid_input_exception_handler)
        app.add_exception_handler(NotFoundError, not_found_exception_handler)
        app.add_exception_handler(
            RoomUnavailableError, room_unavailable_exception_handler
        )
        app.add_exception_handler(
            TimeRangeInvalidError, time_range_invalid_exception_handler
        )
        app.add_exception_handler(Exception, general_exception_handler)

        async def mock_set_current_user(request: Request):
            request.state.user = {
                "user_id": "admin-123",
                "email": "admin@example.com",
                "role": "admin",
            }

        async def mock_require_admin(request: Request):
            pass

        app.dependency_overrides[get_booking_service] = lambda: mock_booking_service
        app.dependency_overrides[set_current_user] = mock_set_current_user
        app.dependency_overrides[require_admin_state] = mock_require_admin

        return TestClient(app, raise_server_exceptions=False)

    @pytest.fixture
    def sample_booking(self):
        return Booking(
            id="booking-123",
            user_id="user-456",
            user_name="John Doe",
            room_id="room-789",
            room_number=101,
            start_time=1704800000,
            end_time=1704803600,
            purpose="Team meeting",
            status="confirmed",
            created_at=1704700000,
            updated_at=1704700000,
        )

    def test_create_booking_success(self, client, mock_booking_service):
        mock_booking_service.create_booking = AsyncMock()

        response = client.post(
            "/api/bookings",
            json={
                "room_id": "room-789",
                "start_time": 1704800000,
                "end_time": 1704803600,
                "purpose": "Team meeting",
            },
        )

        assert response.status_code == 201
        assert response.json() == {"message": "booking created successfully"}
        mock_booking_service.create_booking.assert_called_once()

    def test_create_booking_room_unavailable(self, client, mock_booking_service):
        mock_booking_service.create_booking = AsyncMock(
            side_effect=RoomUnavailableError("Room is already booked for this time")
        )

        response = client.post(
            "/api/bookings",
            json={
                "room_id": "room-789",
                "start_time": 1704800000,
                "end_time": 1704803600,
                "purpose": "Meeting",
            },
        )

        assert response.status_code == 409

    def test_create_booking_invalid_time_range(self, client, mock_booking_service):
        response = client.post(
            "/api/bookings",
            json={
                "room_id": "room-789",
                "start_time": 1704803600,
                "end_time": 1704800000,
                "purpose": "Meeting",
            },
        )

        assert response.status_code == 422

    @pytest.mark.parametrize(
        "payload,description",
        [
            (
                {
                    "start_time": 1704800000,
                    "end_time": 1704803600,
                    "purpose": "Meeting",
                },
                "missing room_id",
            ),
            (
                {"room_id": "room-789", "end_time": 1704803600, "purpose": "Meeting"},
                "missing start_time",
            ),
            (
                {"room_id": "room-789", "start_time": 1704800000, "purpose": "Meeting"},
                "missing end_time",
            ),
            (
                {
                    "room_id": "room-789",
                    "start_time": 1704800000,
                    "end_time": 1704803600,
                },
                "missing purpose",
            ),
            (
                {
                    "room_id": "",
                    "start_time": 1704800000,
                    "end_time": 1704803600,
                    "purpose": "Meeting",
                },
                "empty room_id",
            ),
            (
                {
                    "room_id": "room-789",
                    "start_time": 0,
                    "end_time": 1704803600,
                    "purpose": "Meeting",
                },
                "invalid start_time",
            ),
            (
                {
                    "room_id": "room-789",
                    "start_time": 1704800000,
                    "end_time": 0,
                    "purpose": "Meeting",
                },
                "invalid end_time",
            ),
            (
                {
                    "room_id": "room-789",
                    "start_time": 1704800000,
                    "end_time": 1704803600,
                    "purpose": "",
                },
                "empty purpose",
            ),
        ],
    )
    def test_create_booking_validation_errors(self, client, payload, description):
        response = client.post("/api/bookings", json=payload)
        assert response.status_code == 422, f"Failed for case: {description}"

    def test_get_booking_by_id_success(
        self, client, mock_booking_service, sample_booking
    ):
        mock_booking_service.get_booking_by_id = AsyncMock(return_value=sample_booking)

        response = client.get("/api/bookings/booking-123")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == "booking-123"
        assert data["user_id"] == "user-456"
        assert data["room_id"] == "room-789"
        assert data["purpose"] == "Team meeting"
        assert data["status"] == "confirmed"

    def test_get_booking_by_id_not_found(self, client, mock_booking_service):
        mock_booking_service.get_booking_by_id = AsyncMock(
            side_effect=NotFoundError("Booking not found")
        )

        response = client.get("/api/bookings/nonexistent")

        assert response.status_code == 404

    def test_cancel_booking_success(self, client, mock_booking_service):
        mock_booking_service.cancel_booking = AsyncMock()

        response = client.delete("/api/bookings/booking-123")

        assert response.status_code == 200
        assert response.json() == {"message": "booking cancelled successfully"}
        mock_booking_service.cancel_booking.assert_called_once_with("booking-123")

    def test_cancel_booking_not_found(self, client, mock_booking_service):
        mock_booking_service.cancel_booking = AsyncMock(
            side_effect=NotFoundError("Booking not found")
        )

        response = client.delete("/api/bookings/nonexistent")

        assert response.status_code == 404

    def test_get_all_bookings_as_admin(
        self, client, mock_booking_service, sample_booking
    ):
        bookings = [sample_booking]
        mock_booking_service.get_all_bookings = AsyncMock(return_value=bookings)

        response = client.get("/api/bookings")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["id"] == "booking-123"
        mock_booking_service.get_all_bookings.assert_called_once()

    def test_get_all_bookings_empty(self, client, mock_booking_service):
        mock_booking_service.get_all_bookings = AsyncMock(return_value=[])

        response = client.get("/api/bookings")

        assert response.status_code == 200
        assert response.json() == []

    def test_get_bookings_by_room_id_success(
        self, client, mock_booking_service, sample_booking
    ):
        bookings = [sample_booking]
        mock_booking_service.get_bookings_by_room_id = AsyncMock(return_value=bookings)

        response = client.get("/api/rooms/room-789/bookings")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["room_id"] == "room-789"
        mock_booking_service.get_bookings_by_room_id.assert_called_once_with("room-789")

    def test_get_bookings_by_room_id_empty(self, client, mock_booking_service):
        mock_booking_service.get_bookings_by_room_id = AsyncMock(return_value=[])

        response = client.get("/api/rooms/room-789/bookings")

        assert response.status_code == 200
        assert response.json() == []

    def test_get_my_bookings_success(
        self, client, mock_booking_service, sample_booking
    ):
        bookings = [sample_booking]
        mock_booking_service.get_bookings_by_user_id = AsyncMock(return_value=bookings)

        response = client.get("/api/bookings/my")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["user_id"] == "user-456"

    def test_get_room_schedule_by_date_success(self, client, mock_booking_service):
        schedule = RoomScheduleResponse(
            room_id="room-789",
            room_name="Conference Room A",
            room_number=101,
            date=1704700000,
            bookings=[
                ScheduleSlot(
                    start_time=1704800000,
                    end_time=1704803600,
                    is_booked=True,
                    booking_id="booking-123",
                    user_name="John Doe",
                    purpose="Team meeting",
                ),
                ScheduleSlot(
                    start_time=1704803600,
                    end_time=1704807200,
                    is_booked=False,
                ),
            ],
        )
        mock_booking_service.get_room_schedule_by_date = AsyncMock(
            return_value=schedule
        )

        response = client.get("/api/rooms/room-789/schedule?date=2024-01-09")

        assert response.status_code == 200
        data = response.json()
        assert data["room_id"] == "room-789"
        assert data["room_name"] == "Conference Room A"
        assert len(data["bookings"]) == 2
        assert data["bookings"][0]["is_booked"] is True
        assert data["bookings"][1]["is_booked"] is False

    def test_get_room_schedule_invalid_date_format(self, client, mock_booking_service):
        response = client.get("/api/rooms/room-789/schedule?date=invalid-date")

        assert response.status_code == 400

    def test_get_room_schedule_missing_date(self, client, mock_booking_service):
        response = client.get("/api/rooms/room-789/schedule")

        assert response.status_code == 422

    def test_create_booking_room_not_found(self, client, mock_booking_service):
        mock_booking_service.create_booking = AsyncMock(
            side_effect=NotFoundError("Room not found")
        )

        response = client.post(
            "/api/bookings",
            json={
                "room_id": "nonexistent",
                "start_time": 1704800000,
                "end_time": 1704803600,
                "purpose": "Meeting",
            },
        )

        assert response.status_code == 404
