from datetime import datetime
from typing import Optional
from uuid import UUID
from sqlmodel import Column, Field, Text, DateTime, func, Index
from app.model.base_model import BaseModel



class JobAnalytic(BaseModel, table=True):
    __table_args__ = (
        Index("ix_job_analytic", "job_id", "user_id", unique=True),
    )

    job_id: UUID = Field(foreign_key="job.id")
    user_id: UUID = Field(foreign_key="user.id")
    match_overall: float = Field()
    match_experience: float = Field()
    match_skills: float = Field()
    weaknesses: str = Field(sa_column=Column(Text, nullable=False))
    strengths: str = Field(sa_column=Column(Text, nullable=False))
    overall_assessment: str = Field(sa_column=Column(Text, nullable=False))
    strength_details: str = Field(sa_column=Column(Text, nullable=False))
    weakness_concerns: str = Field(sa_column=Column(Text, nullable=False))
    recommendations: str = Field(sa_column=Column(Text, nullable=False))
    questions: str = Field(sa_column=Column(Text, nullable=False))
    roadmap: str = Field(sa_column=Column(Text, nullable=False))
    conclusion: str = Field(sa_column=Column(Text, nullable=False))

    created_at: Optional[datetime] = Field(default=None, sa_column=Column(DateTime(timezone=True), default=func.now()))
    updated_at: Optional[datetime] = Field(default=None, sa_column=Column(DateTime(timezone=True), default=func.now(), onupdate=func.now()))
    deleted_at: Optional[datetime] = Field(default=None, sa_column=Column(DateTime(timezone=True), nullable=True))