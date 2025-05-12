from typing import Optional, List
from pydantic import BaseModel, EmailStr, field_validator

from app.schema.award_schema import AwardResponse
from app.schema.base_schema import ModelBaseInfo
from app.schema.education_schema import EducationResponse
from app.schema.experience_schema import ExperienceResponse
from app.schema.project_schema import ProjectResponse
from app.schema.skill_schema import SkillResponse
from app.util.regex import PASSWORD_REGEX


class BaseUser(BaseModel):
    email: EmailStr
    name: Optional[str] = None
    avatar_url: Optional[str] = None
    uploaded_resume: bool = False

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
    experiences: List[ExperienceResponse] = []
    educations: List[EducationResponse] = []
    skills: List[SkillResponse] = []
    awards: List[AwardResponse] = []




class UserUpdate(BaseModel):
    name: Optional[str] = None
    headline: Optional[str] = None
    phone_number: Optional[str] = None
    location: Optional[str] = None
    education: Optional[str] = None
    linkedin_url: Optional[str] = None
    github_url: Optional[str] = None
    avatar_url: Optional[str] = None
    introduction: Optional[str] = None
    uploaded_resume: Optional[bool] = None



class UserPasswordUpdate(BaseModel):
    password: str

    @field_validator("password")
    def check_password_complexity(cls, v):
        if not PASSWORD_REGEX.match(v):
            raise ValueError(
                "Password must be at least 8 characters long, include uppercase, lowercase, number, and special character."
            )
        return v




