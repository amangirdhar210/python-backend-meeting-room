from fastapi import APIRouter, Depends, Query, Request
from typing import List
from app.models.models import Booking
from app.models.pydantic_models import (
    CreateBookingRequest,
    BookingDTO,
    GenericResponse,
    RoomScheduleResponse as RoomScheduleDTO,
    ScheduleSlotDTO,
)
from app.services.bookings_service import BookingService
from app.dependencies.dependencies import get_booking_service, BookingServiceInstance
from app.middleware.auth_middleware import set_current_user, require_admin_state
from app.utils.errors import (
    InvalidInputError,
    NotFoundError,
    RoomUnavailableError,
    TimeRangeInvalidError,
)


bookings_router: APIRouter = APIRouter(
    prefix="/api",
    tags=["Bookings"],
    dependencies=[Depends(set_current_user)],
)


@bookings_router.post("/bookings", response_model=GenericResponse, status_code=201)
async def create_booking(
    req: Request,
    request: CreateBookingRequest,
    booking_service: BookingServiceInstance,
) -> GenericResponse:
    booking: Booking = Booking(
        user_id=req.state.user.get("user_id"),
        room_id=request.room_id,
        start_time=request.start_time,
        end_time=request.end_time,
        purpose=request.purpose,
    )
    await booking_service.create_booking(booking)
    return GenericResponse(message="booking created successfully")


@bookings_router.get("/bookings/{booking_id}", response_model=BookingDTO)
async def get_booking_by_id(
    req: Request,
    booking_id: str,
    booking_service: BookingServiceInstance,
) -> BookingDTO:
    booking: Booking = await booking_service.get_booking_by_id(booking_id)
    return BookingDTO(**{**booking.model_dump(), "status": booking.status.lower()})


@bookings_router.delete("/bookings/{id}", response_model=GenericResponse)
async def cancel_booking(
    req: Request,
    id: str,
    booking_service: BookingServiceInstance,
) -> GenericResponse:
    await booking_service.cancel_booking(id)
    return GenericResponse(message="booking cancelled successfully")


@bookings_router.get("/bookings", response_model=List[BookingDTO])
async def get_all_bookings(
    req: Request,
    booking_service: BookingServiceInstance,
) -> List[BookingDTO]:
    if req.state.user.get("role") == "admin":
        bookings: List[Booking] = await booking_service.get_all_bookings()
    else:
        user_id: str = req.state.user.get("user_id")
        bookings = await booking_service.get_bookings_by_user_id(user_id)
    return [
        BookingDTO(**{**b.model_dump(), "status": b.status.lower()}) for b in bookings
    ]


@bookings_router.get("/rooms/{room_id}/bookings", response_model=List[BookingDTO])
async def get_bookings_by_room_id(
    req: Request,
    room_id: str,
    booking_service: BookingServiceInstance,
) -> List[BookingDTO]:
    bookings: List[Booking] = await booking_service.get_bookings_by_room_id(room_id)
    return [
        BookingDTO(**{**b.model_dump(), "status": b.status.lower()}) for b in bookings
    ]


@bookings_router.get("/bookings/my", response_model=List[BookingDTO])
async def get_bookings_by_user_id(
    req: Request,
    booking_service: BookingServiceInstance,
) -> List[BookingDTO]:
    user_id: str = req.state.user.get("user_id")
    bookings: List[Booking] = await booking_service.get_bookings_by_user_id(user_id)
    return [
        BookingDTO(**{**b.model_dump(), "status": b.status.lower()}) for b in bookings
    ]


@bookings_router.get("/rooms/{room_id}/schedule", response_model=RoomScheduleDTO)
async def get_room_schedule_by_date(
    req: Request,
    room_id: str,
    booking_service: BookingServiceInstance,
    date: str = Query(..., description="Date in YYYY-MM-DD format"),
) -> RoomScheduleDTO:
    try:
        from datetime import datetime, timezone

        date_obj = datetime.strptime(date, "%Y-%m-%d")
        unix_timestamp = int(date_obj.replace(tzinfo=timezone.utc).timestamp())
    except (ValueError, AttributeError):
        raise InvalidInputError("Invalid date format. Use YYYY-MM-DD")

    schedule = await booking_service.get_room_schedule_by_date(room_id, unix_timestamp)

    return RoomScheduleDTO(
        room_id=schedule.room_id,
        room_name=schedule.room_name,
        room_number=schedule.room_number,
        date=schedule.date,
        bookings=[ScheduleSlotDTO(**slot.model_dump()) for slot in schedule.bookings],
    )
