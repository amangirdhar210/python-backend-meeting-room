import pytest
from app.utils import password_utils


class TestPasswordUtils:

    def test_hash_password_success(self):
        password = "secure_password_123"

        hashed = password_utils.hash_password(password)

        assert hashed is not None
        assert isinstance(hashed, str)
        assert hashed != password
        assert len(hashed) > 0

    def test_hash_password_different_hashes_for_same_password(self):
        password = "test_password"

        hash1 = password_utils.hash_password(password)
        hash2 = password_utils.hash_password(password)

        assert hash1 != hash2

    def test_hash_password_empty_raises_error(self):
        with pytest.raises(ValueError, match="Password cannot be empty"):
            password_utils.hash_password("")

    def test_hash_password_none_raises_error(self):
        with pytest.raises(ValueError, match="Password cannot be empty"):
            password_utils.hash_password(None)

    def test_verify_password_correct_password(self):
        password = "my_secure_password"
        hashed = password_utils.hash_password(password)

        result = password_utils.verify_password(hashed, password)

        assert result is True

    def test_verify_password_incorrect_password(self):
        password = "correct_password"
        wrong_password = "wrong_password"
        hashed = password_utils.hash_password(password)

        result = password_utils.verify_password(hashed, wrong_password)

        assert result is False

    def test_verify_password_case_sensitive(self):
        password = "MyPassword"
        hashed = password_utils.hash_password(password)

        result = password_utils.verify_password(hashed, "mypassword")

        assert result is False

    def test_verify_password_invalid_hash_format(self):
        invalid_hash = "not_a_valid_hash"
        password = "test_password"

        result = password_utils.verify_password(invalid_hash, password)

        assert result is False

    def test_verify_password_empty_password(self):
        hashed = password_utils.hash_password("test")

        result = password_utils.verify_password(hashed, "")

        assert result is False

    def test_verify_password_empty_hash(self):
        result = password_utils.verify_password("", "password")

        assert result is False

    def test_hash_password_special_characters(self):
        password = "P@ssw0rd!#$%^&*()"
        hashed = password_utils.hash_password(password)

        result = password_utils.verify_password(hashed, password)

        assert result is True

    def test_hash_password_unicode_characters(self):
        password = "пароль密码🔒"
        hashed = password_utils.hash_password(password)

        result = password_utils.verify_password(hashed, password)

        assert result is True

    def test_hash_password_within_bcrypt_limit(self):
        password = "a" * 70
        hashed = password_utils.hash_password(password)

        result = password_utils.verify_password(hashed, password)

        assert result is True
