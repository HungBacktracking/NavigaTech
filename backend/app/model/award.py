from datetime import date, datetime
from typing import Optional
from uuid import UUID
from sqlmodel import Column, DateTime, Field, func, Text, Date, Index
from app.model.base_model import BaseModel


class Award(BaseModel, table=True):
    __table_args__ = (
        Index("ix_user_award", "id", "user_id", unique=True),
    )

    user_id: UUID = Field(foreign_key="user.id")
    name: str = Field()
    description: Optional[str] = Field(default=None, sa_column=Column(Text, nullable=True))
    award_date: Optional[date] = Field(default=None, sa_column=Column(Date, nullable=True))

    created_at: Optional[datetime] = Field(default=None, sa_column=Column(DateTime(timezone=True), default=func.now()))
    updated_at: Optional[datetime] = Field(default=None, sa_column=Column(DateTime(timezone=True), default=func.now(), onupdate=func.now()))
    deleted_at: Optional[datetime] = Field(default=None, sa_column=Column(DateTime(timezone=True), nullable=True))