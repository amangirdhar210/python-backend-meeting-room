import pytest
from unittest.mock import AsyncMock, patch
from app.services.users_service import UserService
from app.models.models import User
from app.utils.errors import InvalidInputError, NotFoundError, ConflictError


class TestUserService:

    @pytest.fixture
    def mock_user_repo(self):
        return AsyncMock()

    @pytest.fixture
    def mock_booking_repo(self):
        return AsyncMock()

    @pytest.fixture
    def user_service(self, mock_user_repo, mock_booking_repo):
        return UserService(mock_user_repo, mock_booking_repo)

    @pytest.fixture
    def sample_user(self):
        return User(
            id="user-1234567890",
            email="test@example.com",
            password="plainpassword",
            name="Test User",
            role="user",
            created_at=1704067200,
            updated_at=1704067200,
        )

    @pytest.mark.asyncio
    async def test_register_success(self, user_service, mock_user_repo, sample_user):
        mock_user_repo.find_by_email.side_effect = NotFoundError("Not found")

        await user_service.register(sample_user)

        mock_user_repo.create.assert_called_once()
        assert sample_user.id is not None
        assert len(sample_user.id) > 10

    @pytest.mark.asyncio
    async def test_register_hashes_password(
        self, user_service, mock_user_repo, sample_user
    ):
        mock_user_repo.find_by_email.side_effect = NotFoundError("Not found")
        original_password = sample_user.password

        await user_service.register(sample_user)

        assert sample_user.password != original_password
        assert sample_user.password.startswith("$2b$")

    @pytest.mark.asyncio
    async def test_register_duplicate_email(
        self, user_service, mock_user_repo, sample_user
    ):
        mock_user_repo.find_by_email.return_value = sample_user

        with pytest.raises(ConflictError, match="User already exists"):
            await user_service.register(sample_user)

    @pytest.mark.asyncio
    async def test_register_missing_email(self, user_service, sample_user):
        sample_user.email = ""

        with pytest.raises(InvalidInputError, match="All fields are required"):
            await user_service.register(sample_user)

    @pytest.mark.asyncio
    async def test_register_missing_password(self, user_service, sample_user):
        sample_user.password = ""

        with pytest.raises(InvalidInputError, match="All fields are required"):
            await user_service.register(sample_user)

    @pytest.mark.asyncio
    async def test_register_missing_name(self, user_service, sample_user):
        sample_user.name = ""

        with pytest.raises(InvalidInputError, match="All fields are required"):
            await user_service.register(sample_user)

    @pytest.mark.asyncio
    async def test_register_missing_role(self, user_service, sample_user):
        sample_user.role = ""

        with pytest.raises(InvalidInputError, match="All fields are required"):
            await user_service.register(sample_user)

    @pytest.mark.asyncio
    async def test_register_none_user(self, user_service):
        with pytest.raises(InvalidInputError, match="User is required"):
            await user_service.register(None)

    @pytest.mark.asyncio
    async def test_register_sets_timestamps(
        self, user_service, mock_user_repo, sample_user
    ):
        mock_user_repo.find_by_email.side_effect = NotFoundError("Not found")

        await user_service.register(sample_user)

        assert sample_user.created_at > 0
        assert sample_user.updated_at > 0

    @pytest.mark.asyncio
    async def test_get_all_users_success(
        self, user_service, mock_user_repo, sample_user
    ):
        mock_user_repo.get_all.return_value = [sample_user]

        users = await user_service.get_all_users()

        assert len(users) == 1
        assert users[0] == sample_user

    @pytest.mark.asyncio
    async def test_get_all_users_empty(self, user_service, mock_user_repo):
        mock_user_repo.get_all.return_value = []

        with pytest.raises(NotFoundError, match="No users found"):
            await user_service.get_all_users()

    @pytest.mark.asyncio
    async def test_get_all_users_none(self, user_service, mock_user_repo):
        mock_user_repo.get_all.return_value = None

        with pytest.raises(NotFoundError, match="No users found"):
            await user_service.get_all_users()

    @pytest.mark.asyncio
    async def test_get_user_by_id_success(
        self, user_service, mock_user_repo, sample_user
    ):
        mock_user_repo.get_by_id.return_value = sample_user

        user = await user_service.get_user_by_id("user-1234567890")

        assert user == sample_user
        mock_user_repo.get_by_id.assert_called_once_with("user-1234567890")

    @pytest.mark.asyncio
    async def test_get_user_by_id_invalid_id(self, user_service):
        with pytest.raises(InvalidInputError, match="Invalid user ID"):
            await user_service.get_user_by_id("short")

    @pytest.mark.asyncio
    async def test_get_user_by_id_empty_id(self, user_service):
        with pytest.raises(InvalidInputError, match="Invalid user ID"):
            await user_service.get_user_by_id("")

    @pytest.mark.asyncio
    async def test_update_user_success(self, user_service, mock_user_repo, sample_user):
        mock_user_repo.get_by_id.return_value = sample_user
        update_data = AsyncMock()
        update_data.email = None
        update_data.name = "Updated Name"
        update_data.role = None

        await user_service.update_user("user-123", update_data)

        assert sample_user.name == "Updated Name"
        mock_user_repo.update.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_user_cannot_edit_self(
        self, user_service, mock_user_repo, sample_user
    ):
        mock_user_repo.get_by_id.return_value = sample_user
        update_data = AsyncMock()

        with pytest.raises(InvalidInputError, match="You cannot edit your own account"):
            await user_service.update_user(
                "user-123", update_data, current_user_id="user-123"
            )

    @pytest.mark.asyncio
    async def test_update_user_cannot_edit_superadmin(
        self, user_service, mock_user_repo
    ):
        superadmin = User(
            id="admin-1234567890",
            email="admin@example.com",
            password="hash",
            name="Admin",
            role="admin",
            created_at=1704067200,
            updated_at=1704067200,
        )
        mock_user_repo.get_by_id.return_value = superadmin
        update_data = AsyncMock()
        update_data.email = None
        update_data.name = None
        update_data.role = None

        with pytest.raises(
            InvalidInputError, match="Superadmin accounts cannot be updated"
        ):
            await user_service.update_user("admin-1234567890", update_data)

    @pytest.mark.asyncio
    async def test_update_user_email_conflict(
        self, user_service, mock_user_repo, sample_user
    ):
        mock_user_repo.get_by_id.return_value = sample_user
        mock_user_repo.find_by_email.return_value = User(
            id="other-user",
            email="other@example.com",
            password="hash",
            name="Other",
            role="user",
            created_at=1704067200,
            updated_at=1704067200,
        )
        update_data = AsyncMock()
        update_data.email = "other@example.com"
        update_data.name = None
        update_data.role = None

        with pytest.raises(ConflictError, match="Email already in use"):
            await user_service.update_user("user-123", update_data)

    @pytest.mark.asyncio
    async def test_delete_user_success(
        self, user_service, mock_user_repo, mock_booking_repo, sample_user
    ):
        mock_user_repo.get_by_id.return_value = sample_user

        await user_service.delete_user_by_id("user-123")

        mock_booking_repo.delete_by_user_id.assert_called_once_with("user-123")
        mock_user_repo.delete_by_id.assert_called_once_with("user-123")

    @pytest.mark.asyncio
    async def test_delete_user_cannot_delete_self(
        self, user_service, mock_user_repo, sample_user
    ):
        mock_user_repo.get_by_id.return_value = sample_user

        with pytest.raises(
            InvalidInputError, match="You cannot delete your own account"
        ):
            await user_service.delete_user_by_id("user-123", current_user_id="user-123")

    @pytest.mark.asyncio
    async def test_delete_user_empty_id(self, user_service):
        with pytest.raises(InvalidInputError, match="User ID is required"):
            await user_service.delete_user_by_id("")
