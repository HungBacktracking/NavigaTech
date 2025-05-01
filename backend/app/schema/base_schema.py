from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class ModelBaseInfo(BaseModel):
    id: int

class FindBase(BaseModel):
    ordering: Optional[str]
    page: Optional[int]
    page_size: Optional[int]
    total_count: Optional[int]


class FindDateRange(BaseModel):
    created_at__lt: str
    created_at__lte: str
    created_at__gt: str
    created_at__gte: str


class Blank(BaseModel):
    pass
