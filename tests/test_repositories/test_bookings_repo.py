import pytest
import asyncio
from unittest.mock import MagicMock
from app.repositories.bookings_repo import BookingRepository
from app.models.models import Booking
from app.utils.errors import NotFoundError


class TestBookingRepository:

    @pytest.fixture
    def mock_table(self):
        table = MagicMock()
        table.table_name = "TestTable"
        return table

    @pytest.fixture
    def booking_repo(self, mock_table):
        mock_dynamodb = MagicMock()
        mock_dynamodb.Table.return_value = mock_table
        return BookingRepository(mock_dynamodb, "TestTable")

    @pytest.fixture
    def sample_booking(self):
        import time

        current = int(time.time())
        return Booking(
            id="booking-1234567890",
            user_id="user-123",
            user_name="John Doe",
            room_id="room-456",
            room_number=101,
            start_time=current + 3600,
            end_time=current + 7200,
            purpose="Team meeting",
            status="confirmed",
            created_at=current,
            updated_at=current,
        )

    def test_create_booking_success(self, booking_repo, mock_table, sample_booking):
        asyncio.run(booking_repo.create(sample_booking))

        mock_table.put_item.assert_called_once()
        call_args = mock_table.put_item.call_args[1]
        item = call_args["Item"]

        assert item["PK"] == "BOOKING"
        assert item["SK"] == "BOOKING#booking-1234567890"
        assert item["ID"] == "booking-1234567890"
        assert item["UserID"] == "user-123"
        assert item["RoomID"] == "room-456"
        assert item["Purpose"] == "Team meeting"
        assert item["Status"] == "confirmed"

    def test_get_by_id_success(self, booking_repo, mock_table):
        mock_table.get_item.return_value = {
            "Item": {
                "PK": "BOOKING",
                "SK": "BOOKING#booking-123",
                "ID": "booking-123",
                "UserID": "user-456",
                "UserName": "Jane Doe",
                "RoomID": "room-789",
                "RoomNumber": 102,
                "StartTime": 1704800000,
                "EndTime": 1704803600,
                "Purpose": "Interview",
                "Status": "confirmed",
                "CreatedAt": 1704700000,
                "UpdatedAt": 1704700000,
            }
        }

        booking = asyncio.run(booking_repo.get_by_id("booking-123"))

        assert booking.id == "booking-123"
        assert booking.user_id == "user-456"
        assert booking.room_id == "room-789"
        assert booking.purpose == "Interview"

    def test_get_by_id_not_found(self, booking_repo, mock_table):
        mock_table.get_item.return_value = {}

        with pytest.raises(NotFoundError, match="Booking not found"):
            asyncio.run(booking_repo.get_by_id("nonexistent-booking"))

    def test_get_all_bookings_success(self, booking_repo, mock_table):
        mock_table.query.return_value = {
            "Items": [
                {
                    "ID": "booking-1",
                    "UserID": "user-1",
                    "UserName": "User One",
                    "RoomID": "room-1",
                    "RoomNumber": 101,
                    "StartTime": 1704800000,
                    "EndTime": 1704803600,
                    "Purpose": "Meeting",
                    "Status": "confirmed",
                    "CreatedAt": 1704700000,
                    "UpdatedAt": 1704700000,
                },
                {
                    "ID": "booking-2",
                    "UserID": "user-2",
                    "UserName": "User Two",
                    "RoomID": "room-2",
                    "RoomNumber": 102,
                    "StartTime": 1704810000,
                    "EndTime": 1704813600,
                    "Purpose": "Training",
                    "Status": "confirmed",
                    "CreatedAt": 1704710000,
                    "UpdatedAt": 1704710000,
                },
            ]
        }

        bookings = asyncio.run(booking_repo.get_all())

        assert len(bookings) == 2
        assert bookings[0].id == "booking-1"
        assert bookings[1].purpose == "Training"

    def test_get_all_bookings_empty(self, booking_repo, mock_table):
        mock_table.query.return_value = {}

        bookings = asyncio.run(booking_repo.get_all())

        assert bookings == []

    def test_get_by_user_id_success(self, booking_repo, mock_table):
        mock_table.query.return_value = {
            "Items": [
                {
                    "ID": "booking-1",
                    "UserID": "user-123",
                    "UserName": "John Doe",
                    "RoomID": "room-1",
                    "RoomNumber": 101,
                    "StartTime": 1704800000,
                    "EndTime": 1704803600,
                    "Purpose": "Meeting",
                    "Status": "confirmed",
                    "CreatedAt": 1704700000,
                    "UpdatedAt": 1704700000,
                }
            ]
        }

        bookings = asyncio.run(booking_repo.get_by_user_id("user-123"))

        assert len(bookings) == 1
        assert bookings[0].user_id == "user-123"

    def test_get_by_room_id_success(self, booking_repo, mock_table):
        mock_table.query.return_value = {
            "Items": [
                {
                    "ID": "booking-1",
                    "UserID": "user-1",
                    "UserName": "User One",
                    "RoomID": "room-456",
                    "RoomNumber": 101,
                    "StartTime": 1704800000,
                    "EndTime": 1704803600,
                    "Purpose": "Meeting",
                    "Status": "confirmed",
                    "CreatedAt": 1704700000,
                    "UpdatedAt": 1704700000,
                }
            ]
        }

        bookings = asyncio.run(booking_repo.get_by_room_id("room-456"))

        assert len(bookings) == 1
        assert bookings[0].room_id == "room-456"

    def test_get_by_room_and_time_success(self, booking_repo, mock_table):
        mock_table.query.return_value = {
            "Items": [
                {
                    "ID": "booking-1",
                    "UserID": "user-1",
                    "UserName": "User One",
                    "RoomID": "room-456",
                    "RoomNumber": 101,
                    "StartTime": 1704800000,
                    "EndTime": 1704803600,
                    "Purpose": "Meeting",
                    "Status": "confirmed",
                    "CreatedAt": 1704700000,
                    "UpdatedAt": 1704700000,
                }
            ]
        }

        bookings = asyncio.run(
            booking_repo.get_by_room_and_time("room-456", 1704799000, 1704804000)
        )

        assert len(bookings) == 1
        assert bookings[0].room_id == "room-456"

    def test_cancel_booking_success(self, booking_repo, mock_table):
        asyncio.run(booking_repo.cancel("booking-123"))

        mock_table.delete_item.assert_called_once()
        call_args = mock_table.delete_item.call_args[1]

        assert call_args["Key"]["PK"] == "BOOKING"
        assert call_args["Key"]["SK"] == "BOOKING#booking-123"

    def test_delete_by_user_id_success(self, booking_repo, mock_table):
        mock_table.query.return_value = {
            "Items": [
                {"PK": "BOOKING", "SK": "BOOKING#booking-1"},
                {"PK": "BOOKING", "SK": "BOOKING#booking-2"},
            ]
        }

        result = asyncio.run(booking_repo.delete_by_user_id("user-123"))

        assert result == 2
        assert booking_repo.dynamodb.meta.client.batch_write_item.called

    def test_get_by_room_id_and_date_success(self, booking_repo, mock_table):
        mock_table.query.return_value = {
            "Items": [
                {
                    "ID": "booking-1",
                    "UserID": "user-1",
                    "UserName": "User One",
                    "RoomID": "room-456",
                    "RoomNumber": 101,
                    "StartTime": 1704800000,
                    "EndTime": 1704803600,
                    "Purpose": "Meeting",
                    "Status": "confirmed",
                    "CreatedAt": 1704700000,
                    "UpdatedAt": 1704700000,
                }
            ]
        }

        bookings = asyncio.run(
            booking_repo.get_by_room_id_and_date("room-456", 1704758400)
        )

        assert len(bookings) == 1
        assert bookings[0].room_id == "room-456"

    def test_get_by_date_range_success(self, booking_repo, mock_table):
        mock_table.query.return_value = {
            "Items": [
                {
                    "ID": "booking-1",
                    "UserID": "user-1",
                    "UserName": "User One",
                    "RoomID": "room-1",
                    "RoomNumber": 101,
                    "StartTime": 1704800000,
                    "EndTime": 1704803600,
                    "Purpose": "Meeting",
                    "Status": "confirmed",
                    "CreatedAt": 1704700000,
                    "UpdatedAt": 1704700000,
                }
            ]
        }

        bookings = asyncio.run(booking_repo.get_by_date_range(1704758400, 1704844800))

        assert len(bookings) == 1
