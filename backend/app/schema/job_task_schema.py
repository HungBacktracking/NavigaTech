from datetime import datetime
from typing import Optional, Dict, Any, List
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.model.job_task import TaskStatus, TaskType


class JobTaskBase(BaseModel):
    job_id: UUID
    user_id: UUID
    task_type: str


class JobTaskCreate(JobTaskBase):
    pass


class JobTaskUpdate(BaseModel):
    status: Optional[TaskStatus] = None
    result: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None


class JobTaskResponse(JobTaskBase):
    model_config = ConfigDict(arbitrary_types_allowed=True, from_attributes=True)
    
    id: str
    status: str
    result: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class JobTaskStartRequest(BaseModel):
    job_id: UUID
    task_type: str 