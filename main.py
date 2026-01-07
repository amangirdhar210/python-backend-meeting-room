from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.controllers.auth_controllers import auth_router
from app.controllers.bookings_controllers import bookings_router
from app.controllers.rooms_controllers import rooms_router
from app.controllers.users_controllers import users_router
from app.config.config import settings
from app.utils.errors import (
    NotFoundError,
    InvalidInputError,
    UnauthorizedError,
    ConflictError,
    InternalError,
    RoomUnavailableError,
    TimeRangeInvalidError,
)
from app.utils.exception_handlers import (
    not_found_exception_handler,
    invalid_input_exception_handler,
    unauthorized_exception_handler,
    conflict_exception_handler,
    internal_error_exception_handler,
    room_unavailable_exception_handler,
    time_range_invalid_exception_handler,
    general_exception_handler,
)

app = FastAPI(
    title="Meeting Room Booking API",
    description="RESTful API for managing meeting room bookings, users, and rooms with JWT authentication",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
)

app.add_exception_handler(NotFoundError, not_found_exception_handler)
app.add_exception_handler(InvalidInputError, invalid_input_exception_handler)
app.add_exception_handler(UnauthorizedError, unauthorized_exception_handler)
app.add_exception_handler(ConflictError, conflict_exception_handler)
app.add_exception_handler(InternalError, internal_error_exception_handler)
app.add_exception_handler(RoomUnavailableError, room_unavailable_exception_handler)
app.add_exception_handler(TimeRangeInvalidError, time_range_invalid_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)

app.include_router(auth_router)
app.include_router(bookings_router)
app.include_router(rooms_router)
app.include_router(users_router)
