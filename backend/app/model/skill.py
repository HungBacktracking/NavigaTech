from datetime import datetime
from typing import Optional
from uuid import UUID
from sqlmodel import Column, DateTime, Field, func
from app.model.base_model import BaseModel


class Skill(BaseModel, table=True):
    user_id: UUID = Field(foreign_key="user.id")
    name: str = Field()

    created_at: Optional[datetime] = Field(default=None, sa_column=Column(DateTime(timezone=True), default=func.now()))
    updated_at: Optional[datetime] = Field(default=None, sa_column=Column(DateTime(timezone=True), default=func.now(), onupdate=func.now()))
    deleted_at: Optional[datetime] = Field(default=None, sa_column=Column(DateTime(timezone=True), nullable=True))