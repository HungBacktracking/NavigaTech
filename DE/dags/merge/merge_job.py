import os
import io
import json
import logging
from datetime import datetime
from dotenv import load_dotenv
import boto3
import pandas as pd

# Load environment variables
load_dotenv("/opt/airflow/utils/.env")

# Setup logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constants
FIELDS_TO_KEEP = [
    "id", "title", "location", "job_type", "job_level", "salary",
    "min_salary", "max_salary", "date_posted", "job_url",
    "company_logo", "company", "company_industry", "company_addresses",
    "company_description", "skills", "description",
    "qualifications & skills", "benefits", "responsibilities", "search_keyword"
]

timestamp = datetime.now().strftime("%Y%m%d")

# AWS setup
bucket_name = os.getenv("AWS_S3_BUCKET")
if not bucket_name:
    raise ValueError("Missing AWS_S3_BUCKET environment variable")

s3 = boto3.client(
    's3',
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    region_name=os.getenv("AWS_REGION")
)

# S3 Keys
input_key_vietnamworks = f"clean1/vietnamworks_jobs_cleaned_{timestamp}.json"
input_key_linkedin_indeed = f"clean1/linkedin_indeed_jobs_cleaned_{timestamp}.json"
output_key = f"clean2/final_{timestamp}.json"


# --- Normalization Logic ---

def normalize_vietnamworks_job(job):
    return {
        "id": job.get("id"),
        "title": job.get("Tiêu đề", ""),
        "job_url": job.get("Link công việc", ""),
        "company": job.get("Công ty", ""),
        "company_url": job.get("Link công ty", ""),
        "salary": job.get("Lương", ""),
        "location": job.get("Địa điểm", ""),
        "date_posted": None,
        "description": job.get("jd", ""),
        "responsibilities": job.get("Mô tả công việc", ""),
        "qualifications & skills": job.get("Yêu cầu công việc", ""),
        "min_salary": job.get("min_salary"),
        "max_salary": job.get("max_salary"),
        "job_type": None,
        "job_level": None,
        "company_addresses": None,
        "benefits": "",
        "company_logo": job.get("Logo công ty", "")
    }


def normalize_linkedin_indeed_job(job):
    return {
        "id": job.get("id"),
        "title": job.get("title", ""),
        "job_url": job.get("job_url", ""),
        "company": job.get("company", ""),
        "company_url": job.get("company_url", ""),
        "salary": job.get("salary", ""),
        "location": job.get("location", ""),
        "date_posted": job.get("date_posted"),
        "description": job.get("description", ""),
        "responsibilities": job.get("responsibilities", ""),
        "qualifications & skills": job.get("qualifications & skills", ""),
        "min_salary": job.get("min_salary"),
        "max_salary": job.get("max_salary"),
        "job_type": job.get("job_type"),
        "job_level": job.get("job_level"),
        "company_addresses": job.get("company_addresses"),
        "benefits": job.get("benefits", ""),
        "company_logo": job.get("company_logo", "")
    }


def normalize_job(job):
    if "Tiêu đề" in job:
        raw = normalize_vietnamworks_job(job)
    else:
        raw = normalize_linkedin_indeed_job(job)

    return {field: raw.get(field, None) for field in FIELDS_TO_KEEP}


# --- S3 & Local Operations ---

def load_jobs_from_s3(key):
    try:
        logger.info(f"⬇Downloading s3://{bucket_name}/{key}")
        response = s3.get_object(Bucket=bucket_name, Key=key)
        content = response['Body'].read().decode('utf-8')
        data = json.loads(content)
        return data if isinstance(data, list) else [data]
    except s3.exceptions.NoSuchKey:
        logger.warning(f"s3://{bucket_name}/{key} does not exist. Skipping.")
        return []
    except json.JSONDecodeError:
        logger.error(f"Failed to decode JSON from s3://{bucket_name}/{key}")
        return []
    except Exception as e:
        logger.error(f"Failed to load s3://{bucket_name}/{key} - {e}")
        return []


def save_jobs_to_local(jobs, filepath):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    df = pd.DataFrame(jobs)
    df.to_json(filepath, orient="records", force_ascii=False, indent=2)
    logger.info(f"Saved {len(jobs)} jobs to local file {filepath}")


def upload_local_file_to_s3(local_path, key):
    logger.info(f"⬆Uploading {local_path} to s3://{bucket_name}/{key}")
    s3.upload_file(local_path, bucket_name, key)
    logger.info(f"Uploaded to s3://{bucket_name}/{key}")


# --- Main Process ---

def main():
    vietnamworks_jobs = load_jobs_from_s3(input_key_vietnamworks)
    linkedin_indeed_jobs = load_jobs_from_s3(input_key_linkedin_indeed)
    all_jobs = vietnamworks_jobs + linkedin_indeed_jobs

    if not all_jobs:
        logger.warning("No job data loaded from either source. Exiting.")
        return

    normalized_jobs = [normalize_job(job) for job in all_jobs]
    local_file_path = f"/opt/airflow/data/clean2/final_{timestamp}.json"

    save_jobs_to_local(normalized_jobs, local_file_path)
    upload_local_file_to_s3(local_file_path, output_key)

if __name__ == "__main__":
    main()
