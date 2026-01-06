from fastapi import HTTPException, Header, Depends
from typing import Optional
from app.utils.jwt_utils import jwt_generator


def get_current_user(authorization: Optional[str] = Header(None)):
    if not authorization:
        raise HTTPException(status_code=401, detail="unauthorized")

    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="unauthorized")

    token = authorization.replace("Bearer ", "")

    payload = jwt_generator.validate_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="unauthorized")

    return payload


def require_admin(current_user: dict = Depends(get_current_user)):
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="forbidden")
    return current_user


def require_user(current_user: dict = Depends(get_current_user)):
    return current_user
