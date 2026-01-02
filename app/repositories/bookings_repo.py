from typing import List
from app.models.models import Booking


class BookingRepository:

    def __init__(self, dynamodb_client, table_name: str):
        pass

    def create(self, booking: Booking) -> None:
        pass

    def get_by_id(self, booking_id: str) -> Booking:
        pass

    def get_all(self) -> List[Booking]:
        pass

    def get_by_room_and_time(
        self, room_id: str, start_time: int, end_time: int
    ) -> List[Booking]:
        pass

    def get_by_room_id(self, room_id: str) -> List[Booking]:
        pass

    def get_by_user_id(self, user_id: str) -> List[Booking]:
        pass

    def cancel(self, booking_id: str) -> None:
        pass

    def get_by_date_range(self, start_date: int, end_date: int) -> List[Booking]:
        pass

    def get_by_room_id_and_date(self, room_id: str, date: int) -> List[Booking]:
        pass
