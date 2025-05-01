from datetime import datetime, date
from uuid import UUID
from sqlalchemy import Column, Field, func, Text, DateTime, Date
from app.model.base_model import BaseModel



class Project(BaseModel, table=True):
    user_id: UUID = Field(foreign_key="user.id")
    project_name: str = Field(default=None, nullable=True)
    role: str = Field(default=None, nullable=True)
    description: str = Field(default=None, sa_column=Column(Text, nullable=True))
    achievement: str = Field(default=None, sa_column=Column(Text, nullable=True))
    start_date: date = Field(sa_column=Column(Date, nullable=False))
    end_date: date = Field(sa_column=Column(Date, nullable=False))

    created_at: datetime = Field(sa_column=Column(DateTime(timezone=True), default=func.now()))
    updated_at: datetime = Field(sa_column=Column(DateTime(timezone=True), default=func.now(), onupdate=func.now()))
    deleted_at: datetime = Field(default=None, nullable=True)