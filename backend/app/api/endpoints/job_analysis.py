from uuid import UUID

from dependency_injector.wiring import Provide
from fastapi import APIRouter, Depends, Query

from app.core.containers.application_container import ApplicationContainer
from app.core.dependencies import get_current_user
from app.core.middleware import inject
from app.core.security import JWTBearer
from app.schema.base_schema import PageResponse
from app.schema.job_schema import JobFavoriteResponse
from app.schema.user_schema import UserBasicResponse
from app.services.job_analytic_service import JobAnalyticService
from app.services.job_task_service import JobTaskService
from app.services.kafka_service import KafkaService


router = APIRouter(
    prefix="/job-analysis", tags=["Job Analysis"], dependencies=[Depends(JWTBearer())]
)

@router.get("", response_model=PageResponse[JobFavoriteResponse])
@inject
def get_job_analysis_list(
        page: int = Query(1, ge=1, description="Page number"),
        page_size: int = Query(20, ge=1, le=100, description="Items per page"),
        search: str = Query(None, description="Search term to filter by job name or company"),
        job_analytic_service: JobAnalyticService = Depends(Provide[ApplicationContainer.services.job_analytic_service]),
        current_user: UserBasicResponse = Depends(get_current_user)
):
    return job_analytic_service.get_user_job_analytics(
        user_id=current_user.id,
        page=page,
        page_size=page_size,
        search=search
    )


@router.post("/{job_id}")
@inject
def process_job_analysis(
    job_id: UUID,
    kafka_service: KafkaService = Depends(
        Provide[ApplicationContainer.services.kafka_service]
    ),
    job_analytic_service: JobAnalyticService = Depends(
        Provide[ApplicationContainer.services.job_analytic_service]
    ),
    job_task_service: JobTaskService = Depends(
        Provide[ApplicationContainer.services.job_task_service]
    ),
    current_user: UserBasicResponse = Depends(get_current_user),
):

    job_task_service.handle_active_task(job_id, current_user.id)
    job_analytic_service.handle_exist_analysis(job_id, current_user.id)

    kafka_service.create_job_task(job_id=job_id, user_id=current_user.id)

    return {
        "message": "Complete job analysis started in background",
        "job_id": str(job_id),
    }


@router.get("/full", response_model=list[JobFavoriteResponse])
@inject
def get_full_job_analysis(
    job_analytic_service: JobAnalyticService = Depends(
        Provide[ApplicationContainer.services.job_analytic_service]
    ),
    current_user: UserBasicResponse = Depends(get_current_user),
):
    return job_analytic_service.get_full_job_analysis(current_user.id)


@router.get("/{job_id}", response_model=JobFavoriteResponse)
@inject
def get_job_analysis(
    job_id: UUID,
    job_analytic_service: JobAnalyticService = Depends(
        Provide[ApplicationContainer.services.job_analytic_service]
    ),
    current_user: UserBasicResponse = Depends(get_current_user),
):
    return job_analytic_service.get_by_job_and_user(job_id, current_user.id)
