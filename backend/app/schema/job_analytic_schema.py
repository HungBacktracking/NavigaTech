from pydantic import BaseModel
from app.schema.base_schema import ModelBaseInfo



class BaseJobAnalytic(BaseModel):
    general_score: int
    general_feedback: str
    skill_feedback: str
    role_feedback: str
    experience_feedback: str
    benefit_feedback: str
    education_feedback: str

    class Config:
        from_attributes = True

class JobAnalyticResponse(ModelBaseInfo, BaseJobAnalytic): ...








