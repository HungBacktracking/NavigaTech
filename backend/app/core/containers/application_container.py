from dependency_injector import containers, providers
from app.core.config import configs
from app.core.containers.chatbot_container import ChatbotContainer
from app.core.containers.database_container import DatabaseContainer
from app.core.containers.ai_container import AIContainer
from app.core.containers.repository_container import RepositoryContainer
from app.core.containers.resume_parser_container import ResumeParserContainer
from app.core.containers.job_report_container import JobReportContainer
from app.core.containers.resume_converter_container import ResumeConverterContainer
from app.core.containers.recommendation_container import RecommendationContainer
from app.core.containers.service_container import ServiceContainer



class ApplicationContainer(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(
        modules=[
            "app.api.endpoints.auth",
            "app.api.endpoints.user",
            "app.api.endpoints.job",
            "app.api.endpoints.chat",
            "app.api.endpoints.resume",
            "app.core.dependencies",
        ]
    )

    config = providers.Configuration()
    config.override(configs.dict())

    database = providers.Container(
        DatabaseContainer,
        config=config,
    )

    AI = providers.Container(
        AIContainer,
        config=config,
    )

    resume_parser = providers.Container(
        ResumeParserContainer,
        AI=AI
    )
    
    resume_converter = providers.Container(
        ResumeConverterContainer
    )
    
    job_report = providers.Container(
        JobReportContainer
    )
    
    recommendation = providers.Container(
        RecommendationContainer
    )

    chatbot = providers.Container(
        ChatbotContainer,
        config=config,
        database=database,
        AI=AI
    )

    repositories = providers.Container(
        RepositoryContainer,
        database=database
    )

    services = providers.Container(
        ServiceContainer,
        config=config,
        repos=repositories,
        s3_client=database.s3_client,
        resume_pdf_parser=resume_parser.resume_pdf_parser,
        chat_engine=chatbot.chat_engine,
        resume_converter=resume_converter.resume_converter,
        job_report=job_report,
        recommendation=recommendation.job_recommendation
    )
