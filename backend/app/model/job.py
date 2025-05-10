from datetime import datetime, date
from typing import List, Optional
from sqlmodel import Column, Field, Text, String, ARRAY, DateTime, func
from app.model.base_model import BaseModel

class Job(BaseModel, table=True):
    from_site: str = Field()
    job_url: str = Field()
    logo_url: str = Field()
    job_name: str = Field()
    job_level: Optional[str] = Field(default=None, nullable=True)
    job_type: Optional[str] = Field(default=None, nullable=True)
    company_name: str = Field()
    company_type: Optional[str] = Field(default=None, nullable=True)
    company_address: Optional[str] = Field(default=None, nullable=True)
    company_description: Optional[str] = Field(default=None, sa_column=Column(Text, nullable=True))
    skills: str = Field(sa_column=Column(Text))
    location: Optional[str] = Field(default=None, nullable=True)
    date_posted: Optional[date] = Field(default=None, nullable=True)
    job_description: str = Field(sa_column=Column(Text))
    job_requirement: str = Field(sa_column=Column(Text))
    benefit: Optional[str] = Field(default=None, sa_column=Column(Text, nullable=True))

    created_at: Optional[datetime] = Field(default=None, sa_column=Column(DateTime(timezone=True), default=func.now()))
    updated_at: Optional[datetime] = Field(default=None, sa_column=Column(DateTime(timezone=True), default=func.now(), onupdate=func.now()))
    deleted_at: Optional[datetime] = Field(default=None, sa_column=Column(DateTime(timezone=True), nullable=True))