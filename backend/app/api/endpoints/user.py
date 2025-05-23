from dependency_injector.wiring import Provide
from fastapi import Depends

from app.core.containers.application_container import ApplicationContainer
from app.core.dependencies import get_current_user
from app.core.middleware import inject
from app.core.security import JWTBearer
from app.schema.s3_schema import UploadResponse, DownloadResponse
from app.schema.user_schema import UserBasicResponse, UserUpdate, UserDetailResponse
from app.services.resume_service import ResumeService
from app.services.s3_service import S3Service
from app.services.user_service import UserService
from fastapi import APIRouter

router = APIRouter(prefix="/users", tags=["User"], dependencies=[Depends(JWTBearer())])


@router.get("/me", response_model=UserBasicResponse)
@inject
def get_me(current_user: UserBasicResponse = Depends(get_current_user)):
    return current_user

@router.get("/detail-me", response_model=UserDetailResponse)
@inject
def get_detail_me(
        service: UserService = Depends(Provide[ApplicationContainer.services.user_service]),
        current_user: UserDetailResponse = Depends(get_current_user)
):
    return service.get_detail_by_id(current_user.id)

@router.put("/me", response_model=UserDetailResponse)
@inject
def update_me(
    update_request: UserUpdate,
    service: UserService = Depends(Provide[ApplicationContainer.services.user_service]),
    current_user: UserBasicResponse = Depends(get_current_user)
):
    return service.update(current_user.id, update_request)


