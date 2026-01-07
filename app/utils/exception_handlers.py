"""
Global exception handlers for the FastAPI application.
These handlers catch custom exceptions and return appropriate HTTP responses.
"""

from fastapi import Request, status
from fastapi.responses import JSONResponse
from app.utils.errors import (
    NotFoundError,
    InvalidInputError,
    UnauthorizedError,
    ConflictError,
    InternalError,
    RoomUnavailableError,
    TimeRangeInvalidError,
)


async def not_found_exception_handler(request: Request, exc: NotFoundError):
    """Handle NotFoundError exceptions."""
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"detail": str(exc)},
    )


async def invalid_input_exception_handler(request: Request, exc: InvalidInputError):
    """Handle InvalidInputError exceptions."""
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": str(exc)},
    )


async def unauthorized_exception_handler(request: Request, exc: UnauthorizedError):
    """Handle UnauthorizedError exceptions."""
    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content={"detail": str(exc)},
    )


async def conflict_exception_handler(request: Request, exc: ConflictError):
    """Handle ConflictError exceptions."""
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={"detail": str(exc)},
    )


async def room_unavailable_exception_handler(
    request: Request, exc: RoomUnavailableError
):
    """Handle RoomUnavailableError exceptions."""
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={"detail": str(exc)},
    )


async def time_range_invalid_exception_handler(
    request: Request, exc: TimeRangeInvalidError
):
    """Handle TimeRangeInvalidError exceptions."""
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": str(exc)},
    )


async def internal_error_exception_handler(request: Request, exc: InternalError):
    """Handle InternalError exceptions."""
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": str(exc)},
    )


async def general_exception_handler(request: Request, exc: Exception):
    """Handle all unhandled exceptions."""
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error"},
    )
