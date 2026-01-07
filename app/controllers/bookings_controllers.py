from fastapi import APIRouter, Depends, Query
from typing import List, Dict, Any
from datetime import datetime
from app.services.bookings_service import BookingService
from app.models.models import Booking
from app.models.pydantic_models import (
    CreateBookingRequest,
    BookingDTO,
    GenericResponse,
    RoomScheduleResponse,
)
from app.utils.dependencies import get_booking_service
from app.utils.auth_middleware import require_user, require_admin
from app.utils.errors import (
    InvalidInputError,
    NotFoundError,
    RoomUnavailableError,
    TimeRangeInvalidError,
)


bookings_router: APIRouter = APIRouter(prefix="/api", tags=["Bookings"])


@bookings_router.post("/bookings", response_model=GenericResponse, status_code=201)
async def create_booking(
    request: CreateBookingRequest,
    booking_service: BookingService = Depends(get_booking_service),
    current_user: Dict[str, Any] = Depends(require_user),
) -> GenericResponse:
    booking: Booking = Booking(
        id="",
        user_id=current_user.get("user_id"),
        user_name="",
        room_id=request.room_id,
        room_number=0,
        start_time=request.start_time,
        end_time=request.end_time,
        purpose=request.purpose,
        status="",
        created_at=0,
        updated_at=0,
    )
    booking_service.create_booking(booking)
    return GenericResponse(message="booking created successfully")


@bookings_router.get("/bookings/{booking_id}", response_model=BookingDTO)
async def get_booking_by_id(
    booking_id: str,
    booking_service: BookingService = Depends(get_booking_service),
    current_user: Dict[str, Any] = Depends(require_user),
) -> BookingDTO:
    booking: Booking = booking_service.get_booking_by_id(booking_id)
    return BookingDTO(**booking.model_dump())


@bookings_router.delete("/bookings/{id}", response_model=GenericResponse)
async def cancel_booking(
    id: str,
    booking_service: BookingService = Depends(get_booking_service),
    current_user: Dict[str, Any] = Depends(require_user),
) -> GenericResponse:
    booking_service.cancel_booking(id)
    return GenericResponse(message="booking cancelled successfully")


@bookings_router.get("/bookings", response_model=List[BookingDTO])
async def get_all_bookings(
    booking_service: BookingService = Depends(get_booking_service),
    current_user: Dict[str, Any] = Depends(require_user),
) -> List[BookingDTO]:
    if current_user.get("role") == "admin":
        bookings: List[Booking] = booking_service.get_all_bookings()
    else:
        user_id: Any = current_user.get("user_id")
        bookings = booking_service.get_bookings_by_user_id(user_id)
    return [BookingDTO(**b.model_dump()) for b in bookings]


@bookings_router.get("/rooms/{room_id}/bookings", response_model=List[BookingDTO])
async def get_bookings_by_room_id(
    room_id: str,
    booking_service: BookingService = Depends(get_booking_service),
    current_user: Dict[str, Any] = Depends(require_user),
) -> List[BookingDTO]:
    bookings: List[Booking] = booking_service.get_bookings_by_room_id(room_id)
    return [BookingDTO(**b.model_dump()) for b in bookings]


@bookings_router.get("/bookings/my", response_model=List[BookingDTO])
async def get_bookings_by_user_id(
    booking_service: BookingService = Depends(get_booking_service),
    current_user: Dict[str, Any] = Depends(require_user),
) -> List[BookingDTO]:
    user_id: Any = current_user.get("user_id")
    bookings: List[Booking] = booking_service.get_bookings_by_user_id(user_id)
    return [BookingDTO(**b.model_dump()) for b in bookings]


@bookings_router.get("/rooms/{room_id}/schedule", response_model=RoomScheduleResponse)
async def get_room_schedule_by_date(
    room_id: str,
    date: str = Query(..., description="Date in YYYY-MM-DD format"),
    booking_service: BookingService = Depends(get_booking_service),
    current_user: Dict[str, Any] = Depends(require_user),
) -> RoomScheduleResponse:
    try:
        date_obj: datetime = datetime.strptime(date, "%Y-%m-%d")
    except ValueError:
        raise InvalidInputError("Invalid date format. Use YYYY-MM-DD")

    unix_timestamp: int = int(date_obj.timestamp())
    schedule: RoomScheduleResponse = booking_service.get_room_schedule_by_date(
        room_id, unix_timestamp
    )
    return schedule
