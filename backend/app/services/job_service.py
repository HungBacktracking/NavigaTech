from typing import Optional, List
from uuid import UUID

from app.convert.job import to_favorite_job_response
from app.model.favorite_job import FavoriteJob
from app.model.job import Job
from app.repository.job_repository import JobRepository
from app.schema.job_schema import JobSearchRequest, JobFavoriteResponse, JobResponse
from app.services.base_service import BaseService


class JobService(BaseService):
    def __init__(self, job_repository: JobRepository):
        self.job_repository = job_repository
        super().__init__(job_repository)

    def search_job(self, request: JobSearchRequest, user_id: UUID) -> list[JobResponse]:
        rows: List[tuple[Job, Optional[FavoriteJob]]] = (
            self.job_repository.search_job(request, user_id)
        )

        results: List[JobResponse] = []
        for job, fav in rows:
            results.append(
                JobResponse(
                    id=job.id,
                    job_url=job.job_url,
                    logo_url=job.logo_url,
                    job_name=job.job_name,
                    company_name=job.company_name,
                    company_type=job.company_type,
                    company_address=job.company_address,
                    company_description=job.company_description,
                    job_type=job.job_type,
                    skills=job.skills,
                    location=job.location,
                    date_posted=job.date_posted,
                    job_description=job.job_description,
                    job_requirement=job.job_requirement,
                    benefit=job.benefit,
                    is_expired=job.is_expired,

                    is_analyze=fav.is_analyze if fav else False,
                    resume_url=fav.resume_url if fav else None,
                    is_favorite=fav.is_favorite if fav else False,
                )
            )

        return results

    def get_user_favorite_jobs_with_analytics(self, user_id: UUID) -> List[JobFavoriteResponse]:
        rows = self.job_repository.find_favorite_job_with_analytics(user_id)

        return [
            to_favorite_job_response(job, fav, analytic)
            for job, fav, analytic in rows
        ]




    def get_job_recommendation(self, user_id: UUID) -> List[JobResponse]:
        pass

    def analyze_job(self, job_id: UUID, user_id: UUID):
        pass

    def generate_resume(self, job_id: UUID, user_id: UUID):
        pass




