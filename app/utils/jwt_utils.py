from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
import jwt
from app.config.config import settings


def generate_token(user_id: str, role: str) -> str:
    expiration_time: datetime = datetime.now(timezone.utc) + timedelta(
        hours=settings.JWT_EXPIRATION_HOURS
    )
    payload: Dict[str, Any] = {
        "user_id": user_id,
        "role": role,
        "exp": expiration_time,
        "iat": datetime.now(timezone.utc),
    }
    token: str = jwt.encode(payload, settings.JWT_SECRET, algorithm="HS256")
    return token


def validate_token(token: str) -> Optional[Dict[str, Any]]:
    try:
        payload: Dict[str, Any] = jwt.decode(
            token, settings.JWT_SECRET, algorithms=["HS256"]
        )
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None
