from typing import List, Optional
import uuid
import time
from app.models.models import Room
from app.repositories.rooms_repo import RoomRepository
from app.utils.errors import ApplicationError, ErrorCode


class RoomService:

    def __init__(self, room_repository: RoomRepository) -> None:
        self.room_repo: RoomRepository = room_repository

    async def add_room(self, room: Room) -> None:
        room.name = room.name.strip()
        room.location = room.location.strip()

        if not room.status:
            room.status = "Available"

        if not room.amenities:
            room.amenities = []

        exists: bool = await self.room_repo.check_room_number_exists_on_floor(
            room.room_number, room.floor
        )
        if exists:
            raise ApplicationError(ErrorCode.ROOM_ALREADY_EXISTS)

        room.id = str(uuid.uuid4())
        room.created_at = int(time.time())
        room.updated_at = int(time.time())

        await self.room_repo.create(room)

    async def get_all_rooms(self) -> List[Room]:
        rooms: List[Room] = await self.room_repo.get_all()
        return rooms if rooms else []

    async def get_room_by_id(self, room_id: str) -> Room:
        return await self.room_repo.get_by_id(room_id)

    async def update_room(self, room_id: str, update_data) -> None:
        room: Room = await self.room_repo.get_by_id(room_id)

        if update_data.name:
            room.name = update_data.name.strip()

        if update_data.capacity is not None:
            room.capacity = update_data.capacity

        if update_data.amenities is not None:
            room.amenities = update_data.amenities

        if update_data.status:
            room.status = update_data.status

        if update_data.location:
            room.location = update_data.location.strip()

        if update_data.description is not None:
            room.description = update_data.description

        room.updated_at = int(time.time())
        await self.room_repo.update(room)

    async def delete_room_by_id(self, room_id: str) -> None:
        await self.room_repo.delete_by_id(room_id)
