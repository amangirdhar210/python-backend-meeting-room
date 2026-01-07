from fastapi import APIRouter, Depends, Query
from typing import Optional, List, Dict, Any
from app.services.rooms_service import RoomService
from app.models.models import Room
from app.models.pydantic_models import AddRoomRequest, RoomDTO, GenericResponse
from app.utils.dependencies import get_room_service
from app.utils.auth_middleware import require_admin, require_user
from app.utils.errors import InvalidInputError, NotFoundError, ConflictError


rooms_router: APIRouter = APIRouter(prefix="/api", tags=["Rooms"])


@rooms_router.post("/rooms", response_model=GenericResponse, status_code=201)
async def add_room(
    request: AddRoomRequest,
    room_service: RoomService = Depends(get_room_service),
    current_user: Dict[str, Any] = Depends(require_admin),
) -> GenericResponse:
    room: Room = Room(
        id="",
        name=request.name,
        room_number=request.room_number,
        capacity=request.capacity,
        floor=request.floor,
        amenities=request.amenities,
        status=request.status or "available",
        location=request.location,
        description=request.description,
        created_at=0,
        updated_at=0,
    )
    room_service.add_room(room)
    return GenericResponse(message="room added successfully")


@rooms_router.get("/rooms", response_model=List[RoomDTO])
async def get_all_rooms(
    room_service: RoomService = Depends(get_room_service),
    current_user: Dict[str, Any] = Depends(require_user),
) -> List[RoomDTO]:
    rooms: List[Room] = room_service.get_all_rooms()
    return [
        RoomDTO(
            id=r.id,
            name=r.name,
            room_number=r.room_number,
            capacity=r.capacity,
            floor=r.floor,
            amenities=r.amenities,
            status=r.status,
            location=r.location,
            description=r.description,
            created_at=r.created_at,
            updated_at=r.updated_at,
        )
        for r in rooms
    ]


@rooms_router.get("/rooms/{id}", response_model=RoomDTO)
async def get_room_by_id(
    id: str,
    room_service: RoomService = Depends(get_room_service),
    current_user: Dict[str, Any] = Depends(require_user),
) -> RoomDTO:
    room: Room = room_service.get_room_by_id(id)
    return RoomDTO(
        id=room.id,
        name=room.name,
        room_number=room.room_number,
        capacity=room.capacity,
        floor=room.floor,
        amenities=room.amenities,
        status=room.status,
        location=room.location,
        description=room.description,
        created_at=room.created_at,
        updated_at=room.updated_at,
    )


@rooms_router.delete("/rooms/{id}", response_model=GenericResponse)
async def delete_room_by_id(
    id: str,
    room_service: RoomService = Depends(get_room_service),
    current_user: Dict[str, Any] = Depends(require_admin),
) -> GenericResponse:
    room_service.delete_room_by_id(id)
    return GenericResponse(message="room deleted successfully")


@rooms_router.get("/rooms/search", response_model=List[RoomDTO])
async def search_rooms(
    min_capacity: int = Query(default=0),
    max_capacity: int = Query(default=0),
    floor: Optional[int] = Query(default=None),
    start_time: Optional[int] = Query(default=None),
    end_time: Optional[int] = Query(default=None),
    room_service: RoomService = Depends(get_room_service),
    current_user: Dict[str, Any] = Depends(require_user),
) -> List[RoomDTO]:
    rooms: List[Room] = room_service.search_rooms(
        min_capacity, max_capacity, floor, start_time, end_time
    )
    return [
        RoomDTO(
            id=r.id,
            name=r.name,
            room_number=r.room_number,
            capacity=r.capacity,
            floor=r.floor,
            amenities=r.amenities,
            status=r.status,
            location=r.location,
            description=r.description,
            created_at=r.created_at,
            updated_at=r.updated_at,
        )
        for r in rooms
    ]
