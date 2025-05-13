import logging
from typing import Dict, Any, Optional, List
from uuid import UUID

from app.exceptions.custom_error import CustomError
from app.model.job_task import JobTask, TaskStatus
from app.repository.job_task_repository import JobTaskRepository
from app.schema.job_task_schema import JobTaskCreate, JobTaskResponse


class JobTaskService:
    def __init__(self, job_task_repository: JobTaskRepository):
        self.job_task_repository = job_task_repository
        self._logger = logging.getLogger(__name__)

    def create_task(self, job_id: UUID, user_id: UUID) -> JobTask:
        """Create a new job task"""
        task = JobTaskCreate(
            job_id=job_id,
            user_id=user_id
        )
        return self.job_task_repository.create_task(task)

    def update_task_status(self, task_id: str, status: TaskStatus, result=None, error_message=None) -> Optional[JobTask]:
        return self.job_task_repository.update_task_status(task_id, status, result, error_message)

    def get_user_tasks(self, user_id: UUID) -> List[JobTaskResponse]:
        tasks = self.job_task_repository.get_user_tasks(user_id)

        return [JobTaskResponse.model_validate(task) for task in tasks]

    def get_task_by_job(self, job_id: UUID, user_id: UUID) -> Optional[JobTaskResponse]:
        task = self.job_task_repository.get_task_by_job(job_id, user_id)
        if task:
            return JobTaskResponse.model_validate(task)

        raise CustomError.NOT_FOUND.as_exception()