import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, MagicMock
from app.models.models import Room
from app.utils.errors import ApplicationError, ErrorCode


class TestRoomsControllers:

    @pytest.fixture
    def mock_room_service(self):
        return MagicMock()

    @pytest.fixture
    def client(self, mock_room_service):
        from fastapi import FastAPI, Request
        from app.controllers.rooms_controllers import rooms_router
        from app.dependencies.dependencies import get_room_service
        from app.middleware.auth_middleware import set_current_user, require_admin_state
        from app.utils.exception_handlers import (
            application_error_handler,
            general_exception_handler,
        )

        app = FastAPI()
        app.include_router(rooms_router)

        app.add_exception_handler(ApplicationError, application_error_handler)
        app.add_exception_handler(Exception, general_exception_handler)

        async def mock_set_current_user(request: Request):
            request.state.user = {
                "user_id": "admin-123",
                "email": "admin@example.com",
                "role": "admin",
            }

        async def mock_require_admin(request: Request):
            pass

        app.dependency_overrides[get_room_service] = lambda: mock_room_service
        app.dependency_overrides[set_current_user] = mock_set_current_user
        app.dependency_overrides[require_admin_state] = mock_require_admin

        return TestClient(app, raise_server_exceptions=False)

    @pytest.fixture
    def sample_room(self):
        return Room(
            id="room-123",
            name="Conference Room A",
            room_number=101,
            capacity=10,
            floor=1,
            amenities=["Projector", "Whiteboard"],
            status="available",
            location="Building A",
            description="Large conference room",
            created_at=1704700000,
            updated_at=1704700000,
        )

    def test_add_room_success(self, client, mock_room_service):
        mock_room_service.add_room = AsyncMock()

        response = client.post(
            "/api/rooms",
            json={
                "name": "Meeting Room B",
                "room_number": 102,
                "capacity": 8,
                "floor": 2,
                "amenities": ["TV", "Conference Phone"],
                "status": "available",
                "location": "Building B",
                "description": "Medium meeting room",
            },
        )

        assert response.status_code == 201
        assert response.json() == {"message": "room added successfully"}
        mock_room_service.add_room.assert_called_once()

    def test_add_room_conflict(self, client, mock_room_service):
        mock_room_service.add_room = AsyncMock(
            side_effect=ApplicationError(ErrorCode.ROOM_ALREADY_EXISTS)
        )

        response = client.post(
            "/api/rooms",
            json={
                "name": "Duplicate Room",
                "room_number": 101,
                "capacity": 10,
                "floor": 1,
                "location": "Building A",
            },
        )

        assert response.status_code == 409

    @pytest.mark.parametrize(
        "payload,description",
        [
            (
                {"room_number": 101, "capacity": 10, "floor": 1, "location": "A"},
                "missing name",
            ),
            (
                {"name": "Room", "capacity": 10, "floor": 1, "location": "A"},
                "missing room_number",
            ),
            (
                {"name": "Room", "room_number": 101, "floor": 1, "location": "A"},
                "missing capacity",
            ),
            (
                {"name": "Room", "room_number": 101, "capacity": 10, "location": "A"},
                "missing floor",
            ),
            (
                {"name": "Room", "room_number": 101, "capacity": 10, "floor": 1},
                "missing location",
            ),
            (
                {
                    "name": "Room",
                    "room_number": 0,
                    "capacity": 10,
                    "floor": 1,
                    "location": "A",
                },
                "invalid room_number",
            ),
            (
                {
                    "name": "Room",
                    "room_number": 101,
                    "capacity": 0,
                    "floor": 1,
                    "location": "A",
                },
                "invalid capacity",
            ),
            (
                {
                    "name": "Room",
                    "room_number": 101,
                    "capacity": 10,
                    "floor": -1,
                    "location": "A",
                },
                "invalid floor",
            ),
            (
                {
                    "name": "Room",
                    "room_number": 101,
                    "capacity": 10,
                    "floor": 1,
                    "location": "A",
                    "status": "invalid",
                },
                "invalid status",
            ),
        ],
    )
    def test_add_room_validation_errors(self, client, payload, description):
        response = client.post("/api/rooms", json=payload)
        assert response.status_code == 422, f"Failed for case: {description}"

    def test_get_all_rooms_success(self, client, mock_room_service, sample_room):
        rooms = [
            sample_room,
            Room(
                id="room-456",
                name="Meeting Room B",
                room_number=102,
                capacity=8,
                floor=2,
                amenities=["TV"],
                status="available",
                location="Building B",
                created_at=1704700000,
                updated_at=1704700000,
            ),
        ]
        mock_room_service.get_all_rooms = AsyncMock(return_value=rooms)

        response = client.get("/api/rooms")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]["id"] == "room-123"
        assert data[0]["status"] == "available"
        assert data[1]["id"] == "room-456"

    def test_get_all_rooms_empty(self, client, mock_room_service):
        mock_room_service.get_all_rooms = AsyncMock(return_value=[])

        response = client.get("/api/rooms")

        assert response.status_code == 200
        assert response.json() == []

    def test_get_room_by_id_success(self, client, mock_room_service, sample_room):
        mock_room_service.get_room_by_id = AsyncMock(return_value=sample_room)

        response = client.get("/api/rooms/room-123")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == "room-123"
        assert data["name"] == "Conference Room A"
        assert data["room_number"] == 101
        assert data["capacity"] == 10
        assert data["status"] == "available"
        mock_room_service.get_room_by_id.assert_called_once_with("room-123")

    def test_get_room_by_id_not_found(self, client, mock_room_service):
        mock_room_service.get_room_by_id = AsyncMock(
            side_effect=ApplicationError(ErrorCode.ROOM_NOT_FOUND)
        )

        response = client.get("/api/rooms/nonexistent")

        assert response.status_code == 404
        assert response.json()["message"] == "Room not found"

    def test_update_room_success(self, client, mock_room_service):
        mock_room_service.update_room = AsyncMock()

        response = client.put(
            "/api/rooms/room-123",
            json={
                "name": "Updated Room Name",
                "capacity": 15,
                "status": "maintenance",
            },
        )

        assert response.status_code == 200
        assert response.json() == {"message": "room updated successfully"}
        mock_room_service.update_room.assert_called_once()

    def test_update_room_not_found(self, client, mock_room_service):
        mock_room_service.update_room = AsyncMock(
            side_effect=ApplicationError(ErrorCode.ROOM_NOT_FOUND)
        )

        response = client.put(
            "/api/rooms/nonexistent",
            json={"name": "Updated Name"},
        )

        assert response.status_code == 404

    @pytest.mark.parametrize(
        "payload,description",
        [
            ({"capacity": 0}, "invalid capacity"),
            ({"capacity": 1001}, "capacity too large"),
            ({"status": "invalid"}, "invalid status"),
            ({"name": ""}, "empty name"),
        ],
    )
    def test_update_room_validation_errors(self, client, payload, description):
        response = client.put("/api/rooms/room-123", json=payload)
        assert response.status_code == 422, f"Failed for case: {description}"

    def test_delete_room_success(self, client, mock_room_service):
        mock_room_service.delete_room_by_id = AsyncMock()

        response = client.delete("/api/rooms/room-123")

        assert response.status_code == 200
        assert response.json() == {"message": "room deleted successfully"}
        mock_room_service.delete_room_by_id.assert_called_once_with("room-123")

    def test_delete_room_not_found(self, client, mock_room_service):
        mock_room_service.delete_room_by_id = AsyncMock(
            side_effect=ApplicationError(ErrorCode.ROOM_NOT_FOUND)
        )

        response = client.delete("/api/rooms/nonexistent")

        assert response.status_code == 404

    def test_add_room_with_optional_fields(self, client, mock_room_service):
        mock_room_service.add_room = AsyncMock()

        response = client.post(
            "/api/rooms",
            json={
                "name": "Simple Room",
                "room_number": 103,
                "capacity": 5,
                "floor": 1,
                "location": "Building C",
            },
        )

        assert response.status_code == 201

    def test_update_room_partial_update(self, client, mock_room_service):
        mock_room_service.update_room = AsyncMock()

        response = client.put(
            "/api/rooms/room-123",
            json={"status": "unavailable"},
        )

        assert response.status_code == 200
