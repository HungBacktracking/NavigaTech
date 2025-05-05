from datetime import date
from typing import Optional
from uuid import UUID

from pydantic import BaseModel
from app.schema.base_schema import ModelBaseInfo


class BaseProject(BaseModel):
    project_name: str
    role: Optional[str] = None
    description: Optional[str] = None
    achievement: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None

    class Config:
        from_attributes = True

class ProjectResponse(ModelBaseInfo, BaseProject): ...

class ProjectRequest(ModelBaseInfo, BaseProject):
    user_id: UUID