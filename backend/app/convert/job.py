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
        job_url=job.job_url or "",
        logo_url=job.logo_url or "",
        job_name=job.job_name or "",
        from_site=job.from_site or "",
        company_name=job.company_name or "",
        company_type=job.company_type,
        company_address=job.company_address,
        company_description=job.company_description,
        job_type=job.job_type,
        skills=job.skills or "",
        location=job.location,
        date_posted=job.date_posted,
        salary=job.salary,
        job_description=job.job_description or "",
        is_analyze=fav.is_analyze if fav else False,
        is_favorite=fav.is_favorite if fav else False,
        job_analytics=analytic_resp,
    )
