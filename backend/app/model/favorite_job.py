from datetime import datetime
from typing import Optional
from uuid import UUID
from sqlmodel import Column, Field, func, DateTime
from app.model.base_model import BaseModel



class FavoriteJob(BaseModel, table=True):
    job_id: UUID = Field(foreign_key="job.id")
    user_id: UUID = Field(foreign_key="user.id")
    is_analyze: bool = Field(default=False)
    is_generated_resume: bool = Field(default=False)
    is_favorite: bool = Field(default=False)

    created_at: Optional[datetime] = Field(default=None, sa_column=Column(DateTime(timezone=True), default=func.now()))
    updated_at: Optional[datetime] = Field(default=None, sa_column=Column(DateTime(timezone=True), default=func.now(), onupdate=func.now()))
    deleted_at: Optional[datetime] = Field(default=None, sa_column=Column(DateTime(timezone=True), nullable=True))