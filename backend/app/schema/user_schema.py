from typing import Optional
from pydantic import BaseModel, EmailStr, field_validator
from app.schema.base_schema import ModelBaseInfo
from app.util.regex import PASSWORD_REGEX


class BaseUser(BaseModel):
    email: EmailStr
    name: str

    class Config:
        from_attributes = True

class UserResponse(ModelBaseInfo, BaseUser): ...



class UserUpdate(BaseModel):
    password: Optional[str] = None
    name: Optional[str] = None


    @field_validator("password")
    def check_password_complexity(cls, v):
        if not PASSWORD_REGEX.match(v):
            raise ValueError(
                "Password must be at least 8 characters long, include uppercase, lowercase, number, and special character."
            )
        return v




