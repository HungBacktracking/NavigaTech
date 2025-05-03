from dependency_injector.wiring import Provide
from fastapi import APIRouter, Depends

from app.core.container import Container
from app.core.dependencies import get_current_user
from app.core.middleware import inject
from app.core.security import JWTBearer
from app.schema.job_schema import JobSearchRequest
from app.schema.user_schema import UserBasicResponse, UserUpdate, UserDetailResponse
from app.services.user_service import UserService

router = APIRouter(prefix="/jobs", tags=["Job"], dependencies=[Depends(JWTBearer())])


@router.get("/search")
@inject
def search(
        request: JobSearchRequest,
        service: JobService = Depends(Provide[Container.job_service]),
        current_user: UserBasicResponse = Depends(get_current_user)
):
    return service.search(request)

@router.get("/favorite")

@router.get("/me", response_model=UserBasicResponse)
@inject
def get_me(current_user: UserBasicResponse = Depends(get_current_user)):
    return current_user

@router.get("/detail-me", response_model=UserDetailResponse)
@inject
def get_detail_me(
        service: UserService = Depends(Provide[Container.user_service]),
        current_user: UserDetailResponse = Depends(get_current_user)
):
    return service.get_detail_by_id(current_user.id)

@router.put("/me", response_model=UserDetailResponse)
@inject
def update_me(
    update_request: UserUpdate,
    service: UserService = Depends(Provide[Container.user_service]),
    current_user: UserBasicResponse = Depends(get_current_user)
):
    return service.update(current_user.id, update_request)

