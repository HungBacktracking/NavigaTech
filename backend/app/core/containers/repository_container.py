from dependency_injector import containers, providers
from app.repository import UserRepository
from app.repository.award_repository import AwardRepository
from app.repository.chatbot_repository import ChatbotRepository
from app.repository.education_repository import EducationRepository
from app.repository.experience_repository import ExperienceRepository
from app.repository.favorite_job_repository import FavoriteJobRepository
from app.repository.job_repository import JobRepository
from app.repository.job_task_repository import JobTaskRepository
from app.repository.job_analytic_repository import JobAnalyticRepository
from app.repository.project_repository import ProjectRepository
from app.repository.skill_repository import SkillRepository
from app.repository.user_file_repository import UserFileRepository
from app.repository.elasticsearch_repository import ElasticsearchRepository



class RepositoryContainer(containers.DeclarativeContainer):
    database = providers.DependenciesContainer()
    db = database.db
    mongo_db = database.mongo_db
    s3 = database.s3_client
    elasticsearch_client = database.elasticsearch_client

    user_repository = providers.Factory(
        UserRepository, 
        session_factory=db.provided.session,
        replica_session_factory=db.provided.replica_session
    )
    skill_repository = providers.Factory(
        SkillRepository, 
        session_factory=db.provided.session,
        replica_session_factory=db.provided.replica_session
    )
    project_repository = providers.Factory(
        ProjectRepository, 
        session_factory=db.provided.session,
        replica_session_factory=db.provided.replica_session
    )
    experience_repository = providers.Factory(
        ExperienceRepository, 
        session_factory=db.provided.session,
        replica_session_factory=db.provided.replica_session
    )
    education_repository = providers.Factory(
        EducationRepository, 
        session_factory=db.provided.session,
        replica_session_factory=db.provided.replica_session
    )
    award_repository = providers.Factory(
        AwardRepository, 
        session_factory=db.provided.session,
        replica_session_factory=db.provided.replica_session
    )
    user_file_repository = providers.Factory(
        UserFileRepository, 
        session_factory=db.provided.session,
        replica_session_factory=db.provided.replica_session
    )
    favorite_job_repository = providers.Factory(
        FavoriteJobRepository, 
        session_factory=db.provided.session,
        replica_session_factory=db.provided.replica_session
    )
    chatbot_repository = providers.Factory(ChatbotRepository, mongo_db=mongo_db.provided.db)


    elasticsearch_repository = providers.Singleton(
        ElasticsearchRepository,
        es_client=elasticsearch_client
    )

    job_repository = providers.Factory(
        JobRepository, 
        session_factory=db.provided.session,
        replica_session_factory=db.provided.replica_session
    )
    
    job_task_repository = providers.Factory(
        JobTaskRepository,
        session_factory=db.provided.session,
        replica_session_factory=db.provided.replica_session
    )
    
    job_analytic_repository = providers.Factory(
        JobAnalyticRepository,
        session_factory=db.provided.session
    )