from dependency_injector import containers, providers

from app.resume_building.cv_information_extractor import ResumeParser
from app.resume_building.pdf_parser import ResumePdfParser
from app.core.config import configs
from app.core.database import Database
from app.core.s3_client import S3Client
from app.repository import UserRepository
from app.repository.award_repository import AwardRepository
from app.repository.education_repository import EducationRepository
from app.repository.experience_repository import ExperienceRepository
from app.repository.user_file_repository import UserFileRepository
from app.repository.job_repository import JobRepository
from app.repository.project_repository import ProjectRepository
from app.repository.skill_repository import SkillRepository
from app.services import AuthService, UserService
from app.services.job_service import JobService
from app.services.resume_service import ResumeService
from app.services.s3_service import S3Service
import google.generativeai as genai


def create_llm_model(api_key: str, model_name: str = "gemini-2.0-flash"):
    genai.configure(api_key=api_key)
    return genai.GenerativeModel(model_name)



class Container(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(
        modules=[
            "app.api.endpoints.auth",
            "app.api.endpoints.user",
            "app.api.endpoints.job",
            "app.core.dependencies",
        ]
    )

    # Database
    db = providers.Singleton(Database, db_url=configs.DATABASE_URI)

    # S3 Client
    s3_client = providers.Factory(
        S3Client,
        region_name=configs.AWS_REGION,
        access_key_id=configs.AWS_ACCESS_KEY_ID,
        secret_key=configs.AWS_SECRET_KEY
    )

    # Resume parser
    llm_model = providers.Singleton(
        create_llm_model,
        api_key=configs.GEMINI_TOKEN,
        model_name=configs.GEMINI_MODEL_NAME,
    )
    resume_parser = providers.Factory(ResumeParser, llm_model)
    resume_pdf_parser = providers.Factory(
        ResumePdfParser,
        resume_parser=resume_parser
    )


    # Repositories
    user_repository = providers.Factory(UserRepository, session_factory=db.provided.session)
    skill_repository = providers.Factory(SkillRepository, session_factory=db.provided.session)
    project_repository = providers.Factory(ProjectRepository, session_factory=db.provided.session)
    experience_repository = providers.Factory(ExperienceRepository, session_factory=db.provided.session)
    education_repository = providers.Factory(EducationRepository, session_factory=db.provided.session)
    award_repository = providers.Factory(AwardRepository, session_factory=db.provided.session)
    job_repository = providers.Factory(JobRepository, session_factory=db.provided.session)
    user_file_repository = providers.Factory(UserFileRepository, session_factory=db.provided.session)

    # Services
    auth_service = providers.Factory(AuthService, user_repository=user_repository)
    user_service = providers.Factory(
        UserService,
        user_repository=user_repository,
        skill_repository=skill_repository,
        project_repository=project_repository,
        experience_repository=experience_repository,
        education_repository=education_repository
    )
    job_service = providers.Factory(JobService, job_repository=job_repository)
    s3_service = providers.Factory(
        S3Service,
        file_repository=user_file_repository,
        s3_client=s3_client,
        bucket_name=configs.AWS_S3_BUCKET_NAME
    )
    resume_service = providers.Factory(
        ResumeService,

        exp_repo=experience_repository,
        project_repo=project_repository,
        edu_repo=education_repository,
        skill_repo=skill_repository,
        award_repo=award_repository,
        user_service=user_service,
        file_repo=user_file_repository,
        user_repo=user_repository,
        s3_client=s3_client,
        resume_pdf_parser=resume_pdf_parser,
        bucket_name=configs.AWS_S3_BUCKET_NAME
    )
