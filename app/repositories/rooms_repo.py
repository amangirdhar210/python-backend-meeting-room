from typing import Optional, List
from app.models.models import Room


class RoomRepository:

    def __init__(self, dynamodb_client, table_name: str):
        pass

    def create(self, room: Room) -> None:
        pass

    def get_all(self) -> List[Room]:
        pass

    def get_by_id(self, room_id: str) -> Optional[Room]:
        pass

    def delete_by_id(self, room_id: str) -> None:
        pass

    def update_availability(self, room_id: str, status: str) -> None:
        pass

    def search_with_filters(
        self, min_capacity: int, max_capacity: int, floor: Optional[int]
    ) -> List[Room]:
        pass

    def check_room_number_exists_on_floor(self, room_number: int, floor: int) -> bool:
        pass
