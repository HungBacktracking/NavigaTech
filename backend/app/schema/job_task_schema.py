from datetime import datetime
from typing import Optional, Dict, Any, List
from uuid import UUID

from pydantic import BaseModel, ConfigDict, field_serializer

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
    
    id: UUID
    status: str
    result: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    # Serialize UUIDs to strings when outputting to JSON
    @field_serializer('id', 'job_id', 'user_id')
    def serialize_uuid(self, uuid_value: UUID) -> str:
        return str(uuid_value)


class JobTaskStartRequest(BaseModel):
    job_id: UUID
    task_type: str 