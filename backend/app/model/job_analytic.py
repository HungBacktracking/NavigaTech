from datetime import datetime
from typing import Optional
from uuid import UUID
from sqlmodel import Column, Field, Text, DateTime, func
from app.model.base_model import BaseModel



class JobAnalytic(BaseModel, table=True):
    job_id: UUID = Field(foreign_key="job.id")
    user_id: UUID = Field(foreign_key="user.id")
    general_score: int = Field()
    general_feedback: str = Field(sa_column=Column(Text))
    skill_feedback: str = Field(sa_column=Column(Text))
    role_feedback: str = Field(sa_column=Column(Text))
    experience_feedback: str = Field(sa_column=Column(Text))
    benefit_feedback: str = Field(sa_column=Column(Text))
    education_feedback: str = Field(sa_column=Column(Text))

    created_at: Optional[datetime] = Field(default=None, sa_column=Column(DateTime(timezone=True), default=func.now()))
    updated_at: Optional[datetime] = Field(default=None, sa_column=Column(DateTime(timezone=True), default=func.now(), onupdate=func.now()))
    deleted_at: Optional[datetime] = Field(default=None, sa_column=Column(DateTime(timezone=True), nullable=True))