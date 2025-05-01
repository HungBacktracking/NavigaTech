from datetime import datetime, date
from typing import List
from uuid import UUID
from sqlmodel import Column, Field, func, DateTime, String, ARRAY
from app.model.base_model import BaseModel


class JobPref(BaseModel, table=True):
    user_id: UUID = Field(primary_key=True, foreign_key="user.id")
    desired_title: str = Field(default=None, nullable=True)
    desired_location: List[str] = Field(default=None, sa_column=Column(ARRAY(String), nullable=True))
    job_type: List[str] = Field(default=None, sa_column=Column(ARRAY(String), nullable=True))
    min_salary: int = Field(default=None, nullable=True)
    max_salary: int = Field(default=None, nullable=True)

    created_at: datetime = Field(sa_column=Column(DateTime(timezone=True), default=func.now()))
    updated_at: datetime = Field(sa_column=Column(DateTime(timezone=True), default=func.now(), onupdate=func.now()))
    deleted_at: datetime = Field(default=None, nullable=True)