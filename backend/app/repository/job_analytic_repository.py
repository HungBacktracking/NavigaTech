from uuid import UUID
from typing import Optional, Tuple, List
from sqlalchemy import func, select

from app.model.job import Job
from app.model.job_analytic import JobAnalytic
from app.model.favorite_job import FavoriteJob
from app.repository.base_repository import BaseRepository
from app.schema.job_analytic_schema import JobAnalyticRequest


class JobAnalyticRepository(BaseRepository):
    def __init__(self, session_factory, replica_session_factory):
        super().__init__(session_factory, JobAnalytic, replica_session_factory)

    def find_by_job_and_user(
        self, job_id: UUID, user_id: UUID
    ) -> Optional[JobAnalytic]:
        """
        Find job analytic by job_id and user_id
        """
        with self.replica_session_factory() as session:
            return (
                session.query(JobAnalytic)
                .filter(
                    JobAnalytic.job_id == job_id,
                    JobAnalytic.user_id == user_id,
                    JobAnalytic.deleted_at == None,
                )
                .first()
            )

    def find_by_user_with_pagination(
        self, user_id: UUID, page: int, page_size: int
    ) -> Tuple[List[Tuple[Job, FavoriteJob, JobAnalytic]], int]:
        """
        Find all job analytics for a user with pagination
        Returns a tuple of (results, total_count)
        """
        with self.replica_session_factory() as session:
            query = (
                select(Job, FavoriteJob, JobAnalytic)
                .join(JobAnalytic, Job.id == JobAnalytic.job_id)
                .join(FavoriteJob, Job.id == FavoriteJob.job_id)
                .where(JobAnalytic.user_id == user_id)
                .where(FavoriteJob.user_id == user_id)
                .where(FavoriteJob.is_analyze == True)
                .where(Job.deleted_at == None)
                .order_by(JobAnalytic.updated_at.desc())
            )

            # Count total results
            count_query = select(func.count()).select_from(query.subquery())
            total_count = session.execute(count_query).scalar_one()

            # Apply pagination
            offset = (page - 1) * page_size
            query = query.offset(offset).limit(page_size)
            results = session.execute(query).all()

            return results, total_count

    def create_or_update(self, job_id: UUID, user_id: UUID, data: dict) -> JobAnalytic:
        with self.session_factory() as session:
            # Try to find existing record
            analytic = (
                session.query(JobAnalytic)
                .filter(
                    JobAnalytic.job_id == job_id,
                    JobAnalytic.user_id == user_id,
                    JobAnalytic.deleted_at == None,
                )
                .first()
            )

            # If exists, update it
            if analytic:
                for key, value in data.items():
                    if hasattr(analytic, key):
                        setattr(analytic, key, value)
                session.commit()
                session.refresh(analytic)
                return analytic

            # Otherwise create new
            new_analytic = JobAnalytic(job_id=job_id, user_id=user_id, **data)
            session.add(new_analytic)
            session.commit()
            session.refresh(new_analytic)

            return new_analytic
