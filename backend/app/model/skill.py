from datetime import datetime
from uuid import UUID
from sqlalchemy import Column, DateTime, Field, func
from app.model.base_model import BaseModel


class Skill(BaseModel, table=True):
    user_id: UUID = Field(foreign_key="user.id")
    name: str = Field()

    created_at: datetime = Field(sa_column=Column(DateTime(timezone=True), default=func.now()))
    updated_at: datetime = Field(sa_column=Column(DateTime(timezone=True), default=func.now(), onupdate=func.now()))
    deleted_at: datetime = Field(sa_column=Column(DateTime(timezone=True), nullable=True))