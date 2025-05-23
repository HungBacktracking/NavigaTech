from typing import List
from uuid import UUID

from dependency_injector.wiring import Provide
from fastapi import APIRouter, Depends

from app.core.containers.application_container import ApplicationContainer
from app.core.dependencies import get_current_user
from app.core.middleware import inject
from app.core.security import JWTBearer
from app.schema.job_task_schema import JobTaskResponse
from app.schema.user_schema import UserBasicResponse
from app.services.job_task_service import JobTaskService

router = APIRouter(prefix="/job-tasks", tags=["Job Tasks"], dependencies=[Depends(JWTBearer())])


@router.get("", response_model=List[JobTaskResponse])
@inject
def get_user_tasks(
    job_task_service: JobTaskService = Depends(Provide[ApplicationContainer.services.job_task_service]),
    current_user: UserBasicResponse = Depends(get_current_user),
):
    return job_task_service.get_user_tasks(current_user.id)


@router.get("/{job_id}", response_model=JobTaskResponse)
@inject
def get_task_status(
    job_id: UUID,
    job_task_service: JobTaskService = Depends(Provide[ApplicationContainer.services.job_task_service]),
    current_user: UserBasicResponse = Depends(get_current_user),
):
    return job_task_service.get_task_by_job(job_id, current_user.id)