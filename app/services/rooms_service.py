from typing import List, Optional, Tuple
from app.models.models import Room, Booking, TimeSlot
from app.repositories.rooms_repo import RoomRepository


class RoomService:

    def __init__(self, room_repository: RoomRepository):
        pass

    def add_room(self, room: Room) -> None:
        pass

    def get_all_rooms(self) -> List[Room]:
        pass

    def get_room_by_id(self, room_id: str) -> Room:
        pass

    def delete_room_by_id(self, room_id: str) -> None:
        pass

    def search_rooms(
        self,
        min_capacity: int,
        max_capacity: int,
        floor: Optional[int],
        start_time: Optional[int],
        end_time: Optional[int],
    ) -> List[Room]:
        pass

    def check_availability(
        self, room_id: str, start_time: int, end_time: int
    ) -> Tuple[bool, List[Booking]]:
        pass

    def get_available_slots(
        self, room_id: str, date: int, slot_duration: int
    ) -> List[TimeSlot]:
        pass
