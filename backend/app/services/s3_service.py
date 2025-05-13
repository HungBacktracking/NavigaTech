from uuid import uuid4, UUID

from app.core.s3_client import S3Client
from app.exceptions.custom_error import CustomError
from app.model.user_file import UserFile
from app.repository.user_file_repository import UserFileRepository
from app.schema.s3_schema import UploadResponse, DownloadResponse
from app.services.base_service import BaseService


class S3Service(BaseService):
    def __init__(self, file_repository: UserFileRepository, s3_client: S3Client, bucket_name: str):
        self.file_repository = file_repository
        self.s3 = s3_client
        self.bucket = bucket_name
        super().__init__(file_repository)

    def get_upload_url(self, user_id: UUID, file_type: str) -> UploadResponse:
        if file_type not in ("avatar", "resume"):
            raise CustomError.INVALID_FILE_TYPE.as_exception()

        file_id: UUID = uuid4()
        object_key = f"users/{user_id}/{file_type}/{file_id}"
        url = self.s3.generate_presigned_put(
            bucket=self.bucket,
            key=object_key,
            expires_in=600
        )

        meta = UserFile(
            id=file_id,
            user_id=user_id,
            file_type=file_type,
            object_key=object_key
        )
        current_file = self.file_repository.get_by_user_and_type(user_id, file_type)
        if current_file:
            self.file_repository.update(current_file.id, meta)
        else: self.file_repository.create(meta)

        return UploadResponse(upload_url=url, object_key=object_key)

    def get_download_url(self, user_id: UUID, file_type: str) -> DownloadResponse:
        meta = self.file_repository.get_by_user_and_type(user_id, file_type)
        if not meta:
            raise CustomError.NOT_FOUND.as_exception()

        url = self.s3.generate_presigned_get(
            bucket=self.bucket,
            key=meta.object_key,
            expires_in=600
        )

        return DownloadResponse(download_url=url)

    def get_by_key(self, key: str):
        try:
            obj = self.s3.client.get_object(Bucket=self.bucket, Key=key)
            file = obj['Body'].read()
            return file
        except Exception as e:
            raise CustomError.INTERNAL_SERVER_ERROR.as_exception()
