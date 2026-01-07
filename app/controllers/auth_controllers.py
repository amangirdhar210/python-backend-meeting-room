from typing import Dict, Any
from fastapi import APIRouter, Depends
from app.models.pydantic_models import LoginUserRequest, LoginUserResponse, UserDTO
from app.services.auth_service import AuthService
from app.utils.dependencies import get_auth_service
from app.utils.errors import InvalidInputError, UnauthorizedError


auth_router: APIRouter = APIRouter(tags=["Authentication"])


@auth_router.post("/login", response_model=LoginUserResponse)
async def login(
    request: LoginUserRequest, auth_service: AuthService = Depends(get_auth_service)
) -> LoginUserResponse:
    token, user = auth_service.login(request.email, request.password)

    return LoginUserResponse(
        token=token,
        user=UserDTO(
            id=user.id,
            name=user.name,
            email=user.email,
            role=user.role,
            created_at=user.created_at,
            updated_at=user.updated_at,
        ),
    )


@auth_router.get("/health")
async def health_check() -> Dict[str, str]:
    return {"status": "ok"}
