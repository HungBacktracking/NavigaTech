from datetime import datetime, timezone
from enum import Enum
from typing import Optional, TYPE_CHECKING
from uuid import UUID

from pydantic import ConfigDict
from sqlmodel import Column, Field, func, Text, DateTime, Date, JSON, Relationship

from app.model.base_model import BaseModel


if TYPE_CHECKING:
    from app.model.job import Job
    from app.model.user import User

class TaskStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class TaskType(str, Enum):
    JOB_SCORE = "job_score"
    JOB_ANALYZE = "job_analyze"
    RESUME_GENERATE = "resume_generate"


class JobTask(BaseModel, table=True):
    __tablename__ = "job_tasks"
    model_config = ConfigDict(arbitrary_types_allowed=True)

    job_id: UUID = Field(foreign_key="job.id")
    user_id: UUID = Field(foreign_key="user.id")
    task_type: str = Field()
    status: str = Field(default=TaskStatus.PENDING.value)
    result: Optional[JSON] = Field(default=None, sa_column=Column(JSON, nullable=True))
    error_message: Optional[str] = Field(default=None, nullable=True)

    created_at: Optional[datetime] = Field(default=None, sa_column=Column(DateTime(timezone=True), default=func.now()))
    updated_at: Optional[datetime] = Field(default=None, sa_column=Column(DateTime(timezone=True), default=func.now(), onupdate=func.now()))


    def to_dict(self):
        return {
            "id": self.id,
            "job_id": self.job_id,
            "user_id": self.user_id,
            "task_type": self.task_type,
            "status": self.status,
            "result": self.result,
            "error_message": self.error_message,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        } 