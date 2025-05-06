from uuid import UUID

from app.core.s3_client import S3Client
from app.exceptions.custom_error import CustomError
from app.model.user import User
from app.model.user_file import UserFile
from app.repository.user_file_repository import UserFileRepository
from app.repository.user_repository import UserRepository
from app.schema.user_schema import UserDetailResponse
from app.services.base_service import BaseService
from app.util.resume_parser import ResumeParser


class ResumeService(BaseService):
    def __init__(
        self,
        file_repo: UserFileRepository,
        user_repo: UserRepository,
        s3_client: S3Client,
        resume_parser: ResumeParser,
        bucket_name: str
    ):
        self.file_repo = file_repo
        self.user_repo = user_repo
        self.s3 = s3_client
        self.resume_parser = resume_parser
        self.bucket = bucket_name
        super().__init__(file_repo, user_repo)



    def process_resume(self, user_id: UUID):
        user: User = self.user_repo.find_by_id(user_id)
        if not user:
            raise CustomError.NOT_FOUND.as_exception()

        resume: UserFile = self.file_repo.get_by_user_and_type(user_id, "resume")
        if not resume:
            raise CustomError.NOT_FOUND.as_exception()

        resume_obj = self.s3.client.get_object(self.bucket, resume.object_key)
        resume_content = resume_obj["Body"].read().decode(
            "utf-8"
        )
        resume_data = self.resume_parser.parse(resume_content)
        # user_data = UserDetailResponse.model_validate(user)
        # user_data.update(resume_data)

        return resume_data




