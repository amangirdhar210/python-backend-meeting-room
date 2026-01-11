import pytest
import asyncio
from unittest.mock import MagicMock
from botocore.exceptions import ClientError
from app.repositories.rooms_repo import RoomRepository
from app.models.models import Room
from app.utils.errors import NotFoundError, InvalidInputError, ConflictError


class TestRoomRepository:

    @pytest.fixture
    def mock_table(self):
        table = MagicMock()
        table.table_name = "TestTable"
        mock_client = MagicMock()
        mock_client.exceptions.ConditionalCheckFailedException = ClientError
        table.meta.client = mock_client
        return table

    @pytest.fixture
    def room_repo(self, mock_table):
        mock_dynamodb = MagicMock()
        mock_dynamodb.Table.return_value = mock_table
        mock_dynamodb.meta.client = mock_table.meta.client
        return RoomRepository(mock_dynamodb, "TestTable")

    @pytest.fixture
    def sample_room(self):
        return Room(
            id="room-1234567890",
            name="Conference Room A",
            room_number=101,
            capacity=10,
            floor=1,
            amenities=["Projector", "Whiteboard"],
            status="available",
            location="Building 1",
            description="Main conference room",
            created_at=1704067200,
            updated_at=1704067200,
        )

    def test_create_room_success(self, room_repo, mock_table, sample_room):
        asyncio.run(room_repo.create(sample_room))

        mock_table.put_item.assert_called_once()
        call_args = mock_table.put_item.call_args[1]
        item = call_args["Item"]

        assert item["PK"] == "ROOM"
        assert item["SK"] == "ROOM#room-1234567890"
        assert item["ID"] == "room-1234567890"
        assert item["Name"] == "Conference Room A"
        assert item["RoomNumber"] == 101
        assert item["Capacity"] == 10
        assert item["Floor"] == 1
        assert item["LSI1"] == 1
        assert item["LSI2"] == 10

    def test_create_room_none_raises_error(self, room_repo):
        with pytest.raises(InvalidInputError, match="Room is required"):
            asyncio.run(room_repo.create(None))

    def test_get_by_id_success(self, room_repo, mock_table):
        mock_table.get_item.return_value = {
            "Item": {
                "PK": "ROOM",
                "SK": "ROOM#room-123",
                "ID": "room-123",
                "Name": "Meeting Room",
                "RoomNumber": 101,
                "Capacity": 8,
                "Floor": 2,
                "Amenities": ["TV"],
                "Status": "available",
                "Location": "East Wing",
                "Description": "Small room",
                "CreatedAt": 1704067200,
                "UpdatedAt": 1704067200,
            }
        }

        room = asyncio.run(room_repo.get_by_id("room-123"))

        assert room.id == "room-123"
        assert room.name == "Meeting Room"
        assert room.room_number == 101
        assert room.capacity == 8
        assert room.floor == 2

    def test_get_by_id_not_found(self, room_repo, mock_table):
        mock_table.get_item.return_value = {}

        with pytest.raises(NotFoundError, match="Room not found"):
            asyncio.run(room_repo.get_by_id("nonexistent-room"))

    def test_get_by_id_empty_id(self, room_repo):
        with pytest.raises(InvalidInputError, match="Room ID is required"):
            asyncio.run(room_repo.get_by_id(""))

    def test_get_all_rooms_success(self, room_repo, mock_table):
        mock_table.query.return_value = {
            "Items": [
                {
                    "ID": "room-1",
                    "Name": "Room 1",
                    "RoomNumber": 101,
                    "Capacity": 10,
                    "Floor": 1,
                    "Amenities": ["Projector"],
                    "Status": "available",
                    "Location": "West",
                    "Description": "Room 1",
                    "CreatedAt": 1704067200,
                    "UpdatedAt": 1704067200,
                },
                {
                    "ID": "room-2",
                    "Name": "Room 2",
                    "RoomNumber": 102,
                    "Capacity": 5,
                    "Floor": 1,
                    "Amenities": [],
                    "Status": "maintenance",
                    "Location": "East",
                    "CreatedAt": 1704067300,
                    "UpdatedAt": 1704067300,
                },
            ]
        }

        rooms = asyncio.run(room_repo.get_all())

        assert len(rooms) == 2
        assert rooms[0].id == "room-1"
        assert rooms[1].status == "maintenance"

    def test_get_all_rooms_empty(self, room_repo, mock_table):
        mock_table.query.return_value = {}

        rooms = asyncio.run(room_repo.get_all())

        assert rooms == []

    def test_update_room_success(self, room_repo, mock_table, sample_room):
        asyncio.run(room_repo.update(sample_room))

        mock_table.put_item.assert_called_once()
        call_args = mock_table.put_item.call_args[1]
        item = call_args["Item"]

        assert item["SK"] == "ROOM#room-1234567890"
        assert item["UpdatedAt"] == 1704067200

    def test_delete_by_id_success(self, room_repo, mock_table):
        asyncio.run(room_repo.delete_by_id("room-123"))

        mock_table.delete_item.assert_called_once_with(
            Key={"PK": "ROOM", "SK": "ROOM#room-123"},
            ConditionExpression="attribute_exists(PK) AND attribute_exists(SK)",
        )

    def test_check_room_number_exists_on_floor_true(self, room_repo, mock_table):
        mock_table.query.return_value = {"Items": [{"ID": "room-123"}]}

        exists = asyncio.run(room_repo.check_room_number_exists_on_floor(101, 1))

        assert exists is True

    def test_check_room_number_exists_on_floor_false(self, room_repo, mock_table):
        mock_table.query.return_value = {"Items": []}

        exists = asyncio.run(room_repo.check_room_number_exists_on_floor(101, 1))

        assert exists is False
