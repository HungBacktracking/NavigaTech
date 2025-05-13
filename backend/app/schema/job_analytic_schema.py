from pydantic import BaseModel
from app.schema.base_schema import ModelBaseInfo



class BaseJobAnalytic(BaseModel):
    match_overall: float
    match_experience: float
    match_skills: float
    weaknesses: str
    strengths: str
    overall_assessment: str
    strength_details: str
    weakness_concerns: str
    recommendations: str
    questions: str
    roadmap: str
    conclusion: str

    class Config:
        from_attributes = True

class JobAnalyticRequest(BaseJobAnalytic): ...

class JobAnalyticResponse(ModelBaseInfo, BaseJobAnalytic): ...








