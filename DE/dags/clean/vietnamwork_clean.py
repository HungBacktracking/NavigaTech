import os
import re
import io
import json
from datetime import datetime, timedelta

import boto3
from dotenv import load_dotenv

# Load environment variables
load_dotenv("/opt/airflow/utils/.env")

# Constants
BASE64_EMPTY_IMAGE = "data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7"
BUCKET_NAME = os.getenv("AWS_S3_BUCKET")
REGION = os.getenv("AWS_REGION")
AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")

# Initialize S3 client
s3 = boto3.client(
    "s3",
    aws_access_key_id=AWS_ACCESS_KEY,
    aws_secret_access_key=AWS_SECRET_KEY,
    region_name=REGION
)


def remove_special_chars(text):
    """Remove special characters, keep letters, numbers, spaces."""
    return re.sub(r"[^a-zA-Z0-9À-ỹà-ỹ\s]", "", text)


def jd_to_markdown(jd_text):
    """Convert job description text to Markdown format."""
    jd_text = jd_text.replace("\\n", "\n").strip()
    sections = re.split(r'\n(?=\w)', jd_text)

    markdown_lines = []
    for section in sections:
        lines = section.strip().split('\n', 1)
        title = lines[0].strip()
        content = lines[1].strip() if len(lines) > 1 else ""

        markdown_lines.append(f"**{title}**")
        content = re.sub(r'^[\t•\-]+\s*', '- ', content, flags=re.MULTILINE)

        if content:
            markdown_lines.append(content)
        markdown_lines.append("")

    return '\n'.join(markdown_lines).strip()


def extract_job_level_from_title(title: str) -> str:
    """Dựa vào title để suy đoán cấp độ công việc."""
    if not title:
        return ""

    title = title.lower()
    patterns = [
        (r"\b(intern|thực tập)\b", "Intern"),
        (r"\b(fresher|graduate)\b", "Fresher"),
        (r"\b(junior|jr\.)\b", "Junior"),
        (r"\b(senior|sr\.)\b", "Senior"),
        (r"\b(mid|middle)\b", "Middle"),
        (r"\b(lead|leader|team lead)\b", "Lead"),
        (r"\b(manager|supervisor)\b", "Manager"),
        (r"\b(director|head)\b", "Director"),
    ]

    for pattern, level in patterns:
        if re.search(pattern, title):
            return level

    return "Unknown"


def clean_job(job):
    """Clean and normalize a single job entry."""
    job["Job Description"] = re.sub(r'\s+', ' ', remove_special_chars(job.get("Job Description", ""))).strip()
    job["Job Requirements"] = re.sub(r'\s+', ' ', remove_special_chars(job.get("Job Requirements", ""))).strip()
    job["jd"] = jd_to_markdown(job.get("jd", ""))

    # Add job level from title
    title = job.get("Title", "")
    job["job_level"] = extract_job_level_from_title(title)

    # Process expiration date
    expire_text = job.get("Expiration Date", "")
    match = re.search(r'\d+', expire_text)
    if match:
        days = int(match.group())
        expire_date = datetime.now() + timedelta(days=days)
        job["Expiration Date"] = expire_date.strftime("%Y-%m-%d")
    else:
        job["Expiration Date"] = None

    # Clean company logo
    if job.get("company_logo") == BASE64_EMPTY_IMAGE:
        job["company_logo"] = None

    return job


def main():
    now = datetime.now()
    timestamp = now.strftime("%Y%m%d")
    input_key = f"raw/vietnamworks_jobs_{timestamp}.json"
    output_key = f"clean1/vietnamworks_jobs_cleaned_{timestamp}.json"

    print(f"Downloading from s3://{BUCKET_NAME}/{input_key}...")
    input_obj = s3.get_object(Bucket=BUCKET_NAME, Key=input_key)
    jobs = json.load(input_obj['Body'])

    cleaned_jobs = [clean_job(job) for job in jobs]

    output_buffer = io.BytesIO()
    json_bytes = json.dumps(cleaned_jobs, ensure_ascii=False, indent=2).encode("utf-8")
    output_buffer.write(json_bytes)
    output_buffer.seek(0)

    print(f"Uploading cleaned data to s3://{BUCKET_NAME}/{output_key}...")
    s3.upload_fileobj(output_buffer, BUCKET_NAME, output_key)

    print(f"Cleaning and upload completed: s3://{BUCKET_NAME}/{output_key}")


if __name__ == "__main__":
    main()
