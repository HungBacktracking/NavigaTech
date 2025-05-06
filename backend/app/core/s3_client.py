import boto3
from botocore.client import Config

class S3Client:
    def __init__(self, region_name: str, access_key_id: str, secret_key: str):
        self.client = boto3.client(
            "s3",
            region_name=region_name,
            aws_access_key_id=access_key_id,
            aws_secret_access_key=secret_key,
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
