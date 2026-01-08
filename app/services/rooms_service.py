from typing import List, Optional
import uuid
import time
from app.models.models import Room
from app.repositories.rooms_repo import RoomRepository
from app.utils.errors import InvalidInputError, NotFoundError, ConflictError


class RoomService:

    def __init__(self, room_repository: RoomRepository) -> None:
        self.room_repo: RoomRepository = room_repository

    async def add_room(self, room: Room) -> None:
        if not room:
            raise InvalidInputError("Room is required")

        room.name = room.name.strip()
        room.location = room.location.strip()

        if (
            not room.name
            or room.capacity <= 0
            or not room.location
            or room.room_number <= 0
            or room.floor < 0
        ):
            raise InvalidInputError("Invalid room data")

        if not room.status:
            room.status = "Available"

        if not room.amenities:
            room.amenities = []

        exists: bool = await self.room_repo.check_room_number_exists_on_floor(
            room.room_number, room.floor
        )
        if exists:
            raise ConflictError("Room number already exists on this floor")

        room.id = str(uuid.uuid4())
        room.created_at = int(time.time())
        room.updated_at = int(time.time())

        await self.room_repo.create(room)

    async def get_all_rooms(self) -> List[Room]:
        rooms: List[Room] = await self.room_repo.get_all()
        if not rooms:
            raise NotFoundError("No rooms found")
        return rooms

    async def get_room_by_id(self, room_id: str) -> Room:
        if not room_id:
            raise InvalidInputError("Room ID is required")

        room = await self.room_repo.get_by_id(room_id)
        if not room:
            raise NotFoundError("Room not found")
        return room

    async def delete_room_by_id(self, room_id: str) -> None:
        if not room_id:
            raise InvalidInputError("Room ID is required")
        await self.room_repo.delete_by_id(room_id)

    async def search_rooms(
        self,
        min_capacity: int,
        max_capacity: int,
        floor: Optional[int],
        start_time: Optional[int],
        end_time: Optional[int],
    ) -> List[Room]:
        rooms: List[Room] = await self.room_repo.search_with_filters(
            min_capacity, max_capacity, floor
        )
        return rooms

    # def check_availability(
    #     self, room_id: str, start_time: int, end_time: int
    # ) -> Tuple[bool, List[Booking]]:
    #     if not room_id:
    #         raise InvalidInputError("Room ID is required")

    #     room = self.room_repo.get_by_id(room_id)
    #     if not room:
    #         raise NotFoundError("Room not found")

    #     return True, []

    # def get_available_slots(
    #     self, room_id: str, date: int, slot_duration: int
    # ) -> List[TimeSlot]:
    #     if not room_id or slot_duration <= 0:
    #         raise InvalidInputError("Invalid input")

    #     room = self.room_repo.get_by_id(room_id)
    #     if not room:
    #         raise NotFoundError("Room not found")

    #     return []
