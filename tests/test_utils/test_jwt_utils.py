import pytest
import jwt
from datetime import datetime, timezone, timedelta
from app.utils import jwt_utils
from app.config.config import settings


class TestJWTUtils:

    def test_generate_token_success(self):
        token = jwt_utils.generate_token("user-123", "admin")

        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0

    def test_generate_token_contains_correct_payload(self):
        user_id = "user-456"
        role = "user"

        token = jwt_utils.generate_token(user_id, role)
        decoded = jwt.decode(token, settings.JWT_SECRET, algorithms=["HS256"])

        assert decoded["user_id"] == user_id
        assert decoded["role"] == role
        assert "exp" in decoded
        assert "iat" in decoded

    def test_generate_token_has_expiration(self):
        token = jwt_utils.generate_token("user-789", "admin")
        decoded = jwt.decode(token, settings.JWT_SECRET, algorithms=["HS256"])

        exp_time = datetime.fromtimestamp(decoded["exp"], tz=timezone.utc)
        iat_time = datetime.fromtimestamp(decoded["iat"], tz=timezone.utc)
        expected_delta = timedelta(hours=settings.JWT_EXPIRATION_HOURS)
        actual_delta = exp_time - iat_time

        assert abs((actual_delta - expected_delta).total_seconds()) < 2

    def test_validate_token_success(self):
        user_id = "user-123"
        role = "admin"
        token = jwt_utils.generate_token(user_id, role)

        payload = jwt_utils.validate_token(token)

        assert payload is not None
        assert payload["user_id"] == user_id
        assert payload["role"] == role

    def test_validate_token_expired(self):
        expired_token = jwt.encode(
            {
                "user_id": "user-123",
                "role": "admin",
                "exp": datetime.now(timezone.utc) - timedelta(hours=1),
                "iat": datetime.now(timezone.utc) - timedelta(hours=2),
            },
            settings.JWT_SECRET,
            algorithm="HS256",
        )

        payload = jwt_utils.validate_token(expired_token)

        assert payload is None

    def test_validate_token_invalid_signature(self):
        invalid_token = jwt.encode(
            {
                "user_id": "user-123",
                "role": "admin",
                "exp": datetime.now(timezone.utc) + timedelta(hours=1),
            },
            "wrong-secret",
            algorithm="HS256",
        )

        payload = jwt_utils.validate_token(invalid_token)

        assert payload is None

    def test_validate_token_malformed(self):
        malformed_token = "not.a.valid.token"

        payload = jwt_utils.validate_token(malformed_token)

        assert payload is None

    def test_validate_token_empty_string(self):
        payload = jwt_utils.validate_token("")

        assert payload is None

    def test_generate_token_different_roles(self):
        admin_token = jwt_utils.generate_token("user-1", "admin")
        user_token = jwt_utils.generate_token("user-2", "user")

        admin_payload = jwt_utils.validate_token(admin_token)
        user_payload = jwt_utils.validate_token(user_token)

        assert admin_payload["role"] == "admin"
        assert user_payload["role"] == "user"

    def test_generate_token_unique_for_different_users(self):
        token1 = jwt_utils.generate_token("user-1", "admin")
        token2 = jwt_utils.generate_token("user-2", "admin")

        assert token1 != token2
