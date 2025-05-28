from dependency_injector import containers, providers
import logging
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
from app.core.containers.redis_container import RedisContainer

class ApplicationContainer(containers.DeclarativeContainer):
    logger = logging.getLogger(__name__)
    
    wiring_config = containers.WiringConfiguration(
        modules=[
            "app.api.endpoints.auth",
            "app.api.endpoints.user",
            "app.api.endpoints.job",
            "app.api.endpoints.job_analysis",
            "app.api.endpoints.job_task",
            "app.api.endpoints.ws",
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
    
    redis = providers.Container(
        RedisContainer,
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
        JobReportContainer,
        AI=AI
    )
    
    recommendation = providers.Container(
        RecommendationContainer,
        AI=AI,
        database=database
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
        recommendation=recommendation.job_recommendation,
        redis_client=redis.redis_client,
    )
    
    # Start the job worker when the container is initialized
    def init_resources(self):
        super().init_resources()
        
        # Initialize and start the Kafka notification consumer for WebSocket notifications
        try:
            kafka_service = self.services.kafka_service()
            self.logger.info("Starting Kafka notification consumer...")
            kafka_service.start_notification_consumer()
            self.logger.info("Kafka notification consumer started successfully")
        except Exception as e:
            self.logger.error(f"Failed to start Kafka notification consumer: {str(e)}")
        
    def shutdown_resources(self):
        # Stop the job worker if it exists
        if hasattr(self.services, 'job_worker'):
            try:
                worker = self.services.job_worker()
                if worker:
                    self.logger.info("Stopping job worker...")
                    worker.stop()
                    self.logger.info("Job worker stopped successfully")
            except Exception as e:
                self.logger.error(f"Error stopping job worker: {str(e)}")
                
        # Stop the notification consumer
        if hasattr(self.services, 'kafka_service'):
            try:
                kafka = self.services.kafka_service()
                if kafka:
                    self.logger.info("Stopping Kafka notification consumer...")
                    kafka.stop_notification_consumer()
                    self.logger.info("Kafka notification consumer stopped successfully")
            except Exception as e:
                self.logger.error(f"Error stopping Kafka notification consumer: {str(e)}")
                
        super().shutdown_resources()
