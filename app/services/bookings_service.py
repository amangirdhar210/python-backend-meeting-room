from typing import List
import uuid
import time
from app.models.models import (
    Booking,
    BookingWithDetails,
    RoomScheduleResponse,
    ScheduleSlot,
    User,
    Room,
)
from app.repositories.bookings_repo import BookingRepository
from app.repositories.rooms_repo import RoomRepository
from app.repositories.users_repo import UserRepository
from app.utils.errors import ApplicationError, ErrorCode
from app.utils.time_utils import is_time_range_valid, overlaps, is_within_booking_window
from app.config.config import settings


class BookingService:

    def __init__(
        self,
        booking_repository: BookingRepository,
        room_repository: RoomRepository,
        user_repository: UserRepository,
    ) -> None:
        self.booking_repo: BookingRepository = booking_repository
        self.room_repo: RoomRepository = room_repository
        self.user_repo: UserRepository = user_repository

    async def create_booking(self, booking: Booking) -> None:
        if not is_time_range_valid(booking.start_time, booking.end_time):
            raise ApplicationError(ErrorCode.INVALID_TIME_RANGE)

        if not is_within_booking_window(
            booking.start_time, settings.MAX_BOOKING_DAYS_IN_FUTURE
        ):
            raise ApplicationError(
                ErrorCode.BOOKING_TOO_FAR,
                message=f"Bookings can only be made up to {settings.MAX_BOOKING_DAYS_IN_FUTURE} days in advance",
            )

        user = await self.user_repo.get_by_id(booking.user_id)
        room = await self.room_repo.get_by_id(booking.room_id)

        existing_bookings: List[Booking] = await self.booking_repo.get_by_room_and_time(
            booking.room_id, booking.start_time, booking.end_time
        )

        for b in existing_bookings:
            if overlaps(booking.start_time, booking.end_time, b.start_time, b.end_time):
                raise ApplicationError(ErrorCode.ROOM_UNAVAILABLE)

        booking.id = str(uuid.uuid4())
        booking.user_name = user.name
        booking.room_number = room.room_number
        booking.status = "confirmed"
        booking.created_at = int(time.time())
        booking.updated_at = int(time.time())

        await self.booking_repo.create(booking)

    async def get_booking_by_id(self, booking_id: str) -> Booking:
        return await self.booking_repo.get_by_id(booking_id)

    async def cancel_booking(self, booking_id: str, user_id: str, user_role: str) -> None:
        booking: Booking = await self.booking_repo.get_by_id(booking_id)
        
        if user_role != "admin" and booking.user_id != user_id:
            raise ApplicationError(
                ErrorCode.INSUFFICIENT_PERMISSIONS,
                message="You can only cancel your own bookings"
            )
        
        await self.booking_repo.cancel(booking_id)

    async def get_all_bookings(self) -> List[Booking]:
        return await self.booking_repo.get_all()

    async def get_bookings_by_room_id(self, room_id: str) -> List[Booking]:
        return await self.booking_repo.get_by_room_id(room_id)

    async def get_bookings_by_user_id(self, user_id: str) -> List[Booking]:
        return await self.booking_repo.get_by_user_id(user_id)

    async def get_bookings_with_details_by_room_id(
        self, room_id: str
    ) -> List[BookingWithDetails]:
        bookings: List[Booking] = await self.booking_repo.get_by_room_id(room_id)
        room = await self.room_repo.get_by_id(room_id)

        detailed_bookings: List[BookingWithDetails] = []
        for booking in bookings:
            user: User = await self.user_repo.get_by_id(booking.user_id)
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

        return detailed_bookings

    async def get_bookings_by_date_range(
        self, start_date: int, end_date: int
    ) -> List[Booking]:
        return await self.booking_repo.get_by_date_range(start_date, end_date)

    async def get_room_schedule_by_date(
        self, room_id: str, date_str: str
    ) -> RoomScheduleResponse:
        from datetime import datetime, timezone

        date_obj = datetime.strptime(date_str, "%Y-%m-%d")
        target_date = int(date_obj.replace(tzinfo=timezone.utc).timestamp())

        room = await self.room_repo.get_by_id(room_id)

        bookings: List[Booking] = await self.booking_repo.get_by_room_id_and_date(
            room_id, target_date
        )

        schedule_slots: List[ScheduleSlot] = []
        for booking in bookings:
            user: User = await self.user_repo.get_by_id(booking.user_id)
            user_name: str = user.name

            schedule_slots.append(
                ScheduleSlot(
                    start_time=booking.start_time,
                    end_time=booking.end_time,
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
            date=target_date,
            bookings=schedule_slots,
        )
