from typing import Optional
from uuid import UUID

from pydantic import BaseModel



class ModelBaseInfo(BaseModel):
    id: UUID

class PageRequest(BaseModel):
    page: Optional[int] = 1
    page_size: Optional[int] = 20

class PageResponse(BaseModel):
    page: int
    page_size: int
    total_count: int
    total_pages: int

class Blank(BaseModel):
    pass
