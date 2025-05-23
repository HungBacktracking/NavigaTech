from uuid import UUID

from pydantic import BaseModel
from app.schema.base_schema import ModelBaseInfo



class BaseSkill(BaseModel):
    name: str

    class Config:
        from_attributes = True

class SkillResponse(ModelBaseInfo, BaseSkill): ...

class SkillRequest(BaseSkill):
    user_id: UUID