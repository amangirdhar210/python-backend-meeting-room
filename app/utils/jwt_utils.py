from datetime import datetime, timedelta
from typing import Optional
import jwt
from app.config.config import settings


class JWTGenerator:
    def __init__(self, secret: str, expiration_hours: int = 24):
        self.secret = secret
        self.expiration_hours = expiration_hours

    def generate_token(self, user_id: str, role: str) -> str:
        expiration_time = datetime.utcnow() + timedelta(hours=self.expiration_hours)
        payload = {
            "user_id": user_id,
            "role": role,
            "exp": expiration_time,
            "iat": datetime.utcnow(),
        }
        token = jwt.encode(payload, self.secret, algorithm="HS256")
        return token

    def validate_token(self, token: str) -> Optional[dict]:
        try:
            payload = jwt.decode(token, self.secret, algorithms=["HS256"])
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None


jwt_generator = JWTGenerator(settings.JWT_SECRET, settings.JWT_EXPIRATION_HOURS)
