from datetime import datetime

from sqlmodel import Column, DateTime, Field, SQLModel, func

from app.model.base_model import BaseModel


class User(BaseModel, table=True):
    email: str = Field(unique=True)
    password: str = Field()

    name: str = Field(default=None, nullable=True)
    created_at: datetime = Field(sa_column=Column(DateTime(timezone=True), default=func.now()))
    updated_at: datetime = Field(sa_column=Column(DateTime(timezone=True), default=func.now(), onupdate=func.now()))
