import boto3
from botocore.client import Config
from app.core.config import configs

class S3Client:
    def __init__(self):
        self.client = boto3.client(
            "s3",
            region_name=configs.aws_region,
            aws_access_key_id=configs.aws_access_key,
            aws_secret_access_key=configs.aws_secret_key,
            config=Config(signature_version="s3v4")
        )

    def generate_presigned_put(self, bucket: str, key: str, expires_in: int):
        return self.client.generate_presigned_url(
            "put_object",
            Params={"Bucket": bucket, "Key": key},
            ExpiresIn=expires_in
        )

    def generate_presigned_get(self, bucket: str, key: str, expires_in: int):
        return self.client.generate_presigned_url(
            "get_object",
            Params={"Bucket": bucket, "Key": key},
            ExpiresIn=expires_in
        )
