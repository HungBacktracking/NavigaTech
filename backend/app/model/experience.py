from datetime import datetime, date
from uuid import UUID
from sqlmodel import Column, Field, func, Boolean, Text, Date, DateTime
from app.model.base_model import BaseModel


class Experience(BaseModel, table=True):
    user_id: UUID = Field(foreign_key="user.id")
    company_name: str = Field()
    title: str = Field()
    employment_type: str = Field(default=None, sa_column=Column(Text, nullable=True))
    description: str = Field(default=None, sa_column=Column(Text, nullable=True))
    achievement: str = Field(default=None, sa_column=Column(Text, nullable=True))
    start_date: date = Field(sa_column=Column(Date, nullable=False))
    end_date: date = Field(sa_column=Column(Date, nullable=False))
    is_current: bool = Field(default=False, sa_column=Column(Boolean, nullable=False))

    created_at: datetime = Field(sa_column=Column(DateTime(timezone=True), default=func.now()))
    updated_at: datetime = Field(sa_column=Column(DateTime(timezone=True), default=func.now(), onupdate=func.now()))
    deleted_at: datetime = Field(sa_column=Column(DateTime(timezone=True), nullable=True))