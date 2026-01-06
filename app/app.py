from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.controllers.auth_controllers import auth_router
from app.controllers.bookings_controllers import bookings_router
from app.controllers.rooms_controllers import rooms_router
from app.controllers.users_controllers import users_router
from app.config.config import settings


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

app.include_router(auth_router)
app.include_router(bookings_router)
app.include_router(rooms_router)
app.include_router(users_router)
