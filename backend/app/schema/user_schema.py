from typing import Optional, List
from pydantic import BaseModel, EmailStr, field_validator
from app.schema.base_schema import ModelBaseInfo
from app.schema.project_schema import ProjectResponse
from app.util.regex import PASSWORD_REGEX


class BaseUser(BaseModel):
    email: EmailStr
    name: Optional[str] = None
    avatar_url: Optional[str] = None

    class Config:
        from_attributes = True

class UserBasicResponse(ModelBaseInfo, BaseUser): ...

class UserDetailResponse(ModelBaseInfo, BaseUser):
    headline: Optional[str] = None
    phone_number: Optional[str] = None
    location: Optional[str] = None
    education: Optional[str] = None
    linkedin_url: Optional[str] = None
    github_url: Optional[str] = None
    resume_url: Optional[str] = None
    introduction: Optional[str] = None
    projects: List[ProjectResponse] = []
    experiences: List[ProjectResponse] = []
    educations: List[ProjectResponse] = []
    skills: List[ProjectResponse] = []




class UserUpdate(BaseModel):
    password: Optional[str] = None
    name: Optional[str] = None
    headline: Optional[str] = None
    phone_number: Optional[str] = None
    location: Optional[str] = None
    education: Optional[str] = None
    linkedin_url: Optional[str] = None
    github_url: Optional[str] = None
    avatar_url: Optional[str] = None
    introduction: Optional[str] = None



    @field_validator("password")
    def check_password_complexity(cls, v):
        if not PASSWORD_REGEX.match(v):
            raise ValueError(
                "Password must be at least 8 characters long, include uppercase, lowercase, number, and special character."
            )
        return v




