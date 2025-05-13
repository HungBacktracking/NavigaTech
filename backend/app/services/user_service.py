from typing import Optional

from app.core.redis_client import RedisClient
from app.exceptions.custom_error import CustomError
from app.model.user import User
from app.repository.award_repository import AwardRepository
from app.repository.education_repository import EducationRepository
from app.repository.experience_repository import ExperienceRepository
from app.repository.project_repository import ProjectRepository
from app.repository.skill_repository import SkillRepository
from app.repository.user_repository import UserRepository
from app.schema.award_schema import AwardResponse
from app.schema.education_schema import EducationResponse
from app.schema.experience_schema import ExperienceResponse
from app.schema.project_schema import ProjectResponse
from app.schema.skill_schema import SkillResponse
from app.schema.user_schema import UserDetailResponse, UserBasicResponse, UserUpdate
from app.services.base_service import BaseService


class UserService(BaseService):
    def __init__(
        self,
        user_repository: UserRepository,
        experience_repository: ExperienceRepository,
        project_repository: ProjectRepository,
        education_repository: EducationRepository,
        skill_repository: SkillRepository,
        award_repository: AwardRepository,
        redis_client: RedisClient = None
    ):
        self.user_repository = user_repository
        self.experience_repository = experience_repository
        self.project_repository = project_repository
        self.education_repository = education_repository
        self.skill_repository = skill_repository
        self.award_repository = award_repository
        self.redis_client = redis_client
        super().__init__(
            user_repository,
            experience_repository,
            project_repository,
            education_repository,
            skill_repository
        )


    def get_by_id(self, user_id) -> UserBasicResponse:
        # Use cache for basic user details
        if self.redis_client:
            try:
                cache_key = f"user_basic:{user_id}"
                cached_user = self.redis_client.get(cache_key)
                
                if cached_user:
                    return cached_user
            except Exception as e:
                print(f"Redis error while retrieving user cache: {str(e)}")
        
        user: User = self.user_repository.find_by_id(user_id)
        if not user:
            raise CustomError.NOT_FOUND.as_exception()

        user_response = UserBasicResponse.model_validate(user)
        
        # Cache for 30 minutes - user basic details don't change often
        if self.redis_client:
            try:
                self.redis_client.set(cache_key, user_response, 1800)
            except Exception as e:
                print(f"Redis error while setting user cache: {str(e)}")
            
        return user_response

    def get_detail_by_id(self, user_id) -> UserDetailResponse:
        # User details are good candidates for caching
        if self.redis_client:
            try:
                cache_key = f"user_detail:{user_id}"
                cached_user = self.redis_client.get(cache_key)
                
                if cached_user:
                    return cached_user
            except Exception as e:
                print(f"Redis error while retrieving user detail cache: {str(e)}")
        
        user = self.user_repository.find_by_id(user_id)
        if not user:
            raise CustomError.NOT_FOUND.as_exception()

        projects = self.project_repository.find_by_user_id(user_id)
        experiences = self.experience_repository.find_by_user_id(user_id)
        educations = self.education_repository.find_by_user_id(user_id)
        skills = self.skill_repository.find_by_user_id(user_id)
        awards = self.award_repository.find_by_user_id(user_id)

        user_detail = UserDetailResponse(
            **user.model_dump(),
            projects=[ProjectResponse.model_validate(project) for project in projects],
            experiences=[ExperienceResponse.model_validate(experience) for experience in experiences],
            educations=[EducationResponse.model_validate(edu) for edu in educations],
            skills=[SkillResponse.model_validate(skill) for skill in skills],
            awards=[AwardResponse.model_validate(award) for award in awards]
        )
        
        # Cache for 15 minutes - user details might be updated
        if self.redis_client:
            try:
                self.redis_client.set(cache_key, user_detail, 900)
            except Exception as e:
                print(f"Redis error while setting user detail cache: {str(e)}")
            
        return user_detail

    def update(self, user_id, update_request) -> UserDetailResponse:
        updated_user: Optional[User] = self.user_repository.update(user_id, update_request)
        if not updated_user:
            raise CustomError.NOT_FOUND.as_exception()

        projects = self.project_repository.find_by_user_id(user_id)
        experiences = self.experience_repository.find_by_user_id(user_id)
        educations = self.education_repository.find_by_user_id(user_id)
        skills = self.skill_repository.find_by_user_id(user_id)
        awards = self.award_repository.find_by_user_id(user_id)

        user_detail = UserDetailResponse(
            **updated_user.model_dump(),
            projects=[ProjectResponse.model_validate(project) for project in projects],
            experiences=[ExperienceResponse.model_validate(experience) for experience in experiences],
            educations=[EducationResponse.model_validate(edu) for edu in educations],
            skills=[SkillResponse.model_validate(skill) for skill in skills],
            awards=[AwardResponse.model_validate(award) for award in awards]
        )
        
        # Invalidate any cached user data after update
        if self.redis_client:
            try:
                # Invalidate user-specific caches
                self.redis_client.delete(f"user_basic:{user_id}")
                self.redis_client.delete(f"user_detail:{user_id}")
                
                # Also invalidate any derived caches that depend on user profile
                self.redis_client.flush_by_pattern(f"job_recommendations:{user_id}:*")
                self.redis_client.flush_by_pattern(f"job_analysis:*:{user_id}")
                self.redis_client.flush_by_pattern(f"job_score:*:{user_id}")
            except Exception as e:
                print(f"Redis error while invalidating user caches: {str(e)}")
            
        return user_detail



