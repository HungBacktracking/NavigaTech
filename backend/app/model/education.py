from datetime import datetime, date
from typing import Optional
from uuid import UUID
from sqlmodel import Column, Field, func, Boolean, Text, Date, DateTime, Double
from app.model.base_model import BaseModel


class Education(BaseModel, table=True):
    user_id: UUID = Field(foreign_key="user.id")
    major: str = Field()
    school_name: str = Field()
    degree_type: str = Field()
    gpa: Optional[str] = Field(default=None, nullable=True)
    is_current: bool = Field(default=False, sa_column=Column(Boolean, nullable=False))
    description: Optional[str] = Field(default=None, sa_column=Column(Text, nullable=True))
    start_date: Optional[date] = Field(default=None, sa_column=Column(Date, nullable=True))
    end_date: Optional[date] = Field(default=None, sa_column=Column(Date, nullable=True))

    created_at: Optional[datetime] = Field(default=None, sa_column=Column(DateTime(timezone=True), default=func.now()))
    updated_at: Optional[datetime] = Field(default=None, sa_column=Column(DateTime(timezone=True), default=func.now(), onupdate=func.now()))
    deleted_at: Optional[datetime] = Field(default=None, sa_column=Column(DateTime(timezone=True), nullable=True))