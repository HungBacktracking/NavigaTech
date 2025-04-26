from dependency_injector.wiring import Provide
from fastapi import APIRouter, Depends

from app.core.container import Container
from app.core.dependencies import get_current_user
from app.core.middleware import inject
from app.core.security import JWTBearer
from app.model.user import User
from app.schema.user_schema import UserResponse, UserUpdate
from app.services.user_service import UserService

router = APIRouter(prefix="/user", tags=["user"], dependencies=[Depends(JWTBearer())])



@router.get("/{user_id}", response_model=UserResponse)
@inject
def get_user(
    user_id: int,
    service: UserService = Depends(Provide[Container.user_service]),
    current_user: User = Depends(get_current_user)
):
    return service.get_by_id(user_id)



@router.put("/{user_id}", response_model=UserResponse)
@inject
def update_user(
    user_id: int,
    update_request: UserUpdate,
    service: UserService = Depends(Provide[Container.user_service]),
    current_user: User = Depends(get_current_user)
):
    return service.update(user_id, update_request)

