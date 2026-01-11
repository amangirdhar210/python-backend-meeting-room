import pytest
from unittest.mock import AsyncMock
from app.services.auth_service import AuthService
from app.models.models import User
from app.utils.errors import InvalidInputError, UnauthorizedError


class TestAuthService:

    @pytest.fixture
    def mock_user_repo(self):
        return AsyncMock()

    @pytest.fixture
    def auth_service(self, mock_user_repo):
        return AuthService(mock_user_repo)

    @pytest.fixture
    def sample_user(self):
        from app.utils import password_utils

        return User(
            id="user-123",
            email="test@example.com",
            password=password_utils.hash_password("correct_password"),
            name="Test User",
            role="user",
            created_at=1704067200,
            updated_at=1704067200,
        )

    @pytest.mark.asyncio
    async def test_login_success(self, auth_service, mock_user_repo, sample_user):
        mock_user_repo.find_by_email.return_value = sample_user

        token, user = await auth_service.login("test@example.com", "correct_password")

        assert token is not None
        assert isinstance(token, str)
        assert user == sample_user
        mock_user_repo.find_by_email.assert_called_once_with("test@example.com")

    @pytest.mark.asyncio
    async def test_login_email_not_found(self, auth_service, mock_user_repo):
        mock_user_repo.find_by_email.return_value = None

        with pytest.raises(UnauthorizedError, match="Invalid credentials"):
            await auth_service.login("nonexistent@example.com", "password")

    @pytest.mark.asyncio
    async def test_login_incorrect_password(
        self, auth_service, mock_user_repo, sample_user
    ):
        mock_user_repo.find_by_email.return_value = sample_user

        with pytest.raises(UnauthorizedError, match="Invalid credentials"):
            await auth_service.login("test@example.com", "wrong_password")

    @pytest.mark.asyncio
    async def test_login_empty_email(self, auth_service):
        with pytest.raises(InvalidInputError, match="Email and password are required"):
            await auth_service.login("", "password")

    @pytest.mark.asyncio
    async def test_login_empty_password(self, auth_service):
        with pytest.raises(InvalidInputError, match="Email and password are required"):
            await auth_service.login("test@example.com", "")

    @pytest.mark.asyncio
    async def test_login_whitespace_only_email(self, auth_service):
        with pytest.raises(InvalidInputError, match="Email and password are required"):
            await auth_service.login("   ", "password")

    @pytest.mark.asyncio
    async def test_login_whitespace_only_password(self, auth_service):
        with pytest.raises(InvalidInputError, match="Email and password are required"):
            await auth_service.login("test@example.com", "   ")

    @pytest.mark.asyncio
    async def test_login_trims_whitespace(
        self, auth_service, mock_user_repo, sample_user
    ):
        mock_user_repo.find_by_email.return_value = sample_user

        await auth_service.login("  test@example.com  ", "  correct_password  ")

        mock_user_repo.find_by_email.assert_called_once_with("test@example.com")

    @pytest.mark.asyncio
    async def test_login_returns_correct_user_data(
        self, auth_service, mock_user_repo, sample_user
    ):
        mock_user_repo.find_by_email.return_value = sample_user

        token, user = await auth_service.login("test@example.com", "correct_password")

        assert user.id == "user-123"
        assert user.email == "test@example.com"
        assert user.name == "Test User"
        assert user.role == "user"
