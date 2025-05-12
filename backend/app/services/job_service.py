import uuid
from typing import List, Dict
from uuid import UUID

from app.convert.job import to_favorite_job_response
from app.exceptions.custom_error import CustomError
from app.job_report.cv_ai_report import ResumeReport
from app.job_report.cv_grading import ResumeScorer
from app.model.favorite_job import FavoriteJob
from app.model.job import Job
from app.recommendation.job_recommendation import JobRecommendation
from app.repository.elasticsearch_repository import ElasticsearchRepository
from app.repository.favorite_job_repository import FavoriteJobRepository
from app.repository.job_repository import JobRepository
from app.resume_building.resume_convert import ResumeConverter
from app.schema.job_schema import JobSearchRequest, JobFavoriteResponse, JobResponse, FavoriteJobRequest
from app.schema.user_schema import UserDetailResponse
from app.services import UserService
from app.services.base_service import BaseService


class JobService(BaseService):
    def __init__(
        self,
        job_repository: JobRepository,
        favorite_job_repository: FavoriteJobRepository,
        elasticsearch_repository: ElasticsearchRepository,
        user_service: UserService,
        resume_converter: ResumeConverter,
        resume_report: ResumeReport,
        resume_scorer: ResumeScorer,
        job_recommendation: JobRecommendation
    ):
        self.job_repository = job_repository
        self.favorite_job_repository = favorite_job_repository
        self.es_repository = elasticsearch_repository
        self.user_service = user_service
        self.resume_converter = resume_converter
        self.reporter = resume_report
        self.scorer = resume_scorer
        self.recommendation = job_recommendation
        super().__init__(job_repository, favorite_job_repository)

    def full_text_search_job(self, request: JobSearchRequest, user_id: UUID) -> list[JobResponse]:
        # Use Elasticsearch for searching
        es_results = self.es_repository.search_jobs(request)
        
        # Get favorite status for each job
        job_ids = [UUID(job["id"]) for job in es_results]
        favorites = self.favorite_job_repository.get_favorites_by_job_ids(job_ids, user_id)
        
        results: List[JobResponse] = []
        for job_data in es_results:
            job_id = UUID(job_data["id"])
            fav = favorites.get(job_id)
            
            results.append(
                JobResponse(
                    id=job_id,
                    job_url=job_data.get("job_url"),
                    from_site=job_data.get("from_site"),
                    logo_url=job_data.get("logo_url"),
                    job_name=job_data.get("job_name"),
                    job_level=job_data.get("job_level"),
                    company_name=job_data.get("company_name"),
                    company_type=job_data.get("company_type"),
                    company_address=job_data.get("company_address"),
                    company_description=job_data.get("company_description"),
                    job_type=job_data.get("job_type"),
                    skills=job_data.get("skills"),
                    location=job_data.get("location"),
                    date_posted=job_data.get("date_posted"),
                    job_description=job_data.get("job_description"),
                    job_requirement=job_data.get("job_requirement"),
                    benefit=job_data.get("benefit"),

                    is_analyze=fav.is_analyze if fav else False,
                    resume_url=fav.resume_url if fav else None,
                    is_favorite=fav.is_favorite if fav else False
                )
            )

        return results
    


    def get_user_favorite_jobs_with_analytics(self, user_id: UUID) -> List[JobFavoriteResponse]:
        rows = self.job_repository.find_favorite_job_with_analytics(user_id)

        return [
            to_favorite_job_response(job, fav, analytic)
            for job, fav, analytic in rows
        ]

    def get_job_recommendation(self, user_id: UUID):
        user_detail: UserDetailResponse = self.user_service.get_detail_by_id(user_id)
        resume_text = self.resume_converter.process(user_detail.model_dump())

        return self.recommendation.search(resume_text)

    def analyze_job(self, job_id: UUID, user_id: UUID):
        job: Job = self.job_repository.find_by_id(job_id)
        if not job:
            raise CustomError.NOT_FOUND.as_exception()

        job_dict = job.model_dump()
        jd_text = rf"""\
                Title: {job_dict.get("job_name", "")}
                Job level: {job_dict.get("job_type", "")}
                Working type: {job_dict.get("job_type", "")}
                Company: {job_dict.get("company_name", "")}

                Description: {job_dict.get("job_description", "")}\
                Benefit: {job_dict.get("benefit", "")}\
                Requirements: {job_dict.get("job_requirement", "")}\\
                Skills: {job_dict.get("skills", "")}
            """

        user_detail = self.user_service.get_detail_by_id(user_id)
        resume_text = self.resume_converter.process(user_detail.model_dump())

        return self.reporter.run(resume_text, jd_text)

    def generate_resume(self, job_id: UUID, user_id: UUID):
        pass

    def score_job(self, job_id: UUID, user_id: UUID):
        job: Job = self.job_repository.find_by_id(job_id)
        if not job:
            raise CustomError.NOT_FOUND.as_exception()

        job_dict = job.model_dump()
        jd_text = rf"""\
            Title: {job_dict.get("job_name", "")}
            Job level: {job_dict.get("job_type", "")}
            Working type: {job_dict.get("job_type", "")}
            Company: {job_dict.get("company_name", "")}
            
            Description: {job_dict.get("job_description", "")}\
            Benefit: {job_dict.get("benefit", "")}\
            Requirements: {job_dict.get("job_requirement", "")}\\
            Skills: {job_dict.get("skills", "")}
        """

        user_detail = self.user_service.get_detail_by_id(user_id)
        resume_text = self.resume_converter.process(user_detail.model_dump())

        return self.scorer.final_score(resume_text, jd_text)

    def add_to_favorite(self, job_id: uuid, user_id: uuid):
        job: Job = self.job_repository.find_by_id(job_id)
        if not job:
            raise CustomError.NOT_FOUND.as_exception()

        request = FavoriteJobRequest(
            job_id=job_id,
            user_id=user_id,
            is_favorite=True
        )

        fav_job = self.favorite_job_repository.find_by_user_id(user_id)
        if fav_job:
            self.favorite_job_repository.update(fav_job.id, request)
        else:
            self.favorite_job_repository.create(request)

        return self.get_user_favorite_jobs_with_analytics(user_id)

    def remove_from_favorite(self, job_id: uuid, user_id: uuid):
        job: Job = self.job_repository.find_by_id(job_id)
        if not job:
            raise CustomError.NOT_FOUND.as_exception()

        fav_job = self.favorite_job_repository.find_by_user_id(user_id)
        if fav_job:
            request = FavoriteJobRequest(
                job_id=job_id,
                user_id=user_id,
                is_favorite=False
            )
            self.favorite_job_repository.update(fav_job.id, request)
        else:
            raise CustomError.NOT_FOUND.as_exception()

        return self.get_user_favorite_jobs_with_analytics(user_id)


        
    def index_all_jobs(self):
        """Index all jobs from database to Elasticsearch"""
        jobs = self.job_repository.get_all()
        job_dicts = [job.model_dump() for job in jobs]

        # Bulk index
        self.es_repository.index_bulk_jobs(job_dicts)
            
        return len(job_dicts)






