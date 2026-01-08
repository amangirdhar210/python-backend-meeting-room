from fastapi import HTTPException, Header, Depends, Request
from typing import Optional, Dict, Any
from app.utils import jwt_utils


def get_current_user(authorization: Optional[str] = Header(None)) -> Dict[str, Any]:
    if not authorization:
        raise HTTPException(status_code=401, detail="unauthorized")

    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="unauthorized")

    token: str = authorization.replace("Bearer ", "")

    payload: Optional[Dict[str, Any]] = jwt_utils.validate_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="unauthorized")

    return payload


async def set_current_user(
    request: Request,
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> None:
    request.state.user = current_user


async def require_admin_state(request: Request) -> None:
    if not hasattr(request.state, "user"):
        raise HTTPException(status_code=401, detail="unauthorized")
    if request.state.user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="forbidden")
