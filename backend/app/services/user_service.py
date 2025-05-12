from typing import Optional

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
        award_repository: AwardRepository
    ):
        self.user_repository = user_repository
        self.experience_repository = experience_repository
        self.project_repository = project_repository
        self.education_repository = education_repository
        self.skill_repository = skill_repository
        self.award_repository = award_repository
        super().__init__(
            user_repository,
            experience_repository,
            project_repository,
            education_repository,
            skill_repository
        )


    def get_by_id(self, user_id) -> UserBasicResponse:
        user: User = self.user_repository.find_by_id(user_id)
        if not user:
            raise CustomError.NOT_FOUND.as_exception()

        return UserBasicResponse.model_validate(user)

    def get_detail_by_id(self, user_id) -> UserDetailResponse:
        user = self.user_repository.find_by_id(user_id)
        if not user:
            raise CustomError.NOT_FOUND.as_exception()

        projects = self.project_repository.find_by_user_id(user_id)
        experiences = self.experience_repository.find_by_user_id(user_id)
        educations = self.education_repository.find_by_user_id(user_id)
        skills = self.skill_repository.find_by_user_id(user_id)
        awards = self.award_repository.find_by_user_id(user_id)

        return UserDetailResponse(
            **user.model_dump(),
            projects=[ProjectResponse.model_validate(project) for project in projects],
            experiences=[ExperienceResponse.model_validate(experience) for experience in experiences],
            educations=[EducationResponse.model_validate(edu) for edu in educations],
            skills=[SkillResponse.model_validate(skill) for skill in skills],
            awards=[AwardResponse.model_validate(award) for award in awards]
        )

    def update(self, user_id, update_request) -> UserDetailResponse:
        updated_user: Optional[User] = self.user_repository.update(user_id, update_request)
        if not updated_user:
            raise CustomError.NOT_FOUND.as_exception()

        projects = self.project_repository.find_by_user_id(user_id)
        experiences = self.experience_repository.find_by_user_id(user_id)
        educations = self.education_repository.find_by_user_id(user_id)
        skills = self.skill_repository.find_by_user_id(user_id)
        awards = self.award_repository.find_by_user_id(user_id)

        return UserDetailResponse(
            **updated_user.model_dump(),
            projects=[ProjectResponse.model_validate(project) for project in projects],
            experiences=[ExperienceResponse.model_validate(experience) for experience in experiences],
            educations=[EducationResponse.model_validate(edu) for edu in educations],
            skills=[SkillResponse.model_validate(skill) for skill in skills],
            awards=[AwardResponse.model_validate(award) for award in awards]
        )



