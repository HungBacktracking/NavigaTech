from uuid import UUID

from dependency_injector.wiring import Provide
from fastapi import APIRouter, Depends, HTTPException, status

from app.core.containers.application_container import ApplicationContainer
from app.core.dependencies import get_current_user
from app.core.middleware import inject
from app.core.security import JWTBearer
from app.schema.job_analytic_schema import JobAnalyticResponse
from app.schema.user_schema import UserBasicResponse
from app.services.job_analytic_service import JobAnalyticService
from app.services.job_task_service import JobTaskService
from app.services.kafka_service import KafkaService


router = APIRouter(prefix="/job-analysis", tags=["Job Analysis"], dependencies=[Depends(JWTBearer())])



@router.post("/{job_id}")
@inject
def process_job_analysis(
        job_id: UUID,
        kafka_service: KafkaService = Depends(Provide[ApplicationContainer.services.kafka_service]),
        job_analytic_service: JobAnalyticService = Depends(Provide[ApplicationContainer.services.job_analytic_service]),
        job_task_service: JobTaskService = Depends(Provide[ApplicationContainer.services.job_task_service]),
        current_user: UserBasicResponse = Depends(get_current_user)
):

    job_task_service.handle_active_task(job_id, current_user.id)
    job_analytic_service.handle_exist_analysis(job_id, current_user.id)

    kafka_service.create_job_task(
        job_id=job_id,
        user_id=current_user.id
    )

    return {"message": "Complete job analysis started in background", "job_id": str(job_id)}


@router.get("/{job_id}", response_model=JobAnalyticResponse)
@inject
def get_job_analysis(
        job_id: UUID,
        job_analytic_service: JobAnalyticService = Depends(Provide[ApplicationContainer.services.job_analytic_service]),
        current_user: UserBasicResponse = Depends(get_current_user)
):
    return job_analytic_service.get_by_job_and_user(job_id, current_user.id)

