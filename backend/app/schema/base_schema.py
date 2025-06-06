from typing import Optional, TypeVar, Generic, List
from uuid import UUID

from pydantic import BaseModel, ConfigDict, field_serializer


T = TypeVar("T")


class ModelBaseInfo(BaseModel):
    id: UUID
    
    @field_serializer('id')
    def serialize_uuid(self, uuid_value: UUID) -> str:
        return str(uuid_value)
    
    model_config = ConfigDict(
        from_attributes=True
    )


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
