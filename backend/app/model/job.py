from datetime import datetime, date
from typing import List
from sqlmodel import Column, Field, Text, String, ARRAY, DateTime, func
from app.model.base_model import BaseModel

class Job(BaseModel, table=True):
    job_url: str = Field()
    logo_url: str = Field()
    company_name: str = Field()
    company_type: str = Field(default=None, nullable=True)
    company_address: str = Field(default=None, nullable=True)
    company_description: str = Field(default=None, sa_column=Column(Text, nullable=True))
    job_type: str = Field(default=None, nullable=True)
    skills: List[str] = Field(default=None, sa_column=Column(ARRAY(String), nullable=True))
    location: str = Field(default=None, nullable=True)
    date_posted: date = Field(default=None, nullable=True)
    job_description: str = Field(sa_column=Column(Text))
    job_requirement: str = Field(sa_column=Column(Text))
    benefit: str = Field(default=None, sa_column=Column(Text, nullable=True))
    is_expired: bool = Field(default=None, nullable=True)

    created_at: datetime = Field(sa_column=Column(DateTime(timezone=True), default=func.now()))
    updated_at: datetime = Field(sa_column=Column(DateTime(timezone=True), default=func.now(), onupdate=func.now()))
    deleted_at: datetime = Field(sa_column=Column(DateTime(timezone=True), nullable=True))