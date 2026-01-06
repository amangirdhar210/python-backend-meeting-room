from fastapi import APIRouter, Depends, HTTPException
from typing import List
from app.services.users_service import UserService
from app.models.models import User
from app.models.pydantic_models import RegisterUserRequest, UserDTO, GenericResponse
from app.utils.dependencies import get_user_service
from app.utils.auth_middleware import require_admin, require_user
from app.utils.errors import InvalidInputError, NotFoundError, ConflictError


users_router = APIRouter(prefix="/api", tags=["Users"])


@users_router.post("/users/register", response_model=GenericResponse, status_code=201)
async def register(
    request: RegisterUserRequest,
    user_service: UserService = Depends(get_user_service),
    current_user: dict = Depends(require_admin),
):
    try:
        user = User(
            id="",
            name=request.name,
            email=request.email,
            password=request.password,
            role=request.role,
            created_at=0,
            updated_at=0,
        )
        user_service.register(user)
        return GenericResponse(message="user registered successfully")
    except (InvalidInputError, ConflictError) as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Internal server error")


@users_router.get("/users", response_model=List[UserDTO])
async def get_all_users(
    user_service: UserService = Depends(get_user_service),
    current_user: dict = Depends(require_admin),
):
    try:
        users = user_service.get_all_users()
        return [
            UserDTO(
                id=u.id,
                name=u.name,
                email=u.email,
                role=u.role,
                created_at=u.created_at,
                updated_at=u.updated_at,
            )
            for u in users
        ]
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


@users_router.get("/users/{user_id}", response_model=UserDTO)
async def get_user_by_id(
    user_id: str,
    user_service: UserService = Depends(get_user_service),
    current_user: dict = Depends(require_user),
):
    try:
        user = user_service.get_user_by_id(user_id)
        return UserDTO(
            id=user.id,
            name=user.name,
            email=user.email,
            role=user.role,
            created_at=user.created_at,
            updated_at=user.updated_at,
        )
    except (InvalidInputError, NotFoundError) as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


@users_router.delete("/users/{id}", response_model=GenericResponse)
async def delete_user_by_id(
    id: str,
    user_service: UserService = Depends(get_user_service),
    current_user: dict = Depends(require_admin),
):
    try:
        user_service.delete_user_by_id(id)
        return GenericResponse(message="user deleted successfully")
    except (InvalidInputError, NotFoundError) as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")
