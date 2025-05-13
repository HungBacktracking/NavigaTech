from datetime import datetime
from typing import Optional, Dict, Any
from uuid import UUID

from pydantic import BaseModel

from app.model.job_task import TaskStatus
from app.schema.job_analytic_schema import JobAnalyticResponse


class JobTaskBase(BaseModel):
    job_id: UUID
    user_id: UUID

    class Config:
        from_attributes = True


class JobTaskCreate(JobTaskBase):
    pass


class JobTaskUpdate(BaseModel):
    status: Optional[TaskStatus] = None
    result: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None


class JobTaskResponse(JobTaskBase):
    id: UUID
    status: str
    result: Optional[JobAnalyticResponse] = None
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime



class JobTaskStartRequest(BaseModel):
    job_id: UUID