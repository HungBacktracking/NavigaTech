from datetime import date
from typing import Optional, List
from pydantic import BaseModel
from app.schema.base_schema import ModelBaseInfo
from app.schema.job_analytic_schema import JobAnalyticResponse


class BaseJob(BaseModel):
    from_site: str
    job_url: str
    logo_url: str
    job_name: str
    company_name: str
    company_type: Optional[str] = None
    company_address: Optional[str] = None
    company_description: Optional[str] = None
    job_type: Optional[str] = None
    skills: Optional[List[str]] = None
    location: Optional[str] = None
    date_posted: Optional[date] = None
    job_description: str
    job_requirement: str
    benefit: Optional[str] = None
    is_expired: Optional[bool] = None
    is_analyze: bool
    resume_url: Optional[str] = None
    is_favorite: bool

    class Config:
        from_attributes = True

class JobResponse(ModelBaseInfo, BaseJob): ...

class JobFavoriteResponse(ModelBaseInfo, BaseJob):
    job_analytics: Optional[JobAnalyticResponse] = None



class JobSearchRequest(BaseModel):
    query: str
    roles: Optional[List[str]] = None
    levels: Optional[List[str]] = None











