from contextlib import AbstractContextManager
from typing import Optional, List, Callable
from uuid import UUID

from sqlalchemy.orm import Session

from app.model.job_task import JobTask, TaskStatus
from app.repository.base_repository import BaseRepository
from app.schema.job_task_schema import JobTaskCreate, JobTaskUpdate


class JobTaskRepository(BaseRepository):
    def __init__(
        self, 
        session_factory: Callable[..., AbstractContextManager[Session]],
        replica_session_factory: Callable[..., AbstractContextManager[Session]] = None,
    ):
        super().__init__(session_factory, JobTask, replica_session_factory)

    def create_task(self, task: JobTaskCreate) -> JobTask:
        with self.session_factory() as session:
            db_task = JobTask(
                job_id=str(task.job_id),
                user_id=str(task.user_id),
                status=TaskStatus.PENDING.value
            )
            session.add(db_task)
            session.commit()
            session.refresh(db_task)

            return db_task

    def update_task_status(self, task_id: str, status: TaskStatus, result=None, error_message=None) -> Optional[JobTask]:
        with self.session_factory() as session:
            task = session.query(JobTask).filter(JobTask.id == task_id).first()
            if not task:
                return None

            task.status = status.value
            if result is not None:
                task.result = result
            if error_message is not None:
                task.error_message = error_message

            session.commit()
            session.refresh(task)

            return task

    def get_pending_tasks(self, limit: int = 10) -> List[JobTask]:
        with self.replica_session_factory() as session:

            return session.query(JobTask).filter(
                JobTask.status == TaskStatus.PENDING.value
            ).limit(limit).all()

    def get_user_tasks(self, user_id: UUID) -> List[JobTask]:
        with self.replica_session_factory() as session:

            return session.query(JobTask).filter(
                JobTask.user_id == str(user_id)
            ).all()
        
    def get_task_by_job(self, job_id: UUID, user_id: UUID) -> Optional[JobTask]:
        with self.replica_session_factory() as session:

            return session.query(JobTask).filter(
                JobTask.job_id == str(job_id),
                JobTask.user_id == str(user_id)
            ).order_by(JobTask.created_at.desc()).first()