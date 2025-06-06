import os

import boto3
from botocore.exceptions import ClientError
from dotenv import load_dotenv

KEYWORDS = [
    # Vai trò chính (Developer / Engineer / QA / Support)
    "software developer",
    "software engineer",
    "full stack developer",
    "frontend developer",
    "backend developer",
    "web developer",
    "mobile developer",
    "devops engineer",
    "site reliability engineer",
    "system engineer",
    "network engineer",
    "qa engineer",
    "test automation engineer",
    "it support engineer",
    "it administrator",
    "database administrator",

    # Data / AI / ML / Security / Cloud
    "data analyst",
    "data engineer",
    "data scientist",
    "machine learning engineer",
    "ai engineer",
    "security engineer",
    "information security analyst",
    "cloud engineer",
    "aws engineer",
    "azure engineer",
    "google cloud engineer",

    # Quản lý / Lãnh đạo / Kiến trúc
    "technical lead",
    "software architect",
    "it project manager",
    "business analyst",

    # Thiết kế / UX/UI
    "ux ui designer",

    # Các lĩnh vực đặc thù / Emerging Tech
    "iot developer",
    "robotics engineer",
    "automation engineer",
    "blockchain engineer",
]

load_dotenv()

def upload_to_s3():
    try:
        s3 = boto3.client(
            's3',
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
            region_name=os.getenv("AWS_REGION")
        )

        bucket_name = os.getenv("AWS_S3_BUCKET")
        s3_key = f"data/linkedin_jobs.json"

        local_path = "linkedin_jobs.json"
        print(f"Uploading {local_path} to s3://{bucket_name}/{s3_key}...")
        s3.upload_file(local_path, bucket_name, s3_key)
        print(f"Upload completed: s3://{bucket_name}/{s3_key}")

    except ClientError as e:
        print(f"Failed to upload to S3: {e}")

upload_to_s3()
