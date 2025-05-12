from typing import List
from uuid import UUID

from dependency_injector.wiring import Provide
from fastapi import APIRouter, Depends, BackgroundTasks

from app.core.containers.application_container import ApplicationContainer
from app.core.dependencies import get_current_user
from app.core.middleware import inject
from app.core.security import JWTBearer
from app.schema.job_schema import JobSearchRequest, JobResponse, JobFavoriteResponse
from app.schema.user_schema import UserBasicResponse, UserDetailResponse
from app.services.job_service import JobService

router = APIRouter(prefix="/jobs", tags=["Job"], dependencies=[Depends(JWTBearer())])


@router.post("/search", response_model=List[JobResponse])
@inject
def search_job(
    request: JobSearchRequest,
    job_service: JobService = Depends(Provide[ApplicationContainer.services.job_service]),
    current_user: UserBasicResponse = Depends(get_current_user),
):
    return job_service.full_text_search_job(request, current_user.id)


@router.get("/recommendations")
@inject
async def get_recommendations(
        service: JobService = Depends(Provide[ApplicationContainer.services.job_service]),
        current_user: UserDetailResponse = Depends(get_current_user)
):
    return service.get_job_recommendation(current_user.id)

@router.get("/favorite", response_model=List[JobFavoriteResponse])
@inject
async def get_favorite_jobs(
        service: JobService = Depends(Provide[ApplicationContainer.services.job_service]),
        current_user: UserDetailResponse = Depends(get_current_user)
):
    return service.get_user_favorite_jobs_with_analytics(current_user.id)

@router.post("/{job_id}/favorite")
@inject
async def add_favorite_job(
        job_id: UUID,
        service: JobService = Depends(Provide[ApplicationContainer.services.job_service]),
        current_user: UserBasicResponse = Depends(get_current_user)
):
    return service.add_to_favorite(job_id, current_user.id)

@router.post("/{job_id}/delete-favorite")
@inject
async def remove_favorite_job(
        job_id: UUID,
        service: JobService = Depends(Provide[ApplicationContainer.services.job_service]),
        current_user: UserBasicResponse = Depends(get_current_user)
):
    return service.remove_from_favorite(job_id, current_user.id)

@router.post("/{job_id}/scroring")
@inject
async def score_job(
        job_id: UUID,
        service: JobService = Depends(Provide[ApplicationContainer.services.job_service]),
        current_user: UserBasicResponse = Depends(get_current_user)
):
    return service.score_job(job_id, current_user.id)

@router.post("/{job_id}/analyze")
@inject
async def analyze_job(
        job_id: UUID,
        service: JobService = Depends(Provide[ApplicationContainer.services.job_service]),
        current_user: UserBasicResponse = Depends(get_current_user)
):
    return service.analyze_job(job_id, current_user.id)

@router.post("/{job_id}/resume", response_model=JobResponse)
@inject
async def get_resume_job(
        job_id: UUID,
        service: JobService = Depends(Provide[ApplicationContainer.services.job_service]),
        current_user: UserBasicResponse = Depends(get_current_user)
):
    return service.generate_resume(job_id, current_user.id)



@router.post("/elasticsearch/sync")
@inject
def sync_jobs_to_elasticsearch(
    background_tasks: BackgroundTasks,
    job_service: JobService = Depends(Provide[ApplicationContainer.services.job_service]),
    current_user: UserBasicResponse = Depends(get_current_user)
):
    background_tasks.add_task(job_service.index_all_jobs)

    return {"message": "Job synchronization started in background"}

