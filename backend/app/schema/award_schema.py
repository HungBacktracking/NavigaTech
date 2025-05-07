from datetime import date
from typing import Optional
from uuid import UUID

from pydantic import BaseModel
from app.schema.base_schema import ModelBaseInfo


class BaseAward(BaseModel):
    name: str
    description: Optional[str] = None
    award_date: Optional[date] = None

    class Config:
        from_attributes = True

class AwardResponse(ModelBaseInfo, BaseAward): ...

class AwardRequest(BaseAward):
    user_id: UUID