from typing import List
from app.models.models import Booking, BookingWithDetails, RoomScheduleResponse
from app.repositories.bookings_repo import BookingRepository
from app.repositories.rooms_repo import RoomRepository
from app.repositories.users_repo import UserRepository


class BookingService:

    def __init__(
        self,
        booking_repository: BookingRepository,
        room_repository: RoomRepository,
        user_repository: UserRepository,
    ):
        pass

    def create_booking(self, booking: Booking) -> None:
        pass

    def get_booking_by_id(self, booking_id: str) -> Booking:
        pass

    def cancel_booking(self, booking_id: str) -> None:
        pass

    def get_all_bookings(self) -> List[Booking]:
        pass

    def get_bookings_by_room_id(self, room_id: str) -> List[Booking]:
        pass

    def get_bookings_by_user_id(self, user_id: str) -> List[Booking]:
        pass

    def get_bookings_with_details_by_room_id(
        self, room_id: str
    ) -> List[BookingWithDetails]:
        pass

    def get_bookings_by_date_range(
        self, start_date: int, end_date: int
    ) -> List[Booking]:
        pass

    def get_room_schedule_by_date(
        self, room_id: str, target_date: int
    ) -> RoomScheduleResponse:
        pass
