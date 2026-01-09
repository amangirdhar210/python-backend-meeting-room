import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, MagicMock
from app.models.models import User
from app.utils.errors import InvalidInputError, UnauthorizedError


class TestUsersControllers:
    @pytest.fixture
    def mock_user_service(self):
        return MagicMock()

    @pytest.fixture
    def mock_auth_middleware(self):

        async def mock_set_current_user(request):
            request.state.user = {
                "user_id": "admin-123",
                "email": "admin@example.com",
                "role": "admin",
            }

        async def mock_require_admin():
            pass

        return mock_set_current_user, mock_require_admin

    @pytest.fixture
    def client(self, mock_user_service, mock_auth_middleware):
        from fastapi import FastAPI
        from app.controllers.users_controllers import users_router
        from app.dependencies.dependencies import get_user_service
        from app.middleware.auth_middleware import set_current_user, require_admin_state
        from app.utils.exception_handlers import (
            invalid_input_exception_handler,
            unauthorized_exception_handler,
            general_exception_handler,
        )
        from app.utils.errors import InvalidInputError, UnauthorizedError

        app = FastAPI()
        app.include_router(users_router)

        app.add_exception_handler(InvalidInputError, invalid_input_exception_handler)
        app.add_exception_handler(UnauthorizedError, unauthorized_exception_handler)
        app.add_exception_handler(Exception, general_exception_handler)

        app.dependency_overrides[get_user_service] = lambda: mock_user_service
        app.dependency_overrides[set_current_user] = lambda: mock_auth_middleware[0]
        app.dependency_overrides[require_admin_state] = lambda: mock_auth_middleware[1]

        return TestClient(app, raise_server_exceptions=False)

    @pytest.fixture
    def sample_user(self):
        return User(
            id="user-123",
            name="John Doe",
            email="john@example.com",
            password="hashed_password",
            role="user",
            created_at=1704700000,
            updated_at=1704700000,
        )
