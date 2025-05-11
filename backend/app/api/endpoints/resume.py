from dependency_injector.wiring import Provide
from fastapi import Depends

from app.core.containers.application_container import ApplicationContainer
from app.core.dependencies import get_current_user
from app.core.middleware import inject
from app.core.security import JWTBearer
from app.schema.s3_schema import UploadResponse, DownloadResponse
from app.schema.user_schema import UserBasicResponse, UserDetailResponse
from app.services.resume_service import ResumeService
from app.services.s3_service import S3Service
from fastapi import APIRouter

router = APIRouter(prefix="/resumes", tags=["Resume"], dependencies=[Depends(JWTBearer())])



@router.post("/upload", response_model=UploadResponse)
@inject
def upload_file(
    file_type: str,
    service: S3Service = Depends(Provide[ApplicationContainer.services.s3_service]),
    current_user: UserBasicResponse = Depends(get_current_user)
):
    return service.get_upload_url(current_user.id, file_type)

@router.get("/download", response_model=DownloadResponse)
@inject
def download_file(
    file_type: str,
    service: S3Service = Depends(Provide[ApplicationContainer.services.s3_service]),
    current_user: UserBasicResponse = Depends(get_current_user)
):
    return service.get_download_url(current_user.id, file_type)

@router.post("/process", response_model=UserDetailResponse)
@inject
def process_resume(
    service: ResumeService = Depends(Provide[ApplicationContainer.services.resume_service]),
    current_user: UserBasicResponse = Depends(get_current_user)
):
    return service.process_resume(current_user.id)


