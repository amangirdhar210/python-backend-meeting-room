import pytest
import asyncio
from unittest.mock import MagicMock, AsyncMock
from botocore.exceptions import ClientError
from app.repositories.users_repo import UserRepository
from app.models.models import User
from app.utils.errors import NotFoundError, InvalidInputError, ConflictError


class TestUserRepository:

    @pytest.fixture
    def mock_table(self):
        table = MagicMock()
        table.table_name = "TestTable"
        table.meta.client.transact_write_items = MagicMock()
        return table

    @pytest.fixture
    def user_repo(self, mock_table):
        mock_dynamodb = MagicMock()
        mock_dynamodb.Table.return_value = mock_table
        return UserRepository(mock_dynamodb, "TestTable")

    @pytest.fixture
    def sample_user(self):
        return User(
            id="user-1234567890",
            name="John Doe",
            email="john@example.com",
            password="hashed_password",
            role="user",
            created_at=1704067200,
            updated_at=1704067200,
        )

    def test_create_user_success(self, user_repo, mock_table, sample_user):
        asyncio.run(user_repo.create(sample_user))

        mock_table.meta.client.transact_write_items.assert_called_once()
        call_args = mock_table.meta.client.transact_write_items.call_args[1]
        items = call_args["TransactItems"]

        assert len(items) == 2
        assert items[0]["Put"]["Item"]["PK"] == "USER"
        assert items[0]["Put"]["Item"]["SK"] == "john@example.com"
        assert items[0]["Put"]["Item"]["ID"] == "user-1234567890"
        assert items[1]["Put"]["Item"]["SK"] == "USER#user-1234567890"
        assert items[1]["Put"]["Item"]["Email"] == "john@example.com"

    def test_create_user_none_raises_error(self, user_repo):
        with pytest.raises(InvalidInputError, match="User is required"):
            asyncio.run(user_repo.create(None))

    def test_get_by_id_success(self, user_repo, mock_table, sample_user):
        mock_table.query.return_value = {
            "Items": [
                {
                    "PK": "USER",
                    "SK": "USER#user-1234567890",
                    "ID": "user-1234567890",
                    "Name": "John Doe",
                    "Email": "john@example.com",
                    "Password": "hashed_password",
                    "Role": "user",
                    "CreatedAt": 1704067200,
                    "UpdatedAt": 1704067200,
                }
            ]
        }

        user = asyncio.run(user_repo.get_by_id("user-1234567890"))

        assert user.id == "user-1234567890"
        assert user.name == "John Doe"
        assert user.email == "john@example.com"
        assert user.role == "user"

    def test_get_by_id_not_found(self, user_repo, mock_table):
        mock_table.query.return_value = {"Items": []}

        with pytest.raises(NotFoundError, match="User not found"):
            asyncio.run(user_repo.get_by_id("nonexistent-user"))

    def test_get_by_id_empty_id(self, user_repo):
        with pytest.raises(InvalidInputError, match="User ID is required"):
            asyncio.run(user_repo.get_by_id(""))

    def test_find_by_email_success(self, user_repo, mock_table):
        mock_table.query.side_effect = [
            {"Items": [{"ID": "user-1234567890"}]},
            {
                "Items": [
                    {
                        "ID": "user-1234567890",
                        "Name": "John Doe",
                        "Email": "john@example.com",
                        "Password": "hashed_password",
                        "Role": "user",
                        "CreatedAt": 1704067200,
                        "UpdatedAt": 1704067200,
                    }
                ]
            },
        ]

        user = asyncio.run(user_repo.find_by_email("john@example.com"))

        assert user.email == "john@example.com"
        assert user.id == "user-1234567890"

    def test_find_by_email_not_found(self, user_repo, mock_table):
        mock_table.query.return_value = {"Items": []}

        with pytest.raises(NotFoundError, match="User not found"):
            asyncio.run(user_repo.find_by_email("notfound@example.com"))

    def test_find_user_id_by_email_empty_email(self, user_repo):
        with pytest.raises(InvalidInputError, match="Email is required"):
            asyncio.run(user_repo.find_user_id_by_email(""))

    def test_get_all_users_success(self, user_repo, mock_table):
        mock_table.query.return_value = {
            "Items": [
                {
                    "ID": "user-1",
                    "Name": "User One",
                    "Email": "user1@example.com",
                    "Password": "hash1",
                    "Role": "user",
                    "CreatedAt": 1704067200,
                    "UpdatedAt": 1704067200,
                },
                {
                    "ID": "user-2",
                    "Name": "User Two",
                    "Email": "user2@example.com",
                    "Password": "hash2",
                    "Role": "admin",
                    "CreatedAt": 1704067300,
                    "UpdatedAt": 1704067300,
                },
            ]
        }

        users = asyncio.run(user_repo.get_all())

        assert len(users) == 2
        assert users[0].id == "user-1"
        assert users[1].id == "user-2"
        assert users[1].role == "admin"

    def test_get_all_users_empty(self, user_repo, mock_table):
        mock_table.query.return_value = {"Items": []}

        users = asyncio.run(user_repo.get_all())

        assert users == []

    def test_delete_by_id_success(self, user_repo, mock_table):
        mock_table.query.return_value = {
            "Items": [
                {
                    "ID": "user-1234567890",
                    "Name": "John Doe",
                    "Email": "john@example.com",
                    "Password": "hashed_password",
                    "Role": "user",
                    "CreatedAt": 1704067200,
                    "UpdatedAt": 1704067200,
                }
            ]
        }

        asyncio.run(user_repo.delete_by_id("user-1234567890"))

        assert mock_table.meta.client.transact_write_items.called

    def test_update_user_success(self, user_repo, mock_table, sample_user):
        asyncio.run(user_repo.update(sample_user, old_email="old@example.com"))

        assert mock_table.meta.client.transact_write_items.called
        call_args = mock_table.meta.client.transact_write_items.call_args[1]
        items = call_args["TransactItems"]

        assert len(items) == 3
        assert items[2]["Put"]["Item"]["Email"] == "john@example.com"
