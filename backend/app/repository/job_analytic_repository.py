from uuid import UUID
from typing import Optional

from app.model.job_analytic import JobAnalytic
from app.repository.base_repository import BaseRepository
from app.schema.job_analytic_schema import JobAnalyticRequest


class JobAnalyticRepository(BaseRepository):
    def __init__(self, session_factory, replica_session_factory):
        super().__init__(session_factory, JobAnalytic, replica_session_factory)
        
    def find_by_job_and_user(self, job_id: UUID, user_id: UUID) -> Optional[JobAnalytic]:
        """
        Find job analytic by job_id and user_id
        """
        with self.replica_session_factory() as session:
            return session.query(JobAnalytic).filter(
                JobAnalytic.job_id == job_id,
                JobAnalytic.user_id == user_id,
                JobAnalytic.deleted_at == None
            ).first()
            
    def create_or_update(self, job_id: UUID, user_id: UUID, data: dict) -> JobAnalytic:
        """
        Create or update job analytic for a job and user
        """
        with self.session_factory() as session:
            # Try to find existing record
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