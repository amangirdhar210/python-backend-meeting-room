from typing import Optional, List
from pydantic import BaseModel


class User(BaseModel):
    id: str
    name: str
    email: str
    password: str
    role: str
    created_at: int
    updated_at: int


class Room(BaseModel):
    id: str
    name: str
    room_number: int
    capacity: int
    floor: int
    amenities: List[str]
    status: str
    location: str
    description: Optional[str]
    created_at: int
    updated_at: int


class Booking(BaseModel):
    id: str
    user_id: str
    user_name: str
    room_id: str
    room_number: int
    start_time: int
    end_time: int
    purpose: str
    status: str
    created_at: int
    updated_at: int


class TimeSlot(BaseModel):
    start_time: int
    end_time: int
    duration: int


class BookingWithDetails(BaseModel):
    id: str
    user_id: str
    user_name: str
    room_id: str
    room_number: int
    start_time: int
    end_time: int
    purpose: str
    status: str
    created_at: int
    updated_at: int
    user_email: str
    room_name: str


class ScheduleSlot(BaseModel):
    start_time: str
    end_time: str
    is_booked: bool
    booking_id: Optional[str] = None
    user_name: Optional[str] = None
    purpose: Optional[str] = None


class RoomScheduleResponse(BaseModel):
    room_id: str
    room_name: str
    room_number: int
    date: str
    bookings: List[ScheduleSlot]
