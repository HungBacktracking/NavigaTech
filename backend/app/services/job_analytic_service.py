from uuid import UUID
from typing import Dict, Any, Optional

from app.exceptions.custom_error import CustomError
from app.model.job_analytic import JobAnalytic
from app.repository.favorite_job_repository import FavoriteJobRepository
from app.repository.job_analytic_repository import JobAnalyticRepository
from app.schema.job_analytic_schema import JobAnalyticResponse
from app.schema.job_schema import FavoriteJobRequest


class JobAnalyticService:
    def __init__(
            self,
            job_analytic_repository: JobAnalyticRepository,
            favorite_job_repository: FavoriteJobRepository
    ):
        self.repository = job_analytic_repository
        self.favorite_job_repository = favorite_job_repository
        
    def get_by_job_and_user(self, job_id: UUID, user_id: UUID) -> Optional[JobAnalyticResponse]:
        """
        Get job analytic by job_id and user_id
        """
        analytic = self.repository.find_by_job_and_user(job_id, user_id)
        if not analytic:
            raise CustomError.NOT_FOUND.as_exception()

        return JobAnalyticResponse.model_validate(analytic)

    def handle_exist_analysis(self, job_id: UUID, user_id: UUID):
        analytic = self.repository.find_by_job_and_user(job_id, user_id)
        if analytic:
            raise CustomError.EXISTING_RESOURCE.as_exception()

        
    def process_analyze(self, job_id: UUID, user_id: UUID, score_result: Dict[str, Any],
                         analysis_result: Dict[str, Any]) -> JobAnalyticResponse:
        """
        Combine scoring and analysis results and save to database
        """

        match_overall = score_result.get("match_overall", 0)
        match_experience = score_result.get("match_experience", 0)
        match_skills = score_result.get("match_skills", 0)
        weaknesses = score_result.get("weaknesses", "")
        strengths = score_result.get("strengths", "")

        overall_assessment = analysis_result.get("overall_assessment", "")
        strength_details = analysis_result.get("strength_details", "")
        weakness_concerns = analysis_result.get("weakness_concerns", "")
        recommendations = analysis_result.get("recommendations", "")
        questions = analysis_result.get("questions", "")
        roadmap = analysis_result.get("roadmap", "")
        conclusion = analysis_result.get("conclusion", "")
        
        # Combine data into a single dictionary
        combined_data = {
            "match_overall": match_overall,
            "match_experience": match_experience,
            "match_skills": match_skills,
            "weaknesses": weaknesses,
            "strengths": strengths,
            "overall_assessment": overall_assessment,
            "strength_details": strength_details,
            "weakness_concerns": weakness_concerns,
            "recommendations": recommendations,
            "questions": questions,
            "roadmap": roadmap,
            "conclusion": conclusion
        }
        analytic = self.repository.create_or_update(job_id, user_id, combined_data)

        favorite_request = FavoriteJobRequest(
            job_id=job_id,
            user_id=user_id,
            is_analyze=True
        )

        fav_job = self.favorite_job_repository.find_by_job_and_user_id(job_id, user_id)
        if fav_job:
            self.favorite_job_repository.update(fav_job.id, favorite_request)
        else:
            self.favorite_job_repository.create(favorite_request)

        return JobAnalyticResponse.model_validate(analytic)

