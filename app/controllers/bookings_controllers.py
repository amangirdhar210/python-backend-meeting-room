from fastapi import APIRouter, Depends
from app.services.bookings_service import BookingService
from app.models.models import Booking


bookings_router = APIRouter()


@bookings_router.post("/bookings")
def create_booking(booking: Booking):
    pass


def get_booking_by_id(booking_id: str):
    pass


@bookings_router.delete("/bookings/{id}")
def cancel_booking(id: str):
    pass


@bookings_router.get("/bookings")
def get_all_bookings():
    pass


def get_bookings_by_room_id(room_id: str):
    pass


@bookings_router.get("/bookings/my")
def get_bookings_by_user_id(user_id: str):
    pass


@bookings_router.get("/rooms/{id}/schedule")
def get_bookings_with_details_by_room_id(id: str):
    pass


def get_bookings_by_date_range(start_date: int, end_date: int):
    pass


@bookings_router.get("/rooms/{id}/schedule/date")
def get_room_schedule_by_date(
    id: str, date: str 
):
    pass
