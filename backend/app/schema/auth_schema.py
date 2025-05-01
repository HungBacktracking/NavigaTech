from datetime import datetime
from pydantic import BaseModel, EmailStr, field_validator
from app.schema.user_schema import UserResponse
from app.util.regex import PASSWORD_REGEX


class SignIn(BaseModel):
    email: EmailStr
    password: str


class SignUp(BaseModel):
    name: str
    email: EmailStr
    password: str

    @field_validator("password")
    def check_password_complexity(cls, v):
        print(v)
        print("Validating:", repr(v), "=>", bool(PASSWORD_REGEX.match(v)))
        if not PASSWORD_REGEX.match(v):
            raise ValueError(
                "Password must be at least 8 characters long, include uppercase, lowercase, number, and special character."
            )
        return v


class Payload(BaseModel):
    id: int
    email: str
    name: str


class SignInResponse(BaseModel):
    access_token: str
    expiration: datetime
    user_info: UserResponse
