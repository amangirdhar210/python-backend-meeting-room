from fastapi import APIRouter, Depends, Query, Request
from typing import Optional, List
from app.models.models import Room
from app.models.pydantic_models import (
    AddRoomRequest,
    UpdateRoomRequest,
    RoomDTO,
    GenericResponse,
)
from app.services.rooms_service import RoomService
from app.dependencies.dependencies import get_room_service, RoomServiceInstance
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
    room_service: RoomServiceInstance,
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


@rooms_router.get("/rooms", response_model=List[RoomDTO], dependencies=[])
async def get_all_rooms(
    room_service: RoomServiceInstance,
) -> List[RoomDTO]:
    rooms: List[Room] = await room_service.get_all_rooms()
    return [RoomDTO(**{**r.model_dump(), "status": r.status.lower()}) for r in rooms]


@rooms_router.get("/rooms/{id}", response_model=RoomDTO)
async def get_room_by_id(
    req: Request,
    id: str,
    room_service: RoomServiceInstance,
) -> RoomDTO:
    room: Room = await room_service.get_room_by_id(id)
    return RoomDTO(**{**room.model_dump(), "status": room.status.lower()})


@rooms_router.put(
    "/rooms/{id}",
    response_model=GenericResponse,
    dependencies=[Depends(require_admin_state)],
)
async def update_room(
    req: Request,
    id: str,
    request: UpdateRoomRequest,
    room_service: RoomServiceInstance,
) -> GenericResponse:
    await room_service.update_room(id, request)
    return GenericResponse(message="room updated successfully")


@rooms_router.delete(
    "/rooms/{id}",
    response_model=GenericResponse,
    dependencies=[Depends(require_admin_state)],
)
async def delete_room_by_id(
    req: Request,
    id: str,
    room_service: RoomServiceInstance,
) -> GenericResponse:
    await room_service.delete_room_by_id(id)
    return GenericResponse(message="room deleted successfully")
