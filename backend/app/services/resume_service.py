from uuid import UUID

from app.core.s3_client import S3Client
from app.exceptions.custom_error import CustomError
from app.model.user import User
from app.model.user_file import UserFile
from app.pdfparser.pdf_parser import ResumePdfParser
from app.repository.award_repository import AwardRepository
from app.repository.education_repository import EducationRepository
from app.repository.experience_repository import ExperienceRepository
from app.repository.project_repository import ProjectRepository
from app.repository.skill_repository import SkillRepository
from app.repository.user_file_repository import UserFileRepository
from app.repository.user_repository import UserRepository
from app.schema.award_schema import AwardRequest
from app.schema.education_schema import EducationRequest
from app.schema.experience_schema import ExperienceRequest
from app.schema.project_schema import ProjectRequest
from app.schema.skill_schema import SkillRequest
from app.schema.user_schema import UserDetailResponse
from app.services import UserService
from app.services.base_service import BaseService
from io import BytesIO

from app.util.date_formater import DateFormater


class ResumeService(BaseService):
    def __init__(
        self,
        file_repo: UserFileRepository,
        user_repo: UserRepository,
        exp_repo: ExperienceRepository,
        project_repo: ProjectRepository,
        edu_repo: EducationRepository,
        skill_repo: SkillRepository,
        award_repo: AwardRepository,
        user_service: UserService,
        s3_client: S3Client,
        resume_pdf_parser: ResumePdfParser,
        bucket_name: str
    ):
        self.file_repo = file_repo
        self.user_repo = user_repo
        self.exp_repo = exp_repo
        self.project_repo = project_repo
        self.edu_repo = edu_repo
        self.skill_repo = skill_repo
        self.award_repo = award_repo
        self.user_service = user_service
        self.s3 = s3_client
        self.resume_pdf_parser = resume_pdf_parser
        self.bucket = bucket_name
        super().__init__(file_repo, user_repo)


    @staticmethod
    def _bulk_create(
            repo,
            request,
            user_id: UUID,
            items: list,
            fields: list,
            date_fields: set = None
    ):
        """
        Create entities in bulk, excluding any None values from the payload.
        :param repo: Repository with a .create(...) method
        :param request: Schema class to instantiate
        :param user_id: UUID of the user
        :param items: List of dicts containing raw data
        :param fields: List of allowed field names
        :param date_fields: set of field names to convert to date objects
        """

        date_fields = date_fields or set()
        for item in items:
            payload = {}
            for key in fields:
                raw = item.get(key)
                if raw is None:
                    continue
                if key in date_fields:
                    try:
                        payload[key] = DateFormater.format_date(raw)
                    except ValueError:
                        continue
                else:
                    payload[key] = raw
            payload["user_id"] = user_id
            repo.create(request(**payload))




    def process_resume(self, user_id: UUID) -> UserDetailResponse:
        resume: UserFile = self.file_repo.get_by_user_and_type(user_id, "resume")
        if not resume:
            raise CustomError.NOT_FOUND.as_exception()

        resume_obj = self.s3.client.get_object(Bucket=self.bucket, Key=resume.object_key)
        resume_binary_content: bytes = resume_obj["Body"].read()
        data = self.resume_pdf_parser.parse(BytesIO(resume_binary_content))

        update_fields = {key: val for key, val in {
            "name": data.get("name"),
            "headline": data.get("headline"),
            "phone_number": data.get("phone_number"),
            "location": data.get("location"),
            "education": data.get("education"),
            "linkedin_url": data.get("linkedin_url"),
            "github_url": data.get("github_url"),
            "avatar_url": data.get("avatar_url"),
            "resume_url": data.get("resume_url"),
            "introduction": data.get("introduction")
        }.items() if val is not None}
        self.user_repo.update(user_id, User(**update_fields))

        self._bulk_create(
            self.skill_repo,
            SkillRequest,
            user_id,
            data.get("skills", []),
            ["name"]
        )
        self._bulk_create(
            self.project_repo,
            ProjectRequest,
            user_id,
            data.get("projects", []),
            ["project_name", "role", "description", "achievement", "start_date", "end_date"],
            date_fields={"start_date", "end_date"}
        )
        self._bulk_create(
            self.exp_repo,
            ExperienceRequest,
            user_id,
            data.get("experiences", []),
            ["company_name", "title", "location", "employment_type", "description", "achievement", "start_date",
             "end_date", "is_current"],
            date_fields={"start_date", "end_date"}
        )
        self._bulk_create(
            self.edu_repo,
            EducationRequest,
            user_id,
            data.get("educations", []),
            ["major", "school_name", "degree_type", "gpa", "is_current", "description", "start_date", "end_date"],
            date_fields={"start_date", "end_date"}
        )
        self._bulk_create(
            self.award_repo,
            AwardRequest,
            user_id,
            data.get("awards", []),
            ["name", "description", "award_date"],
            date_fields={"award_date"}
        )

        return self.user_service.get_detail_by_id(user_id)




