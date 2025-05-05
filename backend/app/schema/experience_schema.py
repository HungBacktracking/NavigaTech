from datetime import date
from typing import Optional
from pydantic import BaseModel
from app.schema.base_schema import ModelBaseInfo



class BaseExperience(BaseModel):
    company_name: str
    title: str
    employment_type: Optional[str] = None
    description: Optional[str] = None
    achievement: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    is_current: bool = False

    class Config:
        from_attributes = True

class ExperienceResponse(ModelBaseInfo, BaseExperience): ...

class ExperienceRequest(ModelBaseInfo, BaseExperience): ...