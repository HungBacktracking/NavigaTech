from dependency_injector import containers, providers
from app.resume_building.cv_information_extractor import ResumeParser
from app.resume_building.pdf_parser import ResumePdfParser


class ResumeParserContainer(containers.DeclarativeContainer):
    AI = providers.DependenciesContainer()

    resume_parser = providers.Singleton(ResumeParser, AI.llm_model)
    resume_pdf_parser = providers.Factory(
        ResumePdfParser,
        resume_parser=resume_parser
    )