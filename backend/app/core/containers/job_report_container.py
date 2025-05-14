from dependency_injector import containers, providers
from app.job_report.cv_ai_report import ResumeReport
from app.job_report.cv_grading import ResumeScorer


class JobReportContainer(containers.DeclarativeContainer):
    AI = providers.DependenciesContainer()

    resume_report = providers.Singleton(
        ResumeReport,
        llm_chat=AI.llm_model,
        embedding_model=AI.embed_model,
        llm_gemini=AI.llm_gemini
    )
    resume_scorer = providers.Singleton(
        ResumeScorer,
        llm_model=AI.llm_model,
        scoring_model=AI.scoring_model
    )