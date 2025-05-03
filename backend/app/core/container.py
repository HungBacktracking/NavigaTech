from dependency_injector import containers, providers

from app.core.config import configs
from app.core.database import Database
from app.repository import UserRepository
from app.repository.education_repository import EducationRepository
from app.repository.experience_repository import ExperienceRepository
from app.repository.project_repository import ProjectRepository
from app.repository.skill_repository import SkillRepository
from app.services import AuthService, UserService


class Container(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(
        modules=[
            "app.api.endpoints.auth",
            "app.api.endpoints.user",
            "app.core.dependencies",
        ]
    )

    db = providers.Singleton(Database, db_url=configs.DATABASE_URI)

    user_repository = providers.Factory(UserRepository, session_factory=db.provided.session)
    skill_repository = providers.Factory(SkillRepository, session_factory=db.provided.session)
    project_repository = providers.Factory(ProjectRepository, session_factory=db.provided.session)
    experience_repository = providers.Factory(ExperienceRepository, session_factory=db.provided.session)
    education_repository = providers.Factory(EducationRepository, session_factory=db.provided.session)

    auth_service = providers.Factory(AuthService, user_repository=user_repository)
    user_service = providers.Factory(
        UserService,
        user_repository=user_repository,
        skill_repository=skill_repository,
        project_repository=project_repository,
        experience_repository=experience_repository,
        education_repository=education_repository
    )
