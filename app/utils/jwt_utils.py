from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
import jwt
from app.config.config import settings


class JWTGenerator:
    def __init__(self, secret: str, expiration_hours: int = 24) -> None:
        self.secret: str = secret
        self.expiration_hours: int = expiration_hours

    def generate_token(self, user_id: str, role: str) -> str:
        expiration_time: datetime = datetime.now(timezone.utc) + timedelta(
            hours=self.expiration_hours
        )
        payload: Dict[str, Any] = {
            "user_id": user_id,
            "role": role,
            "exp": expiration_time,
            "iat": datetime.now(timezone.utc),
        }
        token: str = jwt.encode(payload, self.secret, algorithm="HS256")
        return token

    def validate_token(self, token: str) -> Optional[Dict[str, Any]]:
        try:
            payload: Dict[str, Any] = jwt.decode(
                token, self.secret, algorithms=["HS256"]
            )
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None


jwt_generator: JWTGenerator = JWTGenerator(
    settings.JWT_SECRET, settings.JWT_EXPIRATION_HOURS
)
