from fastapi import APIRouter, Depends
from typing import List, Dict, Any
from app.services.users_service import UserService
from app.models.models import User
from app.models.pydantic_models import RegisterUserRequest, UserDTO, GenericResponse
from app.utils.dependencies import get_user_service
from app.utils.auth_middleware import require_admin, require_user
from app.utils.errors import InvalidInputError, NotFoundError, ConflictError


users_router: APIRouter = APIRouter(prefix="/api", tags=["Users"])


@users_router.post("/users/register", response_model=GenericResponse, status_code=201)
async def register(
    request: RegisterUserRequest,
    user_service: UserService = Depends(get_user_service),
    current_user: Dict[str, Any] = Depends(require_admin),
) -> GenericResponse:
    user: User = User(
        name=request.name,
        email=request.email,
        password=request.password,
        role=request.role,
    )
    user_service.register(user)
    return GenericResponse(message="user registered successfully")


@users_router.get("/users", response_model=List[UserDTO])
async def get_all_users(
    user_service: UserService = Depends(get_user_service),
    current_user: Dict[str, Any] = Depends(require_admin),
) -> List[UserDTO]:
    users: List[User] = user_service.get_all_users()
    return [UserDTO(**u.model_dump(exclude={"password"})) for u in users]


@users_router.get("/users/{user_id}", response_model=UserDTO)
async def get_user_by_id(
    user_id: str,
    user_service: UserService = Depends(get_user_service),
    current_user: Dict[str, Any] = Depends(require_user),
) -> UserDTO:
    user: User = user_service.get_user_by_id(user_id)
    return UserDTO(**user.model_dump(exclude={"password"}))


@users_router.delete("/users/{id}", response_model=GenericResponse)
async def delete_user_by_id(
    id: str,
    user_service: UserService = Depends(get_user_service),
    current_user: Dict[str, Any] = Depends(require_admin),
) -> GenericResponse:
    user_service.delete_user_by_id(id)
    return GenericResponse(message="user deleted successfully")
