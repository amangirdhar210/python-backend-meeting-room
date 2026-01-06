from typing import List
import uuid
import time
from datetime import datetime
from app.models.models import (
    Booking,
    BookingWithDetails,
    RoomScheduleResponse,
    ScheduleSlot,
)
from app.repositories.bookings_repo import BookingRepository
from app.repositories.rooms_repo import RoomRepository
from app.repositories.users_repo import UserRepository
from app.utils.errors import (
    InvalidInputError,
    NotFoundError,
    RoomUnavailableError,
    TimeRangeInvalidError,
)
from app.utils.time_utils import is_time_range_valid, overlaps, is_within_booking_window
from app.config.config import settings


class BookingService:

    def __init__(
        self,
        booking_repository: BookingRepository,
        room_repository: RoomRepository,
        user_repository: UserRepository,
    ):
        self.booking_repo = booking_repository
        self.room_repo = room_repository
        self.user_repo = user_repository

    def create_booking(self, booking: Booking) -> None:
        if not booking:
            raise InvalidInputError("Booking is required")

        if not booking.user_id or not booking.room_id:
            raise InvalidInputError("User ID and Room ID are required")

        if not is_time_range_valid(booking.start_time, booking.end_time):
            raise TimeRangeInvalidError("Invalid time range")

        if not is_within_booking_window(
            booking.start_time, settings.MAX_BOOKING_DAYS_IN_FUTURE
        ):
            raise InvalidInputError(
                f"Bookings can only be made up to {settings.MAX_BOOKING_DAYS_IN_FUTURE} days in advance"
            )

        user = self.user_repo.get_by_id(booking.user_id)
        if not user:
            raise NotFoundError("User not found")

        room = self.room_repo.get_by_id(booking.room_id)
        if not room:
            raise NotFoundError("Room not found")

        existing_bookings = self.booking_repo.get_by_room_and_time(
            booking.room_id, booking.start_time, booking.end_time
        )

        for b in existing_bookings:
            if overlaps(booking.start_time, booking.end_time, b.start_time, b.end_time):
                raise RoomUnavailableError(
                    "Room is not available for the selected time slot"
                )

        booking.id = str(uuid.uuid4())
        booking.user_name = user.name
        booking.room_number = room.room_number
        booking.status = "confirmed"
        booking.created_at = int(time.time())
        booking.updated_at = int(time.time())

        self.booking_repo.create(booking)

    def get_booking_by_id(self, booking_id: str) -> Booking:
        if not booking_id:
            raise InvalidInputError("Booking ID is required")

        booking = self.booking_repo.get_by_id(booking_id)
        if not booking:
            raise NotFoundError("Booking not found")

        return booking

    def cancel_booking(self, booking_id: str) -> None:
        if not booking_id:
            raise InvalidInputError("Booking ID is required")

        booking = self.booking_repo.get_by_id(booking_id)
        if not booking:
            raise NotFoundError("Booking not found")

        self.booking_repo.cancel(booking_id)

    def get_all_bookings(self) -> List[Booking]:
        return self.booking_repo.get_all()

    def get_bookings_by_room_id(self, room_id: str) -> List[Booking]:
        if not room_id:
            raise InvalidInputError("Room ID is required")

        return self.booking_repo.get_by_room_id(room_id)

    def get_bookings_by_user_id(self, user_id: str) -> List[Booking]:
        if not user_id:
            raise InvalidInputError("User ID is required")

        return self.booking_repo.get_by_user_id(user_id)

    def get_bookings_with_details_by_room_id(
        self, room_id: str
    ) -> List[BookingWithDetails]:
        if not room_id:
            raise InvalidInputError("Room ID is required")

        bookings = self.booking_repo.get_by_room_id(room_id)
        room = self.room_repo.get_by_id(room_id)

        detailed_bookings = []
        for booking in bookings:
            try:
                user = self.user_repo.get_by_id(booking.user_id)
                detailed_bookings.append(
                    BookingWithDetails(
                        id=booking.id,
                        user_id=booking.user_id,
                        user_name=user.name,
                        room_id=booking.room_id,
                        room_number=room.room_number,
                        start_time=booking.start_time,
                        end_time=booking.end_time,
                        purpose=booking.purpose,
                        status=booking.status,
                        created_at=booking.created_at,
                        updated_at=booking.updated_at,
                        user_email=user.email,
                        room_name=room.name,
                    )
                )
            except Exception:
                continue

        return detailed_bookings

    def get_bookings_by_date_range(
        self, start_date: int, end_date: int
    ) -> List[Booking]:
        return self.booking_repo.get_by_date_range(start_date, end_date)

    def get_room_schedule_by_date(
        self, room_id: str, target_date: int
    ) -> RoomScheduleResponse:
        if not room_id:
            raise InvalidInputError("Room ID is required")

        room = self.room_repo.get_by_id(room_id)
        if not room:
            raise NotFoundError("Room not found")

        bookings = self.booking_repo.get_by_room_id_and_date(room_id, target_date)

        schedule_slots = []
        for booking in bookings:
            user_name = ""
            try:
                user = self.user_repo.get_by_id(booking.user_id)
                if user:
                    user_name = user.name
            except Exception:
                pass

            schedule_slots.append(
                ScheduleSlot(
                    start_time=datetime.fromtimestamp(booking.start_time).isoformat(),
                    end_time=datetime.fromtimestamp(booking.end_time).isoformat(),
                    is_booked=True,
                    booking_id=booking.id,
                    user_name=user_name,
                    purpose=booking.purpose,
                )
            )

        return RoomScheduleResponse(
            room_id=room.id,
            room_name=room.name,
            room_number=room.room_number,
            date=datetime.fromtimestamp(target_date).strftime("%Y-%m-%d"),
            bookings=schedule_slots,
        )
