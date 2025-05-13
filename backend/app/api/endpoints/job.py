from app.scripts.elasticsearch_sync import sync_jobs_to_elasticsearch as sync_func
from uuid import UUID

from dependency_injector.wiring import Provide
from fastapi import APIRouter, Depends, BackgroundTasks, Query

from app.core.containers.application_container import ApplicationContainer
from app.core.dependencies import get_current_user
from app.core.middleware import inject
from app.core.security import JWTBearer
from app.model.job_task import TaskType
from app.schema.base_schema import PageResponse
from app.schema.job_schema import JobSearchRequest, JobResponse, JobFavoriteResponse
from app.schema.job_task_schema import JobTaskResponse, JobTaskStartRequest
from app.schema.user_schema import UserBasicResponse, UserDetailResponse
from app.services.job_service import JobService
from app.services.kafka_service import KafkaService
from app.repository.elasticsearch_repository import ElasticsearchRepository

router = APIRouter(prefix="/jobs", tags=["Job"], dependencies=[Depends(JWTBearer())])


@router.post("/search", response_model=PageResponse[JobResponse])
@inject
def search_job(
    request: JobSearchRequest,
    job_service: JobService = Depends(Provide[ApplicationContainer.services.job_service]),
    current_user: UserBasicResponse = Depends(get_current_user),
):
    return job_service.full_text_search_job(request, current_user.id)


@router.get("/recommendations", response_model=PageResponse[JobResponse])
@inject
def get_recommendations(
        page: int = Query(1, ge=1),
        page_size: int = Query(20, ge=1, le=100),
        service: JobService = Depends(Provide[ApplicationContainer.services.job_service]),
        current_user: UserDetailResponse = Depends(get_current_user)
):
    return service.get_job_recommendation(current_user.id, page, page_size)


@router.get("/favorite", response_model=PageResponse[JobFavoriteResponse])
@inject
def get_favorite_jobs(
        page: int = Query(1, ge=1),
        page_size: int = Query(20, ge=1, le=100),
        service: JobService = Depends(Provide[ApplicationContainer.services.job_service]),
        current_user: UserDetailResponse = Depends(get_current_user)
):
    return service.get_user_favorite_jobs_with_analytics(
        current_user.id, page, page_size
    )


@router.post("/{job_id}/favorite")
@inject
def add_favorite_job(
        job_id: UUID,
        service: JobService = Depends(Provide[ApplicationContainer.services.job_service]),
        current_user: UserBasicResponse = Depends(get_current_user)
):
    return service.add_to_favorite(job_id, current_user.id)


@router.post("/{job_id}/delete-favorite")
@inject
def remove_favorite_job(
        job_id: UUID,
        service: JobService = Depends(Provide[ApplicationContainer.services.job_service]),
        current_user: UserBasicResponse = Depends(get_current_user)
):
    return service.remove_from_favorite(job_id, current_user.id)


@router.post("/{job_id}/scoring")
@inject
def score_job(
        job_id: UUID,
        kafka_service: KafkaService = Depends(Provide[ApplicationContainer.services.kafka_service]),
        current_user: UserBasicResponse = Depends(get_current_user)
):
    # Send task to Kafka for background processing
    kafka_service.create_job_task(
        job_id=job_id,
        user_id=current_user.id,
        task_type=TaskType.JOB_SCORE.value
    )
    
    return {"message": "Job scoring started in background", "job_id": str(job_id)}


@router.post("/{job_id}/analyze")
@inject
def analyze_job(
        job_id: UUID,
        kafka_service: KafkaService = Depends(Provide[ApplicationContainer.services.kafka_service]),
        current_user: UserBasicResponse = Depends(get_current_user)
):
    # Send task to Kafka for background processing
    kafka_service.create_job_task(
        job_id=job_id,
        user_id=current_user.id,
        task_type=TaskType.JOB_ANALYZE.value
    )
    
    return {"message": "Job analysis started in background", "job_id": str(job_id)}


@router.post("/{job_id}/resume", response_model=JobResponse)
@inject
def get_resume_job(
        job_id: UUID,
        service: JobService = Depends(Provide[ApplicationContainer.services.job_service]),
        current_user: UserBasicResponse = Depends(get_current_user)
):
    return service.generate_resume(job_id, current_user.id)


@router.post("/elasticsearch/sync")
@inject
def sync_jobs_to_elasticsearch(
    background_tasks: BackgroundTasks,
    batch_size: int = Query(500, ge=100, le=5000, description="Number of jobs to process in each batch"),
    verify: bool = Query(True, description="Verify synchronization after completion"),
    include_deleted: bool = Query(False, description="Include soft-deleted jobs"),
    job_service: JobService = Depends(Provide[ApplicationContainer.services.job_service]),
    es_repository: ElasticsearchRepository = Depends(Provide[ApplicationContainer.repositories.elasticsearch_repository]),
    current_user: UserBasicResponse = Depends(get_current_user)
):
    background_tasks.add_task(sync_func, job_service=job_service, es_repository=es_repository, 
                             batch_size=batch_size, verify=verify, include_deleted=include_deleted)

    return {
        "message": "Job synchronization started in background",
        "details": {
            "batch_size": batch_size,
            "verification": "enabled" if verify else "disabled",
            "include_deleted": "yes" if include_deleted else "no"
        }
    }
