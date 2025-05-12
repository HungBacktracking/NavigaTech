from dependency_injector import containers, providers
from app.job_report.cv_ai_report import ResumeReport
from app.job_report.cv_grading import ResumeScorer


class JobReportContainer(containers.DeclarativeContainer):
    # No external dependencies for these components
    resume_report = providers.Singleton(ResumeReport)
    resume_scorer = providers.Singleton(ResumeScorer) 