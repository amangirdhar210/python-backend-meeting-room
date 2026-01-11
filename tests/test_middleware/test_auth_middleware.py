import pytest
import asyncio
from unittest.mock import Mock, patch
from fastapi import HTTPException, Request
from app.middleware.auth_middleware import (
    get_current_user,
    set_current_user,
    require_admin_state,
)
from app.utils import jwt_utils


class TestAuthMiddleware:

    def test_get_current_user_success(self):
        token = jwt_utils.generate_token("user-123", "admin")
        authorization = f"Bearer {token}"

        result = get_current_user(authorization)

        assert result is not None
        assert result["user_id"] == "user-123"
        assert result["role"] == "admin"

    def test_get_current_user_no_authorization_header(self):
        with pytest.raises(HTTPException) as exc_info:
            get_current_user(None)

        assert exc_info.value.status_code == 401
        assert exc_info.value.detail == "unauthorized"

    def test_get_current_user_missing_bearer_prefix(self):
        token = jwt_utils.generate_token("user-123", "admin")

        with pytest.raises(HTTPException) as exc_info:
            get_current_user(token)

        assert exc_info.value.status_code == 401
        assert exc_info.value.detail == "unauthorized"

    def test_get_current_user_invalid_token(self):
        authorization = "Bearer invalid.token.here"

        with pytest.raises(HTTPException) as exc_info:
            get_current_user(authorization)

        assert exc_info.value.status_code == 401
        assert exc_info.value.detail == "unauthorized"

    def test_get_current_user_expired_token(self):
        with patch("app.utils.jwt_utils.validate_token", return_value=None):
            token = jwt_utils.generate_token("user-123", "admin")
            authorization = f"Bearer {token}"

            with pytest.raises(HTTPException) as exc_info:
                get_current_user(authorization)

            assert exc_info.value.status_code == 401
            assert exc_info.value.detail == "unauthorized"

    def test_get_current_user_empty_bearer_token(self):
        authorization = "Bearer "

        with pytest.raises(HTTPException) as exc_info:
            get_current_user(authorization)

        assert exc_info.value.status_code == 401
        assert exc_info.value.detail == "unauthorized"

    def test_set_current_user_success(self):
        request = Mock(spec=Request)
        request.state = Mock()
        current_user = {"user_id": "user-123", "role": "admin"}

        asyncio.run(set_current_user(request, current_user))

        assert request.state.user == current_user

    def test_set_current_user_regular_user(self):
        request = Mock(spec=Request)
        request.state = Mock()
        current_user = {"user_id": "user-456", "role": "user"}

        asyncio.run(set_current_user(request, current_user))

        assert request.state.user == current_user
        assert request.state.user["role"] == "user"

    def test_require_admin_state_success(self):
        request = Mock(spec=Request)
        request.state = Mock()
        request.state.user = {"user_id": "admin-123", "role": "admin"}

        asyncio.run(require_admin_state(request))

    def test_require_admin_state_no_user_in_state(self):
        request = Mock(spec=Request)
        request.state = Mock(spec=[])

        with pytest.raises(HTTPException) as exc_info:
            asyncio.run(require_admin_state(request))

        assert exc_info.value.status_code == 401
        assert exc_info.value.detail == "unauthorized"

    def test_require_admin_state_user_not_admin(self):
        request = Mock(spec=Request)
        request.state = Mock()
        request.state.user = {"user_id": "user-123", "role": "user"}

        with pytest.raises(HTTPException) as exc_info:
            asyncio.run(require_admin_state(request))

        assert exc_info.value.status_code == 403
        assert exc_info.value.detail == "forbidden"

    def test_require_admin_state_missing_role(self):
        request = Mock(spec=Request)
        request.state = Mock()
        request.state.user = {"user_id": "user-123"}

        with pytest.raises(HTTPException) as exc_info:
            asyncio.run(require_admin_state(request))

        assert exc_info.value.status_code == 403
        assert exc_info.value.detail == "forbidden"

    def test_require_admin_state_empty_role(self):
        request = Mock(spec=Request)
        request.state = Mock()
        request.state.user = {"user_id": "user-123", "role": ""}

        with pytest.raises(HTTPException) as exc_info:
            asyncio.run(require_admin_state(request))

        assert exc_info.value.status_code == 403
        assert exc_info.value.detail == "forbidden"
