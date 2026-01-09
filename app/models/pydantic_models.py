from pydantic import BaseModel, Field, EmailStr, ConfigDict, field_validator
from typing import Optional, List


class LoginUserRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=200)


class UserDTO(BaseModel):
    id: str = Field(min_length=1)
    name: str = Field(min_length=1, max_length=100)
    email: EmailStr
    role: str = Field(pattern="^(user|admin)$")
    created_at: int = Field(gt=0)
    updated_at: int = Field(gt=0)


class LoginUserResponse(BaseModel):
    token: str = Field(min_length=1)
    user: UserDTO


class RegisterUserRequest(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    email: EmailStr
    password: str = Field(min_length=6, max_length=200)
    role: str = Field(pattern="^(user|admin)$")


class UpdateUserRequest(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    email: Optional[EmailStr] = None
    role: Optional[str] = Field(default=None, pattern="^(user|admin)$")


class RoomDTO(BaseModel):
    id: str = Field(min_length=1)
    name: str = Field(min_length=1, max_length=100)
    room_number: int = Field(gt=0)
    capacity: int = Field(gt=0, le=1000)
    floor: int = Field(ge=0, le=200)
    amenities: List[str] = Field(default_factory=list)
    status: str = Field(pattern="^(available|unavailable|maintenance)$")
    location: str = Field(min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=500)
    created_at: int = Field(gt=0)
    updated_at: int = Field(gt=0)
    model_config = ConfigDict(populate_by_name=True)


class AddRoomRequest(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    room_number: int = Field(gt=0, le=9999)
    capacity: int = Field(gt=0, le=1000)
    floor: int = Field(ge=0, le=200)
    amenities: List[str] = Field(default_factory=list, max_length=50)
    status: Optional[str] = Field(
        default="available", pattern="^(available|unavailable|maintenance)$"
    )
    location: str = Field(min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=500)
    model_config = ConfigDict(populate_by_name=True)

    @field_validator("amenities")
    @classmethod
    def validate_amenities(cls, v: List[str]) -> List[str]:
        if v:
            for amenity in v:
                if not amenity or len(amenity) > 50:
                    raise ValueError("Each amenity must be 1-50 characters")
        return v


class UpdateRoomRequest(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    capacity: Optional[int] = Field(default=None, gt=0, le=1000)
    amenities: Optional[List[str]] = Field(default=None, max_length=50)
    status: Optional[str] = Field(
        default=None, pattern="^(available|unavailable|maintenance)$"
    )
    location: Optional[str] = Field(default=None, min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=500)
    model_config = ConfigDict(populate_by_name=True)

    @field_validator("amenities")
    @classmethod
    def validate_amenities(cls, v: Optional[List[str]]) -> Optional[List[str]]:
        if v:
            for amenity in v:
                if not amenity or len(amenity) > 50:
                    raise ValueError("Each amenity must be 1-50 characters")
        return v


class BookingDTO(BaseModel):
    id: str = Field(min_length=1)
    user_id: str = Field(min_length=1)
    user_name: str = Field(min_length=1, max_length=100)
    room_id: str = Field(min_length=1)
    room_number: int = Field(gt=0)
    start_time: int = Field(gt=0)
    end_time: int = Field(gt=0)
    purpose: str = Field(min_length=1, max_length=500)
    status: str = Field(pattern="^(confirmed|cancelled)$")
    created_at: int = Field(gt=0)
    updated_at: int = Field(gt=0)

    @field_validator("end_time")
    @classmethod
    def validate_end_time(cls, v: int, info) -> int:
        if "start_time" in info.data and v <= info.data["start_time"]:
            raise ValueError("end_time must be after start_time")
        return v


class CreateBookingRequest(BaseModel):
    room_id: str = Field(min_length=1)
    start_time: int = Field(gt=0)
    end_time: int = Field(gt=0)
    purpose: str = Field(min_length=1, max_length=500)

    @field_validator("end_time")
    @classmethod
    def validate_end_time(cls, v: int, info) -> int:
        if "start_time" in info.data and v <= info.data["start_time"]:
            raise ValueError("end_time must be after start_time")
        return v


class ScheduleSlotDTO(BaseModel):
    start_time: int = Field(gt=0)
    end_time: int = Field(gt=0)
    is_booked: bool
    booking_id: Optional[str] = Field(default=None, min_length=1)
    user_name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    purpose: Optional[str] = Field(default=None, min_length=1, max_length=500)


class RoomScheduleResponse(BaseModel):
    room_id: str = Field(min_length=1)
    room_name: str = Field(min_length=1, max_length=100)
    room_number: int = Field(gt=0)
    date: int = Field(gt=0)
    bookings: List[ScheduleSlotDTO] = Field(default_factory=list)


class ErrorResponse(BaseModel):
    error: str = Field(min_length=1)


class GenericResponse(BaseModel):
    message: str = Field(min_length=1)
