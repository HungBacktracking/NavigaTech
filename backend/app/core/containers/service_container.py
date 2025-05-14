from dependency_injector import containers, providers
from app.services import AuthService, UserService
from app.services.chatbot_service import ChatbotService
from app.services.job_service import JobService
from app.services.job_task_service import JobTaskService
from app.services.job_analytic_service import JobAnalyticService
from app.services.job_worker import JobWorker
from app.services.kafka_service import KafkaService
from app.services.resume_service import ResumeService
from app.services.s3_service import S3Service
from app.core.redis_client import RedisClient


class ServiceContainer(containers.DeclarativeContainer):
    config = providers.Configuration()
    repos = providers.DependenciesContainer()
    s3_client = providers.Dependency()
    resume_pdf_parser = providers.Dependency()
    chat_engine = providers.Dependency()
    resume_converter = providers.Dependency()
    job_report = providers.DependenciesContainer()
    recommendation = providers.Dependency()
    redis_client = providers.Dependency()

    # Kafka service for message processing
    kafka_service = providers.Singleton(
        KafkaService,
        bootstrap_servers=config.KAFKA_BOOTSTRAP_SERVERS
    )

    auth_service = providers.Factory(AuthService, user_repository=repos.user_repository)
    user_service = providers.Factory(
        UserService,
        user_repository=repos.user_repository,
        skill_repository=repos.skill_repository,
        project_repository=repos.project_repository,
        experience_repository=repos.experience_repository,
        education_repository=repos.education_repository,
        award_repository=repos.award_repository,
        redis_client=redis_client
    )
    job_service = providers.Factory(
        JobService,
        job_repository=repos.job_repository,
        favorite_job_repository=repos.favorite_job_repository,
        elasticsearch_repository=repos.elasticsearch_repository,
        user_service=user_service,
        resume_converter=resume_converter,
        resume_report=job_report.resume_report,
        resume_scorer=job_report.resume_scorer,
        job_recommendation=recommendation,
        redis_client=redis_client
    )
    
    # Job analytic service
    job_analytic_service = providers.Factory(
        JobAnalyticService,
        job_analytic_repository=repos.job_analytic_repository,
        favorite_job_repository=repos.favorite_job_repository,
        redis_client=redis_client
    )
    
    # Job task service
    job_task_service = providers.Factory(
        JobTaskService,
        job_task_repository=repos.job_task_repository
    )
    
    # Job worker for background processing
    job_worker = providers.Singleton(
        JobWorker,
        job_service=job_service,
        job_task_service=job_task_service,
        kafka_service=kafka_service,
        job_analytic_service=job_analytic_service
    )
    
    s3_service = providers.Factory(
        S3Service,
        file_repository=repos.user_file_repository,
        s3_client=s3_client,
        bucket_name=config.AWS_S3_BUCKET_NAME
    )
    resume_service = providers.Factory(
        ResumeService,
        exp_repo=repos.experience_repository,
        project_repo=repos.project_repository,
        edu_repo=repos.education_repository,
        skill_repo=repos.skill_repository,
        award_repo=repos.award_repository,
        user_service=user_service,
        file_repo=repos.user_file_repository,
        user_repo=repos.user_repository,
        s3_client=s3_client,
        resume_pdf_parser=resume_pdf_parser,
        bucket_name=config.AWS_S3_BUCKET_NAME,
        redis_client=redis_client
    )
    chatbot_service = providers.Factory(
        ChatbotService,
        chatbot_repository=repos.chatbot_repository,
        user_repository=repos.user_repository,
        user_service=user_service,
        chat_engine=chat_engine
    )