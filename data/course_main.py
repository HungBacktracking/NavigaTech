import os
import json
from datetime import datetime

import boto3
from botocore.exceptions import ClientError
from dotenv import load_dotenv
import time
from typing import Dict, Any, List
import google.generativeai as genai

load_dotenv()

# Gemini API tokens (rotate to avoid rate limiting)
TOKENS: List[str] = [
    os.environ["GEMINI_TOKEN_1"],
    os.environ["GEMINI_TOKEN_2"],
    os.environ["GEMINI_TOKEN_3"],
    os.environ["GEMINI_TOKEN_4"],
    os.environ["GEMINI_TOKEN_5"],
    os.environ["GEMINI_TOKEN_6"],
    os.environ["GEMINI_TOKEN_7"],
    os.environ["GEMINI_TOKEN_8"],
    os.environ["GEMINI_TOKEN_9"],
    os.environ["GEMINI_TOKEN_10"]
]

# Retry settings
MAX_RETRIES = 10
RETRY_DELAY_SECONDS = 5


# Configure initial Gemini client
token_index = 0
genai.configure(api_key=TOKENS[token_index])
ge_model = genai.GenerativeModel("gemini-2.0-flash")


def upload_to_s3():
    try:
        s3 = boto3.client(
            's3',
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
            region_name=os.getenv("AWS_REGION")
        )

        bucket_name = os.getenv("AWS_S3_BUCKET")
        s3_key = f"data/course_data.json"

        local_path = "course_data.json"
        print(f"Uploading {local_path} to s3://{bucket_name}/{s3_key}...")
        s3.upload_file(local_path, bucket_name, s3_key)
        print(f"Upload completed: s3://{bucket_name}/{s3_key}")

    except ClientError as e:
        print(f"Failed to upload to S3: {e}")


def is_valid(item):
    description = item.get("description")
    competencies = item.get("competencies")

    if competencies is None or description is None or description.strip() == "":
        return False

    return True


def remove_invalid():
    with open('course_data.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    filtered = [item for item in data if is_valid(item)]

    with open('course_data.json', 'w', encoding='utf-8') as f:
        json.dump(filtered, f, ensure_ascii=False, indent=4)

    print(f"Removed invalid courses. Kept {len(filtered)}/{len(data)} items.")


remove_invalid()
upload_to_s3()