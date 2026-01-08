from fastapi import APIRouter, Depends, Query, Request
from typing import Optional, List
from app.models.models import Room
from app.models.pydantic_models import AddRoomRequest, RoomDTO, GenericResponse
from app.services.rooms_service import RoomService
from app.dependencies.dependencies import get_room_service
from app.middleware.auth_middleware import set_current_user, require_admin_state
from app.utils.errors import InvalidInputError, NotFoundError, ConflictError


rooms_router: APIRouter = APIRouter(
    prefix="/api",
    tags=["Rooms"],
    dependencies=[Depends(set_current_user)],
)


@rooms_router.post(
    "/rooms",
    response_model=GenericResponse,
    status_code=201,
    dependencies=[Depends(require_admin_state)],
)
async def add_room(
    req: Request,
    request: AddRoomRequest,
    room_service: RoomService = Depends(get_room_service),
) -> GenericResponse:
    room: Room = Room(
        name=request.name,
        room_number=request.room_number,
        capacity=request.capacity,
        floor=request.floor,
        amenities=request.amenities,
        status=request.status or "available",
        location=request.location,
        description=request.description,
    )
    await room_service.add_room(room)
    return GenericResponse(message="room added successfully")


@rooms_router.get("/rooms", response_model=List[RoomDTO])
async def get_all_rooms(
    req: Request,
    room_service: RoomService = Depends(get_room_service),
) -> List[RoomDTO]:
    rooms: List[Room] = await room_service.get_all_rooms()
    return [RoomDTO(**r.model_dump()) for r in rooms]


@rooms_router.get("/rooms/{id}", response_model=RoomDTO)
async def get_room_by_id(
    req: Request,
    id: str,
    room_service: RoomService = Depends(get_room_service),
) -> RoomDTO:
    room: Room = await room_service.get_room_by_id(id)
    return RoomDTO(**room.model_dump())


@rooms_router.delete(
    "/rooms/{id}",
    response_model=GenericResponse,
    dependencies=[Depends(require_admin_state)],
)
async def delete_room_by_id(
    req: Request,
    id: str,
    room_service: RoomService = Depends(get_room_service),
) -> GenericResponse:
    await room_service.delete_room_by_id(id)
    return GenericResponse(message="room deleted successfully")


@rooms_router.get("/rooms/search", response_model=List[RoomDTO])
async def search_rooms(
    req: Request,
    min_capacity: int = Query(default=0),
    max_capacity: int = Query(default=0),
    floor: Optional[int] = Query(default=None),
    start_time: Optional[int] = Query(default=None),
    end_time: Optional[int] = Query(default=None),
    room_service: RoomService = Depends(get_room_service),
) -> List[RoomDTO]:
    rooms: List[Room] = await room_service.search_rooms(
        min_capacity, max_capacity, floor, start_time, end_time
    )
    return [RoomDTO(**r.model_dump()) for r in rooms]
