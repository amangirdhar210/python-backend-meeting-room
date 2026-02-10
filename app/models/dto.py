from pydantic import BaseModel, Field, EmailStr, ConfigDict, field_validator
from typing import Optional, List
import re
import time


class LoginUserRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True, str_min_length=1)
    
    email: EmailStr = Field(max_length=255)
    password: str = Field(min_length=1, max_length=200)


class UserDTO(BaseModel):
    id: str = Field(min_length=1)
    name: str = Field(min_length=1, max_length=100)
    email: EmailStr
    role: str = Field(pattern="^(user|admin|superadmin)$")
    created_at: int = Field(gt=0)
    updated_at: int = Field(gt=0)


class LoginUserResponse(BaseModel):
    token: str = Field(min_length=1)
    user: UserDTO


class RegisterUserRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True, str_min_length=1)
    
    name: str = Field(min_length=1, max_length=100, pattern=r"^[a-zA-Z0-9\s\-_.]+$")
    email: EmailStr = Field(max_length=255)
    password: str = Field(min_length=8, max_length=200)
    role: str = Field(pattern="^(user|admin|superadmin)$")
    
    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        if not re.search(r"[a-z]", v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not re.search(r"\d", v):
            raise ValueError("Password must contain at least one number")
        if not re.search(r"[@$!%*?&#]", v):
            raise ValueError("Password must contain at least one special character (@$!%*?&#)")
        return v


class UpdateUserRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    
    name: Optional[str] = Field(default=None, min_length=1, max_length=100, pattern=r"^[a-zA-Z0-9\s\-_.]+$")
    email: Optional[EmailStr] = Field(default=None, max_length=255)
    role: Optional[str] = Field(default=None, pattern="^(user|admin|superadmin)$")


class RoomDTO(BaseModel):
    id: str = Field(min_length=1)
    name: str = Field(min_length=1, max_length=100)
    room_number: int = Field(gt=0)
    capacity: int = Field(gt=0, le=1000)
    floor: int = Field(ge=0, le=200)
    amenities: List[str] = Field(default_factory=list, max_length=10)
    status: str = Field(pattern="^(available|unavailable|maintenance)$")
    is_occupied: bool = False
    location: str = Field(min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=500)
    created_at: int = Field(gt=0)
    updated_at: int = Field(gt=0)
    model_config = ConfigDict(populate_by_name=True)


class AddRoomRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True, str_min_length=1)
    
    name: str = Field(min_length=1, max_length=100, pattern=r"^[a-zA-Z0-9\s\-_.]+$")
    room_number: int = Field(gt=0, le=9999)
    capacity: int = Field(gt=0, le=1000)
    floor: int = Field(ge=0, le=200)
    amenities: List[str] = Field(default_factory=list, max_length=10)
    status: Optional[str] = Field(default="available", pattern="^(available|unavailable|maintenance)$")
    location: str = Field(min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=500)


class UpdateRoomRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    
    name: Optional[str] = Field(default=None, min_length=1, max_length=100, pattern=r"^[a-zA-Z0-9\s\-_.]+$")
    capacity: Optional[int] = Field(default=None, gt=0, le=1000)
    amenities: Optional[List[str]] = Field(default=None, max_length=10)
    status: Optional[str] = Field(default=None, pattern="^(available|unavailable|maintenance)$")
    location: Optional[str] = Field(default=None, min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=500)


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


class CreateBookingRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True, str_min_length=1)
    
    room_id: str = Field(min_length=1, max_length=100)
    start_time: int = Field(gt=0)
    end_time: int = Field(gt=0)
    purpose: str = Field(min_length=1, max_length=500, pattern=r"^[a-zA-Z0-9\s\-_.,:;!?()\[\]{}/'\"&@#+]+$")
    
    @field_validator("start_time", "end_time")
    @classmethod
    def validate_booking_timeframe(cls, v: int) -> int:
        current_time = int(time.time())
        max_future_time = current_time + (15 * 24 * 60 * 60)
        
        if v < current_time:
            raise ValueError("Cannot book in the past")
        if v > max_future_time:
            raise ValueError("Cannot book more than 15 days in the future")
        return v
    
    @field_validator("end_time")
    @classmethod
    def validate_meeting_duration(cls, v: int, info) -> int:
        start_time = info.data.get("start_time")
        if start_time:
            duration = v - start_time
            max_duration = 12 * 60 * 60
            if duration > max_duration:
                raise ValueError("Meeting duration cannot exceed 12 hours")
            if duration <= 0:
                raise ValueError("End time must be after start time")
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


class RoomScheduleRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    
    date: str = Field(pattern=r"^\d{4}-\d{2}-\d{2}$", min_length=10, max_length=10, description="Date in YYYY-MM-DD format")


class ErrorResponse(BaseModel):
    error: str = Field(min_length=1)


class GenericResponse(BaseModel):
    message: str = Field(min_length=1)
