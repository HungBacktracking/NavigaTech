from typing import List
from uuid import UUID

from dependency_injector.wiring import Provide
from fastapi import APIRouter, Depends

from app.core.containers.container import Container
from app.core.dependencies import get_current_user
from app.core.middleware import inject
from app.core.security import JWTBearer
from app.schema.job_schema import JobSearchRequest, JobResponse, JobFavoriteResponse
from app.schema.user_schema import UserBasicResponse, UserDetailResponse
from app.services.job_service import JobService

router = APIRouter(prefix="/jobs", tags=["Job"], dependencies=[Depends(JWTBearer())])


@router.get("/search", response_model=List[JobResponse])
@inject
def search(
        request: JobSearchRequest,
        service: JobService = Depends(Provide[Container.job_service]),
        current_user: UserBasicResponse = Depends(get_current_user)
):
    return service.search_job(request, current_user.id)

@router.get("/recommendations", response_model=List[JobResponse])
@inject
def get_recommendations(
        service: JobService = Depends(Provide[Container.job_service]),
        current_user: UserDetailResponse = Depends(get_current_user)
):
    return service.get_job_recommendation(current_user.id)

@router.get("/favorite", response_model=List[JobFavoriteResponse])
@inject
def get_favorite_jobs(
        service: JobService = Depends(Provide[Container.job_service]),
        current_user: UserDetailResponse = Depends(get_current_user)
):
    return service.get_user_favorite_jobs_with_analytics(current_user.id)

@router.post("/{job_id}/analyze", response_model=List[JobFavoriteResponse])
@inject
def analyze_job(
        job_id: UUID,
        service: JobService = Depends(Provide[Container.job_service]),
        current_user: UserDetailResponse = Depends(get_current_user)
):
    return service.analyze_job(job_id, current_user.id)

@router.post("/{job_id}/resume", response_model=JobResponse)
@inject
def get_resume_job(
        job_id: UUID,
        service: JobService = Depends(Provide[Container.job_service]),
        current_user: UserDetailResponse = Depends(get_current_user)
):
    return service.generate_resume(job_id, current_user.id)