from datetime import datetime
from uuid import UUID

from sqlalchemy import Column, Field, Text, DateTime, func
from app.model.base_model import BaseModel



class JobAnalytics(BaseModel, table=True):
    job_id: UUID = Field(primary_key=True, foreign_key="job.id")
    user_id: UUID = Field(primary_key=True, foreign_key="user.id")
    general_score: int = Field(default=None, nullable=True)
    general_feedback: str = Field(default=None, sa_column=Column(Text, nullable=True))
    skill_feedback: str = Field(default=None, sa_column=Column(Text, nullable=True))
    role_feedback: str = Field(default=None, sa_column=Column(Text, nullable=True))
    experience_feedback: str = Field(default=None, sa_column=Column(Text, nullable=True))
    language_feedback: str = Field(default=None, sa_column=Column(Text, nullable=True))
    benefit_feedback: str = Field(default=None, sa_column=Column(Text, nullable=True))
    location_feedback: str = Field(default=None, sa_column=Column(Text, nullable=True))
    job_type_feedback: str = Field(default=None, sa_column=Column(Text, nullable=True))
    education_feedback: str = Field(default=None, sa_column=Column(Text, nullable=True))

    created_at: datetime = Field(sa_column=Column(DateTime(timezone=True), default=func.now()))
    updated_at: datetime = Field(sa_column=Column(DateTime(timezone=True), default=func.now(), onupdate=func.now()))
    deleted_at: datetime = Field(default=None, nullable=True)