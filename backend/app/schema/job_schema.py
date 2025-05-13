from datetime import date
from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel
from app.schema.base_schema import ModelBaseInfo, PageRequest
from app.schema.job_analytic_schema import JobAnalyticResponse


class BaseJob(BaseModel):
    from_site: str
    job_url: str
    logo_url: str
    job_name: str
    job_level: Optional[str] = None
    company_name: str
    company_type: Optional[str] = None
    company_address: Optional[str] = None
    company_description: Optional[str] = None
    job_type: Optional[str] = None
    skills: Optional[str] = None
    location: Optional[str] = None
    date_posted: Optional[date] = None
    job_description: Optional[str] = None
    job_requirement: str
    benefit: Optional[str] = None
    is_analyze: bool
    resume_url: Optional[str] = None
    is_favorite: bool

    class Config:
        from_attributes = True


class JobResponse(ModelBaseInfo, BaseJob): ...


class FavoriteJobRequest(BaseModel):
    job_id: UUID
    user_id: UUID
    is_analyze: Optional[bool] = None
    is_generated_resume: Optional[bool] = None
    is_favorite: bool


class JobFavoriteResponse(ModelBaseInfo, BaseJob):
    job_analytics: Optional[JobAnalyticResponse] = None


class JobSearchRequest(PageRequest):
    query: str
    roles: Optional[List[str]] = None
    levels: Optional[List[str]] = None
