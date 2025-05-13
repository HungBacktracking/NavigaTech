from uuid import UUID
from typing import Dict, Any, Optional

from app.core.redis_client import RedisClient
from app.exceptions.custom_error import CustomError
from app.model.job_analytic import JobAnalytic
from app.repository.favorite_job_repository import FavoriteJobRepository
from app.repository.job_analytic_repository import JobAnalyticRepository
from app.schema.job_analytic_schema import JobAnalyticResponse
from app.schema.job_schema import FavoriteJobRequest
from app.services.base_service import BaseService


class JobAnalyticService(BaseService):
    def __init__(
            self,
            job_analytic_repository: JobAnalyticRepository,
            favorite_job_repository: FavoriteJobRepository,
            redis_client: RedisClient = None
    ):
        self.repository = job_analytic_repository
        self.favorite_job_repository = favorite_job_repository
        self.redis_client = redis_client
        super().__init__(job_analytic_repository, favorite_job_repository)
        
    def get_by_job_and_user(self, job_id: UUID, user_id: UUID) -> Optional[JobAnalyticResponse]:
        """
        Get job analytic by job_id and user_id with caching
        """
        # Try to get from cache first - this is the expensive computation result we want to cache
        cache_key = f"full_job_analysis:{job_id}:{user_id}"
        cached_result = None
        
        if self.redis_client:
            try:
                cached_result = self.redis_client.get(cache_key)
                if cached_result:
                    return cached_result
            except Exception as e:
                print(f"Redis error while retrieving job analysis cache: {str(e)}")
        
        # If not in cache, get from database
        analytic = self.repository.find_by_job_and_user(job_id, user_id)
        if not analytic:
            raise CustomError.NOT_FOUND.as_exception()

        result = JobAnalyticResponse.model_validate(analytic)
        
        # Cache the result for a long time since it rarely changes
        if self.redis_client:
            try:
                # Cache for 1 week - analysis is computationally expensive and rarely changes
                self.redis_client.set(cache_key, result, 604800)  # 7 days in seconds
            except Exception as e:
                print(f"Redis error while setting job analysis cache: {str(e)}")
                
        return result

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
            
        # Invalidate the cache since we've updated the analysis
        if self.redis_client:
            try:
                # Clear full analysis cache
                self.redis_client.delete(f"full_job_analysis:{job_id}:{user_id}")
                
                # Also invalidate favorite caches because we've updated the favorite status
                self.redis_client.flush_by_pattern(f"user_favorites:{user_id}:*")
            except Exception as e:
                print(f"Redis error while invalidating caches: {str(e)}")

        return JobAnalyticResponse.model_validate(analytic)
