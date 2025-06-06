import os

import boto3
from botocore.exceptions import ClientError
from dotenv import load_dotenv

KEYWORDS = [
    # Programming Languages
    "programming language",
    "C/C++",
    "Python",
    "Java",

    # Web Development
    "web development",
    "frontend development",
    "backend development",

    # Mobile Development
    "mobile development",

    # Data Science & Analytics
    "data analysis",
    "statistics for data science",

    # Machine Learning & AI
    "machine learning with python",
    "deep learning",
    "tensorflow",
    "computer vision",
    "AI",
    "LLM",
    "Agent",

    # Cloud Computing & DevOps
    "aws cloud",
    "docker",
    "kubernetes",

    # Cybersecurity
    "cybersecurity fundamentals",
    "ethical hacking",
    "network security",

    # Databases & Big Data
    "sql",
    "big data",

    # Software Architecture & Practices
    "software architecture",
    "design patterns",
    "test-driven development",
    "agile and scrum",

    # Management & Analysis
    "it project management",

    # Emerging Technologies
    "iot development",
    "blockchain development",
    "robotics engineering",
]


# load_dotenv()

# def upload_to_s3():
#     try:
#         s3 = boto3.client(
#             's3',
#             aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
#             aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
#             region_name=os.getenv("AWS_REGION")
#         )
#
#         bucket_name = os.getenv("AWS_S3_BUCKET")
#         s3_key = f"data/linkedin_jobs.json"
#
#         local_path = "linkedin_jobs.json"
#         print(f"Uploading {local_path} to s3://{bucket_name}/{s3_key}...")
#         s3.upload_file(local_path, bucket_name, s3_key)
#         print(f"Upload completed: s3://{bucket_name}/{s3_key}")
#
#     except ClientError as e:
#         print(f"Failed to upload to S3: {e}")
#
# upload_to_s3()
