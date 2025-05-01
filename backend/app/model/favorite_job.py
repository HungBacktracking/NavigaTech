from datetime import datetime
from uuid import UUID
from sqlalchemy import Column, Field, func, DateTime
from app.model.base_model import BaseModel



class FavoriteJob(BaseModel, table=True):
    job_id: UUID = Field(primary_key=True, foreign_key="job.id")
    user_id: UUID = Field(primary_key=True, foreign_key="user.id")
    is_analyze: bool = Field(default=None, nullable=True)
    resume_url: str = Field(default=None, nullable=True)

    created_at: datetime = Field(sa_column=Column(DateTime(timezone=True), default=func.now()))
    updated_at: datetime = Field(sa_column=Column(DateTime(timezone=True), default=func.now(), onupdate=func.now()))
    deleted_at: datetime = Field(sa_column=Column(DateTime(timezone=True), nullable=True))