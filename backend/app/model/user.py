from datetime import datetime
from typing import Optional

from sqlmodel import Column, DateTime, Field, func
from app.model.base_model import BaseModel
from sqlalchemy import Text


class User(BaseModel, table=True):
    email: str = Field(unique=True)
    password: str = Field()
    name: str = Field(default=None, nullable=True)
    headline: str = Field(default=None, nullable=True)
    phone_number: str = Field(default=None, nullable=True)
    location: str = Field(default=None, nullable=True)
    education: str = Field(default=None, nullable=True)
    linkedin_url: str = Field(default=None, nullable=True)
    github_url: str = Field(default=None, nullable=True)
    avatar_url: str = Field(default=None, nullable=True)
    resume_url: str = Field(default=None, nullable=True)
    introduction: str = Field(default=None, sa_column=Column(Text, nullable=True))

    created_at: Optional[datetime] = Field(default=None, sa_column=Column(DateTime(timezone=True), default=func.now()))
    updated_at: Optional[datetime] = Field(default=None, sa_column=Column(DateTime(timezone=True), default=func.now(), onupdate=func.now()))
    deleted_at: Optional[datetime] = Field(default=None, sa_column=Column(DateTime(timezone=True), nullable=True))
