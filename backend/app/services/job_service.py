import math
import uuid
from typing import List
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
from app.schema.base_schema import PageResponse
from app.schema.job_schema import JobSearchRequest, JobFavoriteResponse, JobResponse, FavoriteJobRequest
from app.schema.user_schema import UserDetailResponse
from app.services import UserService
from app.services.base_service import BaseService
from sqlalchemy import select


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
        job_recommendation: JobRecommendation,
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

    def full_text_search_job(
        self, request: JobSearchRequest, user_id: UUID
    ) -> PageResponse[JobResponse]:
        es_results, total_count = self.es_repository.search_jobs(request)

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
                    is_favorite=fav.is_favorite if fav else False
                )
            )

        total_pages = (
            math.ceil(total_count / request.page_size) if total_count > 0 else 1
        )

        return PageResponse(
            items=results,
            total=total_count,
            page=request.page,
            page_size=request.page_size,
            total_pages=total_pages,
        )

    def get_user_favorite_jobs_with_analytics(self, user_id: UUID, page: int = 1, page_size: int = 20) -> PageResponse[JobFavoriteResponse]:
        rows, total_count = self.job_repository.find_favorite_job_with_analytics(
            user_id, page, page_size
        )

        paginated_favorites = [
            to_favorite_job_response(job, fav, analytic) for job, fav, analytic in rows
        ]

        total_pages = math.ceil(total_count / page_size) if total_count > 0 else 1

        return PageResponse(
            items=paginated_favorites,
            total=total_count,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
        )

    def get_job_recommendation(self, user_id: UUID, page: int = 1, page_size: int = 20) -> PageResponse[JobResponse]:
        user_detail: UserDetailResponse = self.user_service.get_detail_by_id(user_id)
        resume_text = self.resume_converter.process(user_detail.model_dump())

        all_recommendations = self.recommendation.search(resume_text, top_k=100)

        offset = (page - 1) * page_size
        total_count = len(all_recommendations)
        paginated_results = all_recommendations[offset : offset + page_size]

        results = []
        for item in paginated_results:
            # Check if job exists in our database
            job = self.job_repository.find_by_url(
                item.get("metadata", {}).get("link", "")
            )

            # Get favorite status if job exists
            fav = None
            if job:
                fav = self.favorite_job_repository.find_by_job_and_user_id(job.id, user_id)

                results.append(
                    JobResponse(
                        id=job.id,
                        job_url=job.job_url,
                        from_site=job.from_site,
                        logo_url=job.logo_url,
                        job_name=job.job_name,
                        job_level=job.job_level,
                        company_name=job.company_name,
                        company_type=job.company_type,
                        company_address=job.company_address,
                        company_description=job.company_description,
                        job_type=job.job_type,
                        skills=job.skills,
                        location=job.location,
                        date_posted=job.date_posted,
                        job_description=job.job_description,
                        job_requirement=job.job_requirement,
                        benefit=job.benefit,
                        is_analyze=fav.is_analyze if fav else False,
                        is_favorite=fav.is_favorite if fav else False
                    )
                )

        total_pages = math.ceil(total_count / page_size) if total_count > 0 else 1

        return PageResponse(
            items=results,
            total=total_count,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
        )

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

    def add_to_favorite(self, job_id: uuid, user_id: uuid) -> PageResponse[JobFavoriteResponse]:
        job: Job = self.job_repository.find_by_id(job_id)
        if not job:
            raise CustomError.NOT_FOUND.as_exception()

        request = FavoriteJobRequest(
            job_id=job_id,
            user_id=user_id,
            is_favorite=True
        )

        fav_job = self.favorite_job_repository.find_by_job_and_user_id(job_id, user_id)
        if fav_job:
            self.favorite_job_repository.update(fav_job.id, request)
        else:
            self.favorite_job_repository.create(request)

        return self.get_user_favorite_jobs_with_analytics(user_id)

    def remove_from_favorite(self, job_id: uuid, user_id: uuid):
        job: Job = self.job_repository.find_by_id(job_id)
        if not job:
            raise CustomError.NOT_FOUND.as_exception()

        fav_job = self.favorite_job_repository.find_by_job_and_user_id(job_id, user_id)
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

    def index_all_jobs(self, batch_size=500, include_deleted=False):
        """
        Index all jobs from database to Elasticsearch
        
        Args:
            batch_size: The number of jobs to process in each batch
            include_deleted: Whether to include soft-deleted jobs
        
        Returns:
            int: The total number of jobs indexed
        """
        # Get total job count
        if include_deleted:
            total_jobs = self.job_repository.get_total_count_including_deleted()
            print(f"Including soft-deleted jobs. Total job count: {total_jobs}")
        else:
            total_jobs = self.job_repository.get_total_count()
            print(f"Only indexing active jobs. Total job count: {total_jobs}")
        
        if total_jobs == 0:
            return 0
        
        # Process in batches for better performance and to avoid memory issues
        total_indexed = 0
        total_batches = (total_jobs + batch_size - 1) // batch_size  # Ceiling division
        
        offset = 0
        success_count = 0
        error_count = 0
        
        while offset < total_jobs:
            try:
                # Get a batch of jobs
                with self.job_repository.replica_session_factory() as session:
                    if include_deleted:
                        statement = select(Job).offset(offset).limit(batch_size)
                    else:
                        statement = select(Job).where(Job.deleted_at == None).offset(offset).limit(batch_size)
                    
                    jobs_batch = session.execute(statement).scalars().all()
                    
                    if not jobs_batch:
                        break
                    
                    # Convert to dictionaries
                    job_dicts = [job.model_dump() for job in jobs_batch]
                    
                    # Bulk index
                    self.es_repository.index_bulk_jobs(job_dicts)
                    
                    # Update counts
                    batch_count = len(job_dicts)
                    success_count += batch_count
                    total_indexed += batch_count
                    
                    print(f"Indexed batch {offset//batch_size + 1}/{total_batches}: {batch_count} jobs")
                
            except Exception as e:
                error_count += 1
                print(f"Error indexing batch starting at offset {offset}: {str(e)}")
                # Continue with next batch despite errors
            
            finally:
                # Move to next batch
                offset += batch_size
        
        # Log results
        print(f"Indexing complete: {success_count} jobs indexed successfully, {error_count} batches with errors")
        
        return total_indexed
