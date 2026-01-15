from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from contextlib import asynccontextmanager

from app.controllers.auth_controllers import auth_router
from app.controllers.bookings_controllers import bookings_router
from app.controllers.rooms_controllers import rooms_router
from app.controllers.users_controllers import users_router
from app.config.config import settings
from app.dependencies import init_app_state
from app.utils.errors import ApplicationError
from app.utils.exception_handlers import (
    application_error_handler,
    validation_exception_handler,
    general_exception_handler,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_app_state(app.state)
    yield


app = FastAPI(
    title="Meeting Room Booking API",
    description="RESTful API for managing meeting room bookings, users, and rooms with JWT authentication",
    version="1.0.0",
    lifespan=lifespan,
)

# Register exception handlers before middleware
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(ApplicationError, application_error_handler)
app.add_exception_handler(Exception, general_exception_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

app.include_router(auth_router)
app.include_router(bookings_router)
app.include_router(rooms_router)
app.include_router(users_router)
