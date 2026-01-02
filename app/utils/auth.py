from typing import Optional


class JWTGenerator:

    def __init__(self, secret: str, expiration_time: int):
        pass

    def generate_token(self, user_id: str, role: str) -> str:
        pass

    def validate_token(self, token: str) -> Optional[dict]:
        pass
