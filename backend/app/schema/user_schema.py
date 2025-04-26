from typing import List, Optional

from pydantic import BaseModel

from app.schema.base_schema import FindBase, ModelBaseInfo, SearchOptions
from app.util.schema import AllOptional


class BaseUser(BaseModel):
    email: str
    name: str

    class Config:
        orm_mode = True


class BaseUserWithPassword(BaseUser):
    password: str


class User(ModelBaseInfo, BaseUser, metaclass=AllOptional): ...


class FindUser(FindBase, BaseUser, metaclass=AllOptional):
    email__eq: str
    ...


class UpsertUser(BaseUser, metaclass=AllOptional): ...


class FindUserResult(BaseModel):
    founds: Optional[List[User]]
    search_options: Optional[SearchOptions]
