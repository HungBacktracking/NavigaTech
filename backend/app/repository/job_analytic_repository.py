from uuid import UUID
from typing import Optional, List, Tuple

from sqlalchemy.sql import func
from sqlmodel import select
from app.model.job import Job
from app.model.favorite_job import FavoriteJob
from app.model.job_analytic import JobAnalytic
from app.repository.base_repository import BaseRepository
from app.schema.job_analytic_schema import JobAnalyticRequest


class JobAnalyticRepository(BaseRepository):
    def __init__(self, session_factory, replica_session_factory):
        super().__init__(session_factory, JobAnalytic, replica_session_factory)
        
    def find_by_job_and_user(self, job_id: UUID, user_id: UUID) -> Optional[JobAnalytic]:
        with self.replica_session_factory() as session:
            return session.query(JobAnalytic).filter(
                JobAnalytic.job_id == job_id,
                JobAnalytic.user_id == user_id,
                JobAnalytic.deleted_at == None
            ).first()
            
    def find_by_user_with_pagination(
        self, user_id: UUID, page: int, page_size: int, search: Optional[str] = None
    ) -> Tuple[List[Tuple[Job, FavoriteJob, JobAnalytic]], int]:
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

            if search and search.strip():
                search_term = f"%{search.strip()}%"
                query = query.where(
                    (Job.job_name.ilike(search_term)) | 
                    (Job.company_name.ilike(search_term))
                )

            count_query = select(func.count()).select_from(query.subquery())
            total_count = session.execute(count_query).scalar_one()

            offset = (page - 1) * page_size
            query = query.offset(offset).limit(page_size)
            results = session.execute(query).all()

            return results, total_count
            
    def create_or_update(self, job_id: UUID, user_id: UUID, data: dict) -> JobAnalytic:
        with self.session_factory() as session:
            analytic = session.query(JobAnalytic).filter(
                JobAnalytic.job_id == job_id,
                JobAnalytic.user_id == user_id,
                JobAnalytic.deleted_at == None
            ).first()
            
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