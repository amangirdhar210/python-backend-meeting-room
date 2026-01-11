import pytest
from unittest.mock import AsyncMock
from app.services.rooms_service import RoomService
from app.models.models import Room
from app.utils.errors import InvalidInputError, NotFoundError, ConflictError


class TestRoomService:

    @pytest.fixture
    def mock_room_repo(self):
        return AsyncMock()

    @pytest.fixture
    def room_service(self, mock_room_repo):
        return RoomService(mock_room_repo)

    @pytest.fixture
    def sample_room(self):
        return Room(
            id="room-123",
            name="Conference Room A",
            capacity=10,
            amenities=["Projector", "Whiteboard"],
            status="available",
            location="Building 1",
            room_number=101,
            floor=1,
            description="Main conference room",
            created_at=1704067200,
            updated_at=1704067200,
        )

    @pytest.mark.asyncio
    async def test_add_room_success(self, room_service, mock_room_repo, sample_room):
        mock_room_repo.check_room_number_exists_on_floor.return_value = False
        sample_room.id = None

        await room_service.add_room(sample_room)

        assert sample_room.id is not None
        assert len(sample_room.id) > 10
        mock_room_repo.create.assert_called_once()

    @pytest.mark.asyncio
    async def test_add_room_sets_timestamps(
        self, room_service, mock_room_repo, sample_room
    ):
        mock_room_repo.check_room_number_exists_on_floor.return_value = False
        sample_room.id = None

        await room_service.add_room(sample_room)

        assert sample_room.created_at > 0
        assert sample_room.updated_at > 0

    @pytest.mark.asyncio
    async def test_add_room_duplicate_room_number(
        self, room_service, mock_room_repo, sample_room
    ):
        mock_room_repo.check_room_number_exists_on_floor.return_value = True

        with pytest.raises(
            ConflictError, match="Room number already exists on this floor"
        ):
            await room_service.add_room(sample_room)

    @pytest.mark.asyncio
    async def test_add_room_none_room(self, room_service):
        with pytest.raises(InvalidInputError, match="Room is required"):
            await room_service.add_room(None)

    @pytest.mark.asyncio
    async def test_add_room_empty_name(self, room_service, sample_room):
        sample_room.name = ""

        with pytest.raises(InvalidInputError, match="Invalid room data"):
            await room_service.add_room(sample_room)

    @pytest.mark.asyncio
    async def test_add_room_zero_capacity(self, room_service, sample_room):
        sample_room.capacity = 0

        with pytest.raises(InvalidInputError, match="Invalid room data"):
            await room_service.add_room(sample_room)

    @pytest.mark.asyncio
    async def test_add_room_negative_capacity(self, room_service, sample_room):
        sample_room.capacity = -5

        with pytest.raises(InvalidInputError, match="Invalid room data"):
            await room_service.add_room(sample_room)

    @pytest.mark.asyncio
    async def test_add_room_empty_location(self, room_service, sample_room):
        sample_room.location = ""

        with pytest.raises(InvalidInputError, match="Invalid room data"):
            await room_service.add_room(sample_room)

    @pytest.mark.asyncio
    async def test_add_room_zero_room_number(self, room_service, sample_room):
        sample_room.room_number = 0

        with pytest.raises(InvalidInputError, match="Invalid room data"):
            await room_service.add_room(sample_room)

    @pytest.mark.asyncio
    async def test_add_room_negative_floor(self, room_service, sample_room):
        sample_room.floor = -1

        with pytest.raises(InvalidInputError, match="Invalid room data"):
            await room_service.add_room(sample_room)

    @pytest.mark.asyncio
    async def test_add_room_default_status(
        self, room_service, mock_room_repo, sample_room
    ):
        mock_room_repo.check_room_number_exists_on_floor.return_value = False
        sample_room.status = None
        sample_room.id = None

        await room_service.add_room(sample_room)

        assert sample_room.status == "Available"

    @pytest.mark.asyncio
    async def test_add_room_default_amenities(
        self, room_service, mock_room_repo, sample_room
    ):
        mock_room_repo.check_room_number_exists_on_floor.return_value = False
        sample_room.amenities = None
        sample_room.id = None

        await room_service.add_room(sample_room)

        assert sample_room.amenities == []

    @pytest.mark.asyncio
    async def test_get_all_rooms_success(
        self, room_service, mock_room_repo, sample_room
    ):
        mock_room_repo.get_all.return_value = [sample_room]

        rooms = await room_service.get_all_rooms()

        assert len(rooms) == 1
        assert rooms[0] == sample_room

    @pytest.mark.asyncio
    async def test_get_all_rooms_empty(self, room_service, mock_room_repo):
        mock_room_repo.get_all.return_value = []

        rooms = await room_service.get_all_rooms()

        assert rooms == []

    @pytest.mark.asyncio
    async def test_get_all_rooms_none(self, room_service, mock_room_repo):
        mock_room_repo.get_all.return_value = None

        rooms = await room_service.get_all_rooms()

        assert rooms == []

    @pytest.mark.asyncio
    async def test_get_room_by_id_success(
        self, room_service, mock_room_repo, sample_room
    ):
        mock_room_repo.get_by_id.return_value = sample_room

        room = await room_service.get_room_by_id("room-123")

        assert room == sample_room
        mock_room_repo.get_by_id.assert_called_once_with("room-123")

    @pytest.mark.asyncio
    async def test_get_room_by_id_not_found(self, room_service, mock_room_repo):
        mock_room_repo.get_by_id.return_value = None

        with pytest.raises(NotFoundError, match="Room not found"):
            await room_service.get_room_by_id("room-999")

    @pytest.mark.asyncio
    async def test_get_room_by_id_empty_id(self, room_service):
        with pytest.raises(InvalidInputError, match="Room ID is required"):
            await room_service.get_room_by_id("")

    @pytest.mark.asyncio
    async def test_update_room_success(self, room_service, mock_room_repo, sample_room):
        mock_room_repo.get_by_id.return_value = sample_room
        update_data = AsyncMock()
        update_data.name = "Updated Room"
        update_data.capacity = 15
        update_data.amenities = ["TV"]
        update_data.status = "maintenance"
        update_data.location = "Building 2"
        update_data.description = "Updated description"

        await room_service.update_room("room-123", update_data)

        assert sample_room.name == "Updated Room"
        assert sample_room.capacity == 15
        assert sample_room.amenities == ["TV"]
        assert sample_room.status == "maintenance"
        assert sample_room.location == "Building 2"
        assert sample_room.description == "Updated description"
        mock_room_repo.update.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_room_partial_update(
        self, room_service, mock_room_repo, sample_room
    ):
        mock_room_repo.get_by_id.return_value = sample_room
        update_data = AsyncMock()
        update_data.name = "New Name"
        update_data.capacity = None
        update_data.amenities = None
        update_data.status = None
        update_data.location = None
        update_data.description = None

        await room_service.update_room("room-123", update_data)

        assert sample_room.name == "New Name"
        assert sample_room.capacity == 10
        mock_room_repo.update.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_room_empty_id(self, room_service):
        update_data = AsyncMock()

        with pytest.raises(InvalidInputError, match="Room ID is required"):
            await room_service.update_room("", update_data)

    @pytest.mark.asyncio
    async def test_delete_room_success(self, room_service, mock_room_repo):
        await room_service.delete_room_by_id("room-123")

        mock_room_repo.delete_by_id.assert_called_once_with("room-123")

    @pytest.mark.asyncio
    async def test_delete_room_empty_id(self, room_service):
        with pytest.raises(InvalidInputError, match="Room ID is required"):
            await room_service.delete_room_by_id("")
