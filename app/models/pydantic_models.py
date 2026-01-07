from pydantic import BaseModel, Field, EmailStr, ConfigDict
from typing import Optional, List, Annotated


class LoginUserRequest(BaseModel):
    email: EmailStr
    password: str


class UserDTO(BaseModel):
    id: str
    name: str
    email: str
    role: str
    created_at: int
    updated_at: int


class LoginUserResponse(BaseModel):
    token: str
    user: UserDTO


class RegisterUserRequest(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    email: EmailStr
    password: str = Field(min_length=6)
    role: str = Field(pattern="^(user|admin)$")


class RoomDTO(BaseModel):
    id: str
    name: str
    room_number: int
    capacity: int
    floor: int
    amenities: List[str]
    status: str
    location: str
    description: Optional[str] = None
    created_at: int
    updated_at: int
    model_config = ConfigDict(populate_by_name=True)


class AddRoomRequest(BaseModel):
    name: Annotated[str, "name of the room"] = Field(min_length=1, max_length=100)
    room_number: int = Field(gt=0)
    capacity: int = Field(gt=0)
    floor: int = Field(ge=0)
    amenities: List[str] = []
    status: Optional[str] = "available"
    location: str = Field(min_length=1)
    description: Optional[str] = None
    model_config = ConfigDict(populate_by_name=True)


class BookingDTO(BaseModel):
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


class CreateBookingRequest(BaseModel):
    room_id: str
    start_time: int
    end_time: int
    purpose: str = Field(min_length=1)


class ScheduleSlotDTO(BaseModel):
    start_time: int
    end_time: int
    is_booked: bool
    booking_id: Optional[str] = None
    user_name: Optional[str] = None
    purpose: Optional[str] = None


class RoomScheduleResponse(BaseModel):
    room_id: str
    room_name: str
    room_number: int
    date: int
    bookings: List[ScheduleSlotDTO]


class ErrorResponse(BaseModel):
    error: str


class GenericResponse(BaseModel):
    message: str
