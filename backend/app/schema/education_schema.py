from datetime import date
from typing import Optional
from uuid import UUID

from pydantic import BaseModel
from app.schema.base_schema import ModelBaseInfo



class BaseEducation(BaseModel):
    major: str
    school_name: str
    degree_type: str
    gpa: Optional[str]
    is_current: bool = False
    description: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None

    class Config:
        from_attributes = True

class EducationResponse(ModelBaseInfo, BaseEducation): ...

class EducationRequest(BaseEducation):
    user_id: UUID
