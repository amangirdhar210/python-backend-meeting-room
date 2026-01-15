from typing import Dict, Optional
from fastapi import status


class ErrorCode:
    INVALID_CREDENTIALS = 1001
    UNAUTHORIZED = 1002
    TOKEN_EXPIRED = 1003
    INVALID_TOKEN = 1004
    INSUFFICIENT_PERMISSIONS = 1005

    USER_NOT_FOUND = 2001
    USER_ALREADY_EXISTS = 2002
    INVALID_EMAIL = 2003
    INVALID_USER_DATA = 2004

    ROOM_NOT_FOUND = 3001
    ROOM_ALREADY_EXISTS = 3002
    ROOM_UNAVAILABLE = 3003
    INVALID_ROOM_DATA = 3004

    BOOKING_NOT_FOUND = 4001
    BOOKING_CONFLICT = 4002
    INVALID_TIME_RANGE = 4003
    BOOKING_IN_PAST = 4004
    BOOKING_TOO_FAR = 4005
    INVALID_BOOKING_DATA = 4006
    BOOKING_CANCELLED = 4007

    INVALID_INPUT = 5001
    MISSING_REQUIRED_FIELD = 5002
    INVALID_FORMAT = 5003

    INTERNAL_ERROR = 9001
    DATABASE_ERROR = 9002
    EXTERNAL_SERVICE_ERROR = 9003


ERROR_REGISTRY: Dict[int, Dict[str, any]] = {
    ErrorCode.INVALID_CREDENTIALS: {
        "message": "Invalid email or password",
        "status_code": status.HTTP_401_UNAUTHORIZED,
    },
    ErrorCode.UNAUTHORIZED: {
        "message": "Unauthorized access",
        "status_code": status.HTTP_401_UNAUTHORIZED,
    },
    ErrorCode.TOKEN_EXPIRED: {
        "message": "Authentication token has expired",
        "status_code": status.HTTP_401_UNAUTHORIZED,
    },
    ErrorCode.INVALID_TOKEN: {
        "message": "Invalid authentication token",
        "status_code": status.HTTP_401_UNAUTHORIZED,
    },
    ErrorCode.INSUFFICIENT_PERMISSIONS: {
        "message": "Insufficient permissions to perform this action",
        "status_code": status.HTTP_403_FORBIDDEN,
    },
    ErrorCode.USER_NOT_FOUND: {
        "message": "User not found",
        "status_code": status.HTTP_404_NOT_FOUND,
    },
    ErrorCode.USER_ALREADY_EXISTS: {
        "message": "User with this email already exists",
        "status_code": status.HTTP_409_CONFLICT,
    },
    ErrorCode.INVALID_EMAIL: {
        "message": "Invalid email format",
        "status_code": status.HTTP_400_BAD_REQUEST,
    },
    ErrorCode.INVALID_USER_DATA: {
        "message": "Invalid user data provided",
        "status_code": status.HTTP_400_BAD_REQUEST,
    },
    ErrorCode.ROOM_NOT_FOUND: {
        "message": "Room not found",
        "status_code": status.HTTP_404_NOT_FOUND,
    },
    ErrorCode.ROOM_ALREADY_EXISTS: {
        "message": "Room with this number already exists",
        "status_code": status.HTTP_409_CONFLICT,
    },
    ErrorCode.ROOM_UNAVAILABLE: {
        "message": "Room is not available for the requested time",
        "status_code": status.HTTP_409_CONFLICT,
    },
    ErrorCode.INVALID_ROOM_DATA: {
        "message": "Invalid room data provided",
        "status_code": status.HTTP_400_BAD_REQUEST,
    },
    ErrorCode.BOOKING_NOT_FOUND: {
        "message": "Booking not found",
        "status_code": status.HTTP_404_NOT_FOUND,
    },
    ErrorCode.BOOKING_CONFLICT: {
        "message": "Booking conflicts with existing reservation",
        "status_code": status.HTTP_409_CONFLICT,
    },
    ErrorCode.INVALID_TIME_RANGE: {
        "message": "Invalid time range: end time must be after start time",
        "status_code": status.HTTP_400_BAD_REQUEST,
    },
    ErrorCode.BOOKING_IN_PAST: {
        "message": "Cannot create booking in the past",
        "status_code": status.HTTP_400_BAD_REQUEST,
    },
    ErrorCode.BOOKING_TOO_FAR: {
        "message": "Booking date exceeds maximum allowed days in future",
        "status_code": status.HTTP_400_BAD_REQUEST,
    },
    ErrorCode.INVALID_BOOKING_DATA: {
        "message": "Invalid booking data provided",
        "status_code": status.HTTP_400_BAD_REQUEST,
    },
    ErrorCode.BOOKING_CANCELLED: {
        "message": "Booking has been cancelled",
        "status_code": status.HTTP_400_BAD_REQUEST,
    },
    ErrorCode.INVALID_INPUT: {
        "message": "Invalid input provided",
        "status_code": status.HTTP_400_BAD_REQUEST,
    },
    ErrorCode.MISSING_REQUIRED_FIELD: {
        "message": "Required field is missing",
        "status_code": status.HTTP_400_BAD_REQUEST,
    },
    ErrorCode.INVALID_FORMAT: {
        "message": "Invalid data format",
        "status_code": status.HTTP_400_BAD_REQUEST,
    },
    ErrorCode.INTERNAL_ERROR: {
        "message": "An internal error occurred",
        "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
    },
    ErrorCode.DATABASE_ERROR: {
        "message": "Database operation failed",
        "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
    },
    ErrorCode.EXTERNAL_SERVICE_ERROR: {
        "message": "External service error",
        "status_code": status.HTTP_503_SERVICE_UNAVAILABLE,
    },
}


class ApplicationError(Exception):

    def __init__(
        self,
        error_code: int,
        message: Optional[str] = None,
        details: Optional[Dict] = None,
    ):
        self.error_code = error_code
        self.details = details or {}

        error_info = ERROR_REGISTRY.get(error_code)
        if not error_info:
            raise ValueError(f"Error code {error_code} not found in registry")

        self.message = message or error_info["message"]
        self.status_code = error_info["status_code"]

        super().__init__(self.message)

    def to_dict(self) -> Dict:
        response = {
            "error_code": self.error_code,
            "message": self.message,
        }
        if self.details:
            response["details"] = self.details
        return response
