from dependency_injector import containers, providers
from app.repository import UserRepository
from app.repository.award_repository import AwardRepository
from app.repository.chatbot_repository import ChatbotRepository
from app.repository.education_repository import EducationRepository
from app.repository.experience_repository import ExperienceRepository
from app.repository.job_repository import JobRepository
from app.repository.project_repository import ProjectRepository
from app.repository.skill_repository import SkillRepository
from app.repository.user_file_repository import UserFileRepository



class RepositoryContainer(containers.DeclarativeContainer):
    database = providers.DependenciesContainer()
    db = database.db
    mongo_db = database.mongo_db
    s3 = database.s3_client

    user_repository = providers.Factory(UserRepository, session_factory=db.provided.session)
    skill_repository = providers.Factory(SkillRepository, session_factory=db.provided.session)
    project_repository = providers.Factory(ProjectRepository, session_factory=db.provided.session)
    experience_repository = providers.Factory(ExperienceRepository, session_factory=db.provided.session)
    education_repository = providers.Factory(EducationRepository, session_factory=db.provided.session)
    award_repository = providers.Factory(AwardRepository, session_factory=db.provided.session)
    job_repository = providers.Factory(JobRepository, session_factory=db.provided.session)
    user_file_repository = providers.Factory(UserFileRepository, session_factory=db.provided.session)
    chatbot_repository = providers.Factory(ChatbotRepository, mongo_db=mongo_db.provided.db)