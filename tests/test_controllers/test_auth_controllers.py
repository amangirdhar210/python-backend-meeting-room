import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, MagicMock
from app.models.models import User
from app.utils.errors import InvalidInputError, UnauthorizedError


class TestAuthControllers:

    @pytest.fixture
    def mock_auth_service(self):
        return MagicMock()

    @pytest.fixture
    def client(self, mock_auth_service):
        from fastapi import FastAPI
        from app.controllers.auth_controllers import auth_router
        from app.dependencies.dependencies import get_auth_service
        from app.utils.exception_handlers import (
            invalid_input_exception_handler,
            unauthorized_exception_handler,
            general_exception_handler,
        )
        from app.utils.errors import InvalidInputError, UnauthorizedError

        app = FastAPI()
        app.include_router(auth_router)

        app.add_exception_handler(InvalidInputError, invalid_input_exception_handler)
        app.add_exception_handler(UnauthorizedError, unauthorized_exception_handler)
        app.add_exception_handler(Exception, general_exception_handler)

        app.dependency_overrides[get_auth_service] = lambda: mock_auth_service

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

    def test_login_success(self, client, mock_auth_service, sample_user):
        mock_auth_service.login = AsyncMock(
            return_value=("mock-jwt-token", sample_user)
        )

        response = client.post(
            "/login",
            json={"email": "john@example.com", "password": "password123"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["token"] == "mock-jwt-token"
        assert data["user"]["id"] == "user-123"
        assert data["user"]["name"] == "John Doe"
        assert data["user"]["email"] == "john@example.com"
        assert data["user"]["role"] == "user"
        assert "password" not in data["user"]
        mock_auth_service.login.assert_called_once_with(
            "john@example.com", "password123"
        )

    def test_login_invalid_credentials(self, client, mock_auth_service):
        mock_auth_service.login = AsyncMock(
            side_effect=UnauthorizedError("Invalid credentials")
        )

        response = client.post(
            "/login",
            json={"email": "wrong@example.com", "password": "wrongpassword"},
        )

        assert response.status_code == 401
        assert response.json()["detail"] == "Invalid credentials"

    @pytest.mark.parametrize(
        "payload,description",
        [
            ({"password": "password123"}, "missing email"),
            ({"email": "john@example.com"}, "missing password"),
            (
                {"email": "not-an-email", "password": "password123"},
                "invalid email format",
            ),
            ({"email": "  ", "password": "  "}, "empty credentials"),
            ({}, "empty payload"),
            ({"email": "", "password": "password123"}, "empty email"),
            ({"email": "john@example.com", "password": ""}, "empty password"),
        ],
    )
    def test_login_validation_errors(
        self, client, mock_auth_service, payload, description
    ):
        """Test login validation errors return 422"""
        response = client.post("/login", json=payload)
        assert response.status_code == 422, f"Failed for case: {description}"

    def test_login_service_error(self, client, mock_auth_service):
        mock_auth_service.login = AsyncMock(side_effect=Exception("Database error"))

        response = client.post(
            "/login",
            json={"email": "john@example.com", "password": "password123"},
        )

        assert response.status_code == 500

    def test_login_admin_user(self, client, mock_auth_service):
        """Test successful login for admin user"""
        admin_user = User(
            id="admin-456",
            name="Admin User",
            email="admin@example.com",
            password="hashed_password",
            role="admin",
            created_at=1704700000,
            updated_at=1704700000,
        )
        mock_auth_service.login = AsyncMock(
            return_value=("admin-jwt-token", admin_user)
        )

        response = client.post(
            "/login",
            json={"email": "admin@example.com", "password": "adminpass"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["token"] == "admin-jwt-token"
        assert data["user"]["role"] == "admin"
        assert data["user"]["id"] == "admin-456"

    def test_health_check(self, client):
        response = client.get("/health")

        assert response.status_code == 200
        assert response.json() == {"status": "ok"}

    def test_login_response_structure(self, client, mock_auth_service, sample_user):
        """Test login response has correct structure"""
        mock_auth_service.login = AsyncMock(return_value=("test-token", sample_user))

        response = client.post(
            "/login",
            json={"email": "john@example.com", "password": "password123"},
        )

        assert response.status_code == 200
        data = response.json()
        assert "token" in data
        assert "user" in data
        assert isinstance(data["token"], str)
        assert isinstance(data["user"], dict)
        assert all(
            key in data["user"]
            for key in ["id", "name", "email", "role", "created_at", "updated_at"]
        )
