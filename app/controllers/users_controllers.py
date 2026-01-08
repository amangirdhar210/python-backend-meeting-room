from fastapi import APIRouter, Depends, Request
from typing import List
from app.models.models import User
from app.models.pydantic_models import RegisterUserRequest, UserDTO, GenericResponse
from app.services.users_service import UserService
from app.dependencies.dependencies import get_user_service
from app.middleware.auth_middleware import set_current_user, require_admin_state
from app.utils.errors import InvalidInputError, NotFoundError, ConflictError


users_router: APIRouter = APIRouter(
    prefix="/api",
    tags=["Users"],
    dependencies=[Depends(set_current_user)],
)


@users_router.post(
    "/users/register",
    response_model=GenericResponse,
    status_code=201,
    dependencies=[Depends(require_admin_state)],
)
async def register(
    req: Request,
    request: RegisterUserRequest,
    user_service: UserService = Depends(get_user_service),
) -> GenericResponse:
    user: User = User(
        name=request.name,
        email=request.email,
        password=request.password,
        role=request.role,
    )
    await user_service.register(user)
    return GenericResponse(message="user registered successfully")


@users_router.get(
    "/users", response_model=List[UserDTO], dependencies=[Depends(require_admin_state)]
)
async def get_all_users(
    req: Request,
    user_service: UserService = Depends(get_user_service),
) -> List[UserDTO]:
    users: List[User] = await user_service.get_all_users()
    return [UserDTO(**u.model_dump(exclude={"password"})) for u in users]


@users_router.get("/users/{user_id}", response_model=UserDTO)
async def get_user_by_id(
    req: Request,
    user_id: str,
    user_service: UserService = Depends(get_user_service),
) -> UserDTO:
    user: User = await user_service.get_user_by_id(user_id)
    return UserDTO(**user.model_dump(exclude={"password"}))


@users_router.delete(
    "/users/{id}",
    response_model=GenericResponse,
    dependencies=[Depends(require_admin_state)],
)
async def delete_user_by_id(
    req: Request,
    id: str,
    user_service: UserService = Depends(get_user_service),
) -> GenericResponse:
    await user_service.delete_user_by_id(id)
    return GenericResponse(message="user deleted successfully")
