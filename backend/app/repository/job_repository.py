from contextlib import AbstractContextManager
from typing import Callable, Optional, List, Tuple
from uuid import UUID

from sqlmodel import Session, select
from sqlalchemy.sql import func

from app.model.favorite_job import FavoriteJob
from app.model.job import Job
from app.model.job_analytic import JobAnalytic
from app.repository.base_repository import BaseRepository
from app.schema.job_schema import JobSearchRequest


class JobRepository(BaseRepository):
    def __init__(
        self, 
        session_factory: Callable[..., AbstractContextManager[Session]],
        replica_session_factory: Callable[..., AbstractContextManager[Session]] = None,
    ):
        super().__init__(session_factory, Job, replica_session_factory)

    def find_by_url(self, job_url: str) -> Optional[Job]:
        """Find a job by its URL"""
        if not job_url:
            return None

        with self.replica_session_factory() as session:
            statement = select(Job).where(Job.job_url == job_url)
            return session.exec(statement).first()

    def search_job(
        self, request: JobSearchRequest, user_id: UUID
    ) -> List[Tuple[Job, Optional[FavoriteJob]]]:
        with self.replica_session_factory() as session:
            select_statement = (
                select(Job)
                .outerjoin(
                    FavoriteJob,
                    (Job.id == FavoriteJob.job_id) & (FavoriteJob.user_id == user_id),
                )
                .where(Job.name.ilike(f"%{request.name}%"))
                .where(Job.company.ilike(f"%{request.company}%"))
                .order_by(Job.end_date.desc())
            )

            return list(session.exec(select_statement).all())

    def find_favorite_job_with_analytics(
        self, user_id: UUID, page: int = None, page_size: int = None
    ) -> Tuple[List[Tuple[Job, FavoriteJob, Optional[JobAnalytic]]], int]:
        with self.replica_session_factory() as session:
            statement = (
                select(Job, FavoriteJob, JobAnalytic)
                .join(FavoriteJob, Job.id == FavoriteJob.job_id)
                .outerjoin(JobAnalytic, Job.id == JobAnalytic.job_id)
                .where(FavoriteJob.user_id == user_id)
                .where(JobAnalytic.user_id == user_id)
                .order_by(FavoriteJob.created_at.desc())
            )

            count_statement = select(func.count()).select_from(statement.subquery())
            total_count = session.exec(count_statement).one()

            if page is not None and page_size is not None:
                offset = (page - 1) * page_size
                statement = statement.offset(offset).limit(page_size)

            results = list(session.exec(statement).all())
            return results, total_count

    def get_all(self) -> List[Job]:
        with self.replica_session_factory() as session:
            statement = select(Job)
            jobs = session.execute(statement).scalars().all()

            return jobs
