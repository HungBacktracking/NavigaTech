from typing import Optional

from app.model.favorite_job import FavoriteJob
from app.model.job import Job
from app.model.job_analytic import JobAnalytic
from app.schema.job_analytic_schema import JobAnalyticResponse
from app.schema.job_schema import JobFavoriteResponse

def to_favorite_job_response(
    job: Job,
    fav: FavoriteJob,
    analytic: Optional[JobAnalytic]
) -> JobFavoriteResponse:
    analytic_resp = (
        JobAnalyticResponse.model_validate(analytic)
        if analytic
        else None
    )

    return JobFavoriteResponse(
        id=job.id,
        job_url=job.job_url,
        logo_url=job.logo_url,
        job_name=job.job_name,
        from_site=job.from_site,
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
        is_analyze=fav.is_analyze,
        is_favorite=fav.is_favorite,

        job_analytics=analytic_resp,
    )
