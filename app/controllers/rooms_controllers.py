from fastapi import APIRouter, Depends, Query
from typing import Optional
from app.services.rooms_service import RoomService
from app.models.models import Room


rooms_router = APIRouter()


@rooms_router.post("/rooms")
def add_room(room: Room):
    pass


@rooms_router.get("/rooms")
def get_all_rooms():
    pass


@rooms_router.get("/rooms/{id}")
def get_room_by_id(id: str):
    pass


@rooms_router.delete("/rooms/{id}/delete")
def delete_room_by_id(id: str):
    pass


@rooms_router.get("/rooms/search")
def search_rooms(
    min_capacity: int = Query(default=0),
    max_capacity: int = Query(default=0),
    floor: Optional[int] = Query(default=None),
    start_time: Optional[int] = Query(default=None),
    end_time: Optional[int] = Query(default=None),
):
    pass


@rooms_router.post("/rooms/check-availability")
def check_availability(room_id: str, start_time: int, end_time: int):
    pass


def get_available_slots(room_id: str, date: int, slot_duration: int):
    pass
