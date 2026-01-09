import os
from typing import List
from dotenv import load_dotenv

load_dotenv()


class Settings:
    JWT_SECRET: str = os.getenv("JWT_SECRET", "amangirdharamangirdhar123123")
    JWT_EXPIRATION_HOURS: int = 24

    AWS_REGION: str = os.getenv("AWS_REGION", "us-east-1")
    DYNAMODB_TABLE_NAME: str = os.getenv("TABLE_NAME", "MeetingRoomSystem")

    CORS_ALLOWED_ORIGINS: List[str] = [
        "http://localhost:4200",
        "http://127.0.0.1:4200",
    ]

    SUPERADMIN_EMAILS: List[str] = [
        "admin@example.com",
    ]

    SERVER_PORT: int = int(os.getenv("SERVER_PORT", "8000"))
    MAX_BOOKING_DAYS_IN_FUTURE: int = int(os.getenv("MAX_BOOKING_DAYS_IN_FUTURE", "10"))


settings = Settings()
