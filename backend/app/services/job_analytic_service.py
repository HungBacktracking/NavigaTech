from uuid import UUID
from typing import Dict, Any, Optional, List
import math

from app.core.redis_client import RedisClient
from app.exceptions.custom_error import CustomError
from app.model.job_analytic import JobAnalytic
from app.repository.favorite_job_repository import FavoriteJobRepository
from app.repository.job_analytic_repository import JobAnalyticRepository
from app.repository.job_repository import JobRepository
from app.schema.base_schema import PageResponse
from app.schema.job_analytic_schema import JobAnalyticResponse
from app.schema.job_schema import FavoriteJobRequest, JobFavoriteResponse
from app.convert.job import to_favorite_job_response
from app.services.base_service import BaseService


class JobAnalyticService(BaseService):
    def __init__(
            self,
            job_analytic_repository: JobAnalyticRepository,
            favorite_job_repository: FavoriteJobRepository,
            job_repository: JobRepository,
            redis_client: RedisClient = None
    ):
        self.repository = job_analytic_repository
        self.favorite_job_repository = favorite_job_repository
        self.job_repository = job_repository
        self.redis_client = redis_client
        super().__init__(job_analytic_repository, favorite_job_repository, job_repository)
        
    def get_by_job_and_user(self, job_id: UUID, user_id: UUID) -> Optional[JobFavoriteResponse]:
        cache_key = f"full_job_analysis:{job_id}:{user_id}"
        cached_result = None
        
        if self.redis_client:
            try:
                cached_result = self.redis_client.get(cache_key)
                if cached_result:
                    return cached_result
            except Exception as e:
                print(f"Redis error while retrieving job analysis cache: {str(e)}")

        # Get job analytic
        analytic = self.repository.find_by_job_and_user(job_id, user_id)
        if not analytic:
            raise CustomError.NOT_FOUND.as_exception()
            
        # Get job
        job = self.job_repository.find_by_id(job_id)
        if not job:
            raise CustomError.NOT_FOUND.as_exception()

        # Get favorite status
        favorite = self.favorite_job_repository.find_by_job_and_user_id(job_id, user_id)
        if not favorite:
            raise CustomError.NOT_FOUND.as_exception("Favorite job record not found")

        # Create JobFavoriteResponse using existing converter
        result = to_favorite_job_response(job, favorite, analytic)
        
        # Cache the result for a long time since it rarely changes
        if self.redis_client:
            try:
                # Cache for 1 week - analysis is computationally expensive and rarely changes
                self.redis_client.set(cache_key, result, 604800)  # 7 days in seconds
            except Exception as e:
                print(f"Redis error while setting job analysis cache: {str(e)}")
                
        return result
        
    def get_user_job_analytics(
        self, user_id: UUID, page: int = 1, page_size: int = 20, search: Optional[str] = None
    ) -> PageResponse[JobFavoriteResponse]:
        cache_key = f"user_job_analytics:{user_id}:{page}:{page_size}:{search or 'all'}"
        cached_result = None
        
        if self.redis_client and not search:  # Only cache when not searching
            try:
                cached_result = self.redis_client.get(cache_key)
                if cached_result:
                    return cached_result
            except Exception as e:
                print(f"Redis error while retrieving job analytics list cache: {str(e)}")

        results, total_count = self.repository.find_by_user_with_pagination(
            user_id=user_id, 
            page=page, 
            page_size=page_size,
            search=search
        )

        items = [to_favorite_job_response(job, favorite, analytic) for job, favorite, analytic in results]
        total_pages = math.ceil(total_count / page_size) if total_count > 0 else 1

        response = PageResponse(
            items=items,
            total=total_count,
            page=page,
            page_size=page_size,
            total_pages=total_pages
        )

        if self.redis_client and not search:  # Only cache when not searching
            try:
                self.redis_client.set(cache_key, response, 600)
            except Exception as e:
                print(f"Redis error while setting job analytics list cache: {str(e)}")
        
        return response

    def handle_exist_analysis(self, job_id: UUID, user_id: UUID):
        analytic = self.repository.find_by_job_and_user(job_id, user_id)
        if analytic:
            raise CustomError.EXISTING_RESOURCE.as_exception()

        
    def process_analyze(self, job_id: UUID, user_id: UUID, score_result: Dict[str, Any],
                         analysis_result: Dict[str, Any]) -> JobFavoriteResponse:
        """
        Combine scoring and analysis results and save to database
        
        Args:
            job_id: Job ID
            user_id: User ID
            score_result: Result from scoring process
            analysis_result: Result from analysis process
            
        Returns:
            Complete JobFavoriteResponse with analysis data
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
            fav_job = self.favorite_job_repository.create(favorite_request)
            
        if self.redis_client:
            try:
                self.redis_client.delete(f"full_job_analysis:{job_id}:{user_id}")
                
                self.redis_client.flush_by_pattern(f"user_favorites:{user_id}:*")
                
                self.redis_client.flush_by_pattern(f"user_job_analytics:{user_id}:*")
            except Exception as e:
                print(f"Redis error while invalidating caches: {str(e)}")

        job = self.job_repository.find_by_id(job_id)
        if not job:
            raise CustomError.NOT_FOUND.as_exception("Job not found")
            
        return to_favorite_job_response(job, fav_job, analytic)
