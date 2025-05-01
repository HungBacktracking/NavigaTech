from datetime import datetime, date
from uuid import UUID
from sqlmodel import Column, Field, func, Boolean, Text, Date, DateTime, Double
from app.model.base_model import BaseModel


class Education(BaseModel, table=True):
    user_id: UUID = Field(foreign_key="user.id")
    major: str = Field()
    school_name: str = Field(default=None, nullable=True)
    degree_type: str = Field(default=None, nullable=True)
    gpa: float = Field(default=None, sa_column=Column(Double, nullable=True))
    is_current: bool = Field(default=False, sa_column=Column(Boolean, nullable=False))
    description: str = Field(default=None, sa_column=Column(Text, nullable=True))
    start_date: date = Field(sa_column=Column(Date, nullable=False))
    end_date: date = Field(sa_column=Column(Date, nullable=False))

    created_at: datetime = Field(sa_column=Column(DateTime(timezone=True), default=func.now()))
    updated_at: datetime = Field(sa_column=Column(DateTime(timezone=True), default=func.now(), onupdate=func.now()))
    deleted_at: datetime = Field(sa_column=Column(DateTime(timezone=True), nullable=True))