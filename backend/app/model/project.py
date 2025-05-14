from datetime import datetime, date
from typing import Optional
from uuid import UUID
from sqlmodel import Column, Field, func, Text, DateTime, Date, Index
from app.model.base_model import BaseModel



class Project(BaseModel, table=True):
    __table_args__ = (
        Index("ix_user_project", "id", "user_id", unique=True),
    )

    user_id: UUID = Field(foreign_key="user.id")
    project_name: str = Field()
    role: Optional[str] = Field(default=None, nullable=True)
    description: Optional[str] = Field(default=None, sa_column=Column(Text, nullable=True))
    achievement: Optional[str] = Field(default=None, sa_column=Column(Text, nullable=True))
    start_date: Optional[date] = Field(default=None, sa_column=Column(Date, nullable=True))
    end_date: Optional[date] = Field(default=None, sa_column=Column(Date, nullable=True))

    created_at: Optional[datetime] = Field(default=None, sa_column=Column(DateTime(timezone=True), default=func.now()))
    updated_at: Optional[datetime] = Field(default=None, sa_column=Column(DateTime(timezone=True), default=func.now(), onupdate=func.now()))
    deleted_at: Optional[datetime] = Field(default=None, sa_column=Column(DateTime(timezone=True), nullable=True))