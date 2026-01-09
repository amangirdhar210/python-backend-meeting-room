from typing import Dict
from fastapi import APIRouter, Depends
from app.models.pydantic_models import LoginUserRequest, LoginUserResponse, UserDTO
from app.services.auth_service import AuthService
from app.dependencies.dependencies import get_auth_service, AuthServiceInstance
from app.utils.errors import InvalidInputError, UnauthorizedError


auth_router: APIRouter = APIRouter(tags=["Authentication"])


@auth_router.post("/login", response_model=LoginUserResponse)
async def login(
    request: LoginUserRequest, auth_service: AuthServiceInstance
) -> LoginUserResponse:
    token, user = await auth_service.login(request.email, request.password)

    return LoginUserResponse(
        token=token,
        user=UserDTO(**user.model_dump(exclude={"password"})),
    )


@auth_router.get("/health")
async def health_check() -> Dict[str, str]:
    return {"status": "ok"}
