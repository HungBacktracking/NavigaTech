from typing import Optional, TypeVar, Generic, List
from uuid import UUID

from pydantic import BaseModel


T = TypeVar("T")


class ModelBaseInfo(BaseModel):
    id: UUID


class PageRequest(BaseModel):
    page: Optional[int] = 1
    page_size: Optional[int] = 20


class PageResponse(BaseModel, Generic[T]):
    items: List[T]
    total: int
    page: int
    page_size: int
    total_pages: int


class Blank(BaseModel):
    pass
