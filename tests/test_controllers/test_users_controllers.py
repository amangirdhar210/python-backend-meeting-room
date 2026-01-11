import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, MagicMock
from app.models.models import User
from app.utils.errors import InvalidInputError, NotFoundError, ConflictError


class TestUsersControllers:

    @pytest.fixture
    def mock_user_service(self):
        return MagicMock()

    @pytest.fixture
    def client(self, mock_user_service):
        from fastapi import FastAPI, Request
        from app.controllers.users_controllers import users_router
        from app.dependencies.dependencies import get_user_service
        from app.middleware.auth_middleware import set_current_user, require_admin_state
        from app.utils.exception_handlers import (
            invalid_input_exception_handler,
            not_found_exception_handler,
            conflict_exception_handler,
            general_exception_handler,
        )

        app = FastAPI()
        app.include_router(users_router)

        app.add_exception_handler(InvalidInputError, invalid_input_exception_handler)
        app.add_exception_handler(NotFoundError, not_found_exception_handler)
        app.add_exception_handler(ConflictError, conflict_exception_handler)
        app.add_exception_handler(Exception, general_exception_handler)

        async def mock_set_current_user(request: Request):
            request.state.user = {
                "user_id": "admin-123",
                "email": "admin@example.com",
                "role": "admin",
            }

        async def mock_require_admin(request: Request):
            pass

        app.dependency_overrides[get_user_service] = lambda: mock_user_service
        app.dependency_overrides[set_current_user] = mock_set_current_user
        app.dependency_overrides[require_admin_state] = mock_require_admin

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

    def test_register_user_success(self, client, mock_user_service):
        mock_user_service.register = AsyncMock()

        response = client.post(
            "/api/users/register",
            json={
                "name": "Jane Doe",
                "email": "jane@example.com",
                "password": "password123",
                "role": "user",
            },
        )

        assert response.status_code == 201
        assert response.json() == {"message": "user registered successfully"}
        mock_user_service.register.assert_called_once()

    def test_register_user_conflict(self, client, mock_user_service):
        mock_user_service.register = AsyncMock(
            side_effect=ConflictError("Email already exists")
        )

        response = client.post(
            "/api/users/register",
            json={
                "name": "Jane Doe",
                "email": "existing@example.com",
                "password": "password123",
                "role": "user",
            },
        )

        assert response.status_code == 409
        assert response.json()["detail"] == "Email already exists"

    @pytest.mark.parametrize(
        "payload,description",
        [
            (
                {"email": "test@test.com", "password": "pass", "role": "user"},
                "missing name",
            ),
            ({"name": "Test", "password": "pass", "role": "user"}, "missing email"),
            (
                {"name": "Test", "email": "test@test.com", "role": "user"},
                "missing password",
            ),
            (
                {"name": "Test", "email": "test@test.com", "password": "pass"},
                "missing role",
            ),
            (
                {
                    "name": "Test",
                    "email": "invalid",
                    "password": "pass",
                    "role": "user",
                },
                "invalid email",
            ),
            (
                {
                    "name": "Test",
                    "email": "test@test.com",
                    "password": "short",
                    "role": "user",
                },
                "short password",
            ),
            (
                {
                    "name": "Test",
                    "email": "test@test.com",
                    "password": "pass123",
                    "role": "invalid",
                },
                "invalid role",
            ),
        ],
    )
    def test_register_user_validation_errors(self, client, payload, description):
        response = client.post("/api/users/register", json=payload)
        assert response.status_code == 422, f"Failed for case: {description}"

    def test_get_all_users_success(self, client, mock_user_service, sample_user):
        users = [
            sample_user,
            User(
                id="user-456",
                name="Jane Doe",
                email="jane@example.com",
                password="hashed",
                role="admin",
                created_at=1704700000,
                updated_at=1704700000,
            ),
        ]
        mock_user_service.get_all_users = AsyncMock(return_value=users)

        response = client.get("/api/users")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]["id"] == "user-123"
        assert data[1]["id"] == "user-456"
        assert "password" not in data[0]
        assert "password" not in data[1]

    def test_get_all_users_empty(self, client, mock_user_service):
        mock_user_service.get_all_users = AsyncMock(return_value=[])

        response = client.get("/api/users")

        assert response.status_code == 200
        assert response.json() == []

    def test_get_user_by_id_success(self, client, mock_user_service, sample_user):
        mock_user_service.get_user_by_id = AsyncMock(return_value=sample_user)

        response = client.get("/api/users/user-123")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == "user-123"
        assert data["name"] == "John Doe"
        assert data["email"] == "john@example.com"
        assert "password" not in data
        mock_user_service.get_user_by_id.assert_called_once_with("user-123")

    def test_get_user_by_id_not_found(self, client, mock_user_service):
        mock_user_service.get_user_by_id = AsyncMock(
            side_effect=NotFoundError("User not found")
        )

        response = client.get("/api/users/nonexistent")

        assert response.status_code == 404
        assert response.json()["detail"] == "User not found"

    def test_update_user_success(self, client, mock_user_service):
        mock_user_service.update_user = AsyncMock()

        response = client.put(
            "/api/users/user-123",
            json={"name": "Updated Name", "email": "updated@example.com"},
        )

        assert response.status_code == 200
        assert response.json() == {"message": "user updated successfully"}
        mock_user_service.update_user.assert_called_once()

    def test_update_user_not_found(self, client, mock_user_service):
        mock_user_service.update_user = AsyncMock(
            side_effect=NotFoundError("User not found")
        )

        response = client.put(
            "/api/users/nonexistent",
            json={"name": "Updated Name"},
        )

        assert response.status_code == 404

    def test_update_user_conflict(self, client, mock_user_service):
        mock_user_service.update_user = AsyncMock(
            side_effect=ConflictError("Email already in use")
        )

        response = client.put(
            "/api/users/user-123",
            json={"email": "existing@example.com"},
        )

        assert response.status_code == 409
        assert response.json()["detail"] == "Email already in use"

    def test_update_user_cannot_edit_yourself(self, client, mock_user_service):
        mock_user_service.update_user = AsyncMock(
            side_effect=InvalidInputError("You cannot edit your own account")
        )

        response = client.put(
            "/api/users/admin-123",
            json={"name": "Updated Name"},
        )

        assert response.status_code == 400
        assert response.json()["detail"] == "You cannot edit your own account"

    def test_update_user_superadmin_protection(self, client, mock_user_service):
        mock_user_service.update_user = AsyncMock(
            side_effect=InvalidInputError("Superadmin accounts cannot be updated")
        )

        response = client.put(
            "/api/users/superadmin-123",
            json={"name": "Updated Name"},
        )

        assert response.status_code == 400
        assert response.json()["detail"] == "Superadmin accounts cannot be updated"

    @pytest.mark.parametrize(
        "payload,description",
        [
            ({"email": "invalid"}, "invalid email format"),
            ({"role": "superuser"}, "invalid role"),
            ({"name": ""}, "empty name"),
        ],
    )
    def test_update_user_validation_errors(self, client, payload, description):
        response = client.put("/api/users/user-123", json=payload)
        assert response.status_code == 422, f"Failed for case: {description}"

    def test_delete_user_success(self, client, mock_user_service):
        mock_user_service.delete_user_by_id = AsyncMock()

        response = client.delete("/api/users/user-123")

        assert response.status_code == 200
        assert response.json() == {"message": "user deleted successfully"}
        mock_user_service.delete_user_by_id.assert_called_once()

    def test_delete_user_not_found(self, client, mock_user_service):
        mock_user_service.delete_user_by_id = AsyncMock(
            side_effect=NotFoundError("User not found")
        )

        response = client.delete("/api/users/nonexistent")

        assert response.status_code == 404

    def test_delete_user_cannot_delete_yourself(self, client, mock_user_service):
        mock_user_service.delete_user_by_id = AsyncMock(
            side_effect=InvalidInputError("You cannot delete your own account")
        )

        response = client.delete("/api/users/admin-123")

        assert response.status_code == 400
        assert response.json()["detail"] == "You cannot delete your own account"
