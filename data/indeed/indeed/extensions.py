import os
import boto3
from dotenv import load_dotenv

load_dotenv()

class S3UploadExtension:
    def __init__(self):
        self.s3 = boto3.client(
            's3',
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
            region_name=os.getenv("AWS_REGION")
        )

    def spider_closed(self, spider):

        try:
            bucket_name = os.getenv("AWS_S3_BUCKET")
            s3_key = f"data/linkedin_jobs.json"
            local_path = "indeed_jobs.json"

            spider.logger.info(
                f"[S3UploadExtension] Start upload {local_path} → s3://{bucket_name}/{s3_key}"
            )
            self.s3.upload_file(local_path, bucket_name, s3_key)
            spider.logger.info(f"[S3UploadExtension] Upload completed!.")
        except Exception as e:
            spider.logger.error(f"[S3UploadExtension] Upload failed: {e}")
