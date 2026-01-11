import pytest
from unittest.mock import AsyncMock
from app.services.bookings_service import BookingService
from app.models.models import (
    Booking,
    BookingWithDetails,
    Room,
    User,
    RoomScheduleResponse,
    ScheduleSlot,
)
from app.utils.errors import (
    InvalidInputError,
    NotFoundError,
    RoomUnavailableError,
    TimeRangeInvalidError,
)


class TestBookingService:

    @pytest.fixture
    def mock_booking_repo(self):
        return AsyncMock()

    @pytest.fixture
    def mock_room_repo(self):
        return AsyncMock()

    @pytest.fixture
    def mock_user_repo(self):
        return AsyncMock()

    @pytest.fixture
    def booking_service(self, mock_booking_repo, mock_room_repo, mock_user_repo):
        return BookingService(mock_booking_repo, mock_room_repo, mock_user_repo)

    @pytest.fixture
    def sample_booking(self):
        import time

        current = int(time.time())
        return Booking(
            id="booking-123",
            user_id="user-123",
            room_id="room-123",
            start_time=current + 3600,
            end_time=current + 7200,
            purpose="Team meeting",
            status="confirmed",
            user_name="Test User",
            room_number=101,
            created_at=current,
            updated_at=current,
        )

    @pytest.fixture
    def sample_user(self):
        return User(
            id="user-123",
            email="test@example.com",
            password="hash",
            name="Test User",
            role="user",
            created_at=1704067200,
            updated_at=1704067200,
        )

    @pytest.fixture
    def sample_room(self):
        return Room(
            id="room-123",
            name="Conference Room A",
            capacity=10,
            amenities=["Projector"],
            status="available",
            location="Building 1",
            room_number=101,
            floor=1,
            description="Main room",
            created_at=1704067200,
            updated_at=1704067200,
        )

    @pytest.mark.asyncio
    async def test_create_booking_success(
        self,
        booking_service,
        mock_booking_repo,
        mock_user_repo,
        mock_room_repo,
        sample_booking,
        sample_user,
        sample_room,
    ):
        mock_user_repo.get_by_id.return_value = sample_user
        mock_room_repo.get_by_id.return_value = sample_room
        mock_booking_repo.get_by_room_and_time.return_value = []
        sample_booking.id = None

        await booking_service.create_booking(sample_booking)

        assert sample_booking.id is not None
        assert sample_booking.status == "confirmed"
        mock_booking_repo.create.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_booking_none_booking(self, booking_service):
        with pytest.raises(InvalidInputError, match="Booking is required"):
            await booking_service.create_booking(None)

    @pytest.mark.asyncio
    async def test_create_booking_missing_user_id(
        self, booking_service, sample_booking
    ):
        sample_booking.user_id = None

        with pytest.raises(InvalidInputError, match="User ID and Room ID are required"):
            await booking_service.create_booking(sample_booking)

    @pytest.mark.asyncio
    async def test_create_booking_missing_room_id(
        self, booking_service, sample_booking
    ):
        sample_booking.room_id = None

        with pytest.raises(InvalidInputError, match="User ID and Room ID are required"):
            await booking_service.create_booking(sample_booking)

    @pytest.mark.asyncio
    async def test_create_booking_invalid_time_range(
        self, booking_service, sample_booking
    ):
        sample_booking.start_time = 1704070800
        sample_booking.end_time = 1704067200

        with pytest.raises(TimeRangeInvalidError, match="Invalid time range"):
            await booking_service.create_booking(sample_booking)

    @pytest.mark.asyncio
    async def test_create_booking_too_far_in_future(
        self, booking_service, sample_booking
    ):
        sample_booking.start_time = 9999999999
        sample_booking.end_time = 9999999999 + 3600

        with pytest.raises(InvalidInputError, match="Bookings can only be made up to"):
            await booking_service.create_booking(sample_booking)

    @pytest.mark.asyncio
    async def test_create_booking_user_not_found(
        self, booking_service, mock_user_repo, sample_booking
    ):
        mock_user_repo.get_by_id.return_value = None

        with pytest.raises(NotFoundError, match="User not found"):
            await booking_service.create_booking(sample_booking)

    @pytest.mark.asyncio
    async def test_create_booking_room_not_found(
        self,
        booking_service,
        mock_user_repo,
        mock_room_repo,
        sample_booking,
        sample_user,
    ):
        mock_user_repo.get_by_id.return_value = sample_user
        mock_room_repo.get_by_id.return_value = None

        with pytest.raises(NotFoundError, match="Room not found"):
            await booking_service.create_booking(sample_booking)

    @pytest.mark.asyncio
    async def test_create_booking_room_unavailable(
        self,
        booking_service,
        mock_booking_repo,
        mock_user_repo,
        mock_room_repo,
        sample_booking,
        sample_user,
        sample_room,
    ):
        import time

        current = int(time.time())
        mock_user_repo.get_by_id.return_value = sample_user
        mock_room_repo.get_by_id.return_value = sample_room
        conflicting_booking = Booking(
            id="booking-999",
            user_id="other-user",
            room_id="room-123",
            start_time=current + 3800,
            end_time=current + 7400,
            purpose="Other meeting",
            status="confirmed",
            user_name="Other User",
            room_number=101,
            created_at=current,
            updated_at=current,
        )
        mock_booking_repo.get_by_room_and_time.return_value = [conflicting_booking]

        with pytest.raises(RoomUnavailableError, match="Room is not available"):
            await booking_service.create_booking(sample_booking)

    @pytest.mark.asyncio
    async def test_get_booking_by_id_success(
        self, booking_service, mock_booking_repo, sample_booking
    ):
        mock_booking_repo.get_by_id.return_value = sample_booking

        booking = await booking_service.get_booking_by_id("booking-123")

        assert booking == sample_booking
        mock_booking_repo.get_by_id.assert_called_once_with("booking-123")

    @pytest.mark.asyncio
    async def test_get_booking_by_id_empty_id(self, booking_service):
        with pytest.raises(InvalidInputError, match="Booking ID is required"):
            await booking_service.get_booking_by_id("")

    @pytest.mark.asyncio
    async def test_get_booking_by_id_not_found(
        self, booking_service, mock_booking_repo
    ):
        mock_booking_repo.get_by_id.return_value = None

        with pytest.raises(NotFoundError, match="Booking not found"):
            await booking_service.get_booking_by_id("booking-999")

    @pytest.mark.asyncio
    async def test_cancel_booking_success(
        self, booking_service, mock_booking_repo, sample_booking
    ):
        mock_booking_repo.get_by_id.return_value = sample_booking

        await booking_service.cancel_booking("booking-123")

        mock_booking_repo.cancel.assert_called_once_with("booking-123")

    @pytest.mark.asyncio
    async def test_cancel_booking_empty_id(self, booking_service):
        with pytest.raises(InvalidInputError, match="Booking ID is required"):
            await booking_service.cancel_booking("")

    @pytest.mark.asyncio
    async def test_cancel_booking_not_found(self, booking_service, mock_booking_repo):
        mock_booking_repo.get_by_id.return_value = None

        with pytest.raises(NotFoundError, match="Booking not found"):
            await booking_service.cancel_booking("booking-999")

    @pytest.mark.asyncio
    async def test_get_all_bookings(
        self, booking_service, mock_booking_repo, sample_booking
    ):
        mock_booking_repo.get_all.return_value = [sample_booking]

        bookings = await booking_service.get_all_bookings()

        assert len(bookings) == 1
        assert bookings[0] == sample_booking

    @pytest.mark.asyncio
    async def test_get_bookings_by_room_id_success(
        self, booking_service, mock_booking_repo, sample_booking
    ):
        mock_booking_repo.get_by_room_id.return_value = [sample_booking]

        bookings = await booking_service.get_bookings_by_room_id("room-123")

        assert len(bookings) == 1
        mock_booking_repo.get_by_room_id.assert_called_once_with("room-123")

    @pytest.mark.asyncio
    async def test_get_bookings_by_room_id_empty_id(self, booking_service):
        with pytest.raises(InvalidInputError, match="Room ID is required"):
            await booking_service.get_bookings_by_room_id("")

    @pytest.mark.asyncio
    async def test_get_bookings_by_user_id_success(
        self, booking_service, mock_booking_repo, sample_booking
    ):
        mock_booking_repo.get_by_user_id.return_value = [sample_booking]

        bookings = await booking_service.get_bookings_by_user_id("user-123")

        assert len(bookings) == 1
        mock_booking_repo.get_by_user_id.assert_called_once_with("user-123")

    @pytest.mark.asyncio
    async def test_get_bookings_by_user_id_empty_id(self, booking_service):
        with pytest.raises(InvalidInputError, match="User ID is required"):
            await booking_service.get_bookings_by_user_id("")

    @pytest.mark.asyncio
    async def test_get_bookings_with_details_by_room_id_success(
        self,
        booking_service,
        mock_booking_repo,
        mock_room_repo,
        mock_user_repo,
        sample_booking,
        sample_room,
        sample_user,
    ):
        mock_booking_repo.get_by_room_id.return_value = [sample_booking]
        mock_room_repo.get_by_id.return_value = sample_room
        mock_user_repo.get_by_id.return_value = sample_user

        detailed_bookings = await booking_service.get_bookings_with_details_by_room_id(
            "room-123"
        )

        assert len(detailed_bookings) == 1
        assert isinstance(detailed_bookings[0], BookingWithDetails)
        assert detailed_bookings[0].user_email == "test@example.com"
        assert detailed_bookings[0].room_name == "Conference Room A"

    @pytest.mark.asyncio
    async def test_get_bookings_with_details_room_not_found(
        self, booking_service, mock_room_repo
    ):
        mock_room_repo.get_by_id.return_value = None

        with pytest.raises(NotFoundError, match="Room not found"):
            await booking_service.get_bookings_with_details_by_room_id("room-999")

    @pytest.mark.asyncio
    async def test_get_bookings_by_date_range(
        self, booking_service, mock_booking_repo, sample_booking
    ):
        mock_booking_repo.get_by_date_range.return_value = [sample_booking]

        bookings = await booking_service.get_bookings_by_date_range(
            1704067200, 1704153600
        )

        assert len(bookings) == 1
        mock_booking_repo.get_by_date_range.assert_called_once_with(
            1704067200, 1704153600
        )

    @pytest.mark.asyncio
    async def test_get_room_schedule_by_date_success(
        self,
        booking_service,
        mock_booking_repo,
        mock_room_repo,
        mock_user_repo,
        sample_booking,
        sample_room,
        sample_user,
    ):
        mock_room_repo.get_by_id.return_value = sample_room
        mock_booking_repo.get_by_room_id_and_date.return_value = [sample_booking]
        mock_user_repo.get_by_id.return_value = sample_user

        schedule = await booking_service.get_room_schedule_by_date(
            "room-123", 1704067200
        )

        assert isinstance(schedule, RoomScheduleResponse)
        assert schedule.room_id == "room-123"
        assert schedule.room_name == "Conference Room A"
        assert len(schedule.bookings) == 1
        assert isinstance(schedule.bookings[0], ScheduleSlot)

    @pytest.mark.asyncio
    async def test_get_room_schedule_empty_room_id(self, booking_service):
        with pytest.raises(InvalidInputError, match="Room ID is required"):
            await booking_service.get_room_schedule_by_date("", 1704067200)

    @pytest.mark.asyncio
    async def test_get_room_schedule_room_not_found(
        self, booking_service, mock_room_repo
    ):
        mock_room_repo.get_by_id.return_value = None

        with pytest.raises(NotFoundError, match="Room not found"):
            await booking_service.get_room_schedule_by_date("room-999", 1704067200)
