from typing import List, Optional
import uuid
import time
from app.models.models import Room
from app.repositories.rooms_repo import RoomRepository
from app.repositories.bookings_repo import BookingRepository
from app.utils.errors import ApplicationError, ErrorCode


class RoomService:

    def __init__(self, room_repository: RoomRepository, booking_repository: BookingRepository = None) -> None:
        self.room_repo: RoomRepository = room_repository
        self.booking_repo: BookingRepository = booking_repository

    def is_room_occupied(self, room_id: str, bookings: List = None) -> bool:
        if not bookings or not self.booking_repo:
            return False
        
        current_time = int(time.time())
        for booking in bookings:
            if (booking.room_id == room_id and 
                booking.status.lower() == "confirmed" and
                booking.start_time <= current_time < booking.end_time):
                return True
        return False

    async def add_room(self, room: Room) -> None:
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
        if not rooms:
            return []
        
        if self.booking_repo:
            current_time = int(time.time())
            all_bookings = await self.booking_repo.get_all()
            for room in rooms:
                room.is_occupied = self.is_room_occupied(room.id, all_bookings)
        
        return rooms

    async def get_room_by_id(self, room_id: str) -> Room:
        room = await self.room_repo.get_by_id(room_id)
        
        if self.booking_repo:
            current_time = int(time.time())
            room_bookings = await self.booking_repo.get_by_room_id(room_id)
            room.is_occupied = self.is_room_occupied(room_id, room_bookings)
        
        return room

    async def update_room(self, room_id: str, update_data) -> None:
        room: Room = await self.room_repo.get_by_id(room_id)

        update_dict = update_data.model_dump(exclude_unset=True)
        
        for field, value in update_dict.items():
            setattr(room, field, value)

        room.updated_at = int(time.time())
        await self.room_repo.update(room)

    async def delete_room_by_id(self, room_id: str) -> None:
        await self.room_repo.delete_by_id(room_id)
