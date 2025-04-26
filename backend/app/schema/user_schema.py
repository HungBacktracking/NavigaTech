from typing import Optional
from pydantic import BaseModel
from app.schema.base_schema import ModelBaseInfo


class BaseUser(BaseModel):
    email: str
    name: str

    class Config:
        orm_mode = True

class UserResponse(ModelBaseInfo, BaseUser): ...


class UserCreate(BaseModel):
    email: str
    password: str
    name: str

class UserUpdate(BaseModel):
    password: Optional[str] = None
    name: Optional[str] = None




