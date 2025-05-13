from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID

from pydantic import ConfigDict
from sqlmodel import Column, Field, func, DateTime, JSON

from app.model.base_model import BaseModel


class TaskStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class JobTask(BaseModel, table=True):
    __tablename__ = "job_tasks"
    model_config = ConfigDict(arbitrary_types_allowed=True)

    job_id: UUID = Field(foreign_key="job.id")
    user_id: UUID = Field(foreign_key="user.id")
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
            "status": self.status,
            "result": self.result,
            "error_message": self.error_message,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        } 