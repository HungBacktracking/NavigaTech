import json
import re
import os
import io
from datetime import datetime, timedelta
import boto3
from dotenv import load_dotenv

# Load environment variables (for AWS credentials and bucket name)
load_dotenv("/opt/airflow/utils/.env")

timestamp = datetime.now().strftime("%Y%m%d")

# Initialize S3 client
s3 = boto3.client(
    's3',
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    region_name=os.getenv("AWS_REGION")
)

bucket_name = os.getenv("AWS_S3_BUCKET")
input_key = f"raw/vietnamworks_jobs_{timestamp}.json"
output_key = f"clean1/vietnamworks_jobs_cleaned_{timestamp}.json"

# --- Download JSON file from S3 ---
print(f"Downloading s3://{bucket_name}/{input_key}...")
input_obj = s3.get_object(Bucket=bucket_name, Key=input_key)
jobs = json.load(input_obj['Body'])

# --- Helper functions ---
def remove_special_chars(text):
    """Remove special characters (keep letters, numbers, spaces)."""
    return re.sub(r'[^a-zA-Z0-9À-ỹà-ỹ\s]', '', text)

def jd_to_markdown(jd_raw):
    """Convert job description to simple markdown (bold + bullet points)."""
    jd = jd_raw.replace("\\n", "\n").strip()

    # Add bold section titles
    jd = re.sub(r"(Job Description)", r"\n**\1**", jd, flags=re.I)
    jd = re.sub(r"(Job Requirements)", r"\n**\1**", jd, flags=re.I)
    jd = re.sub(r"(Benefit & Perks)", r"\n**\1**", jd, flags=re.I)

    # Replace bullet symbols
    jd = re.sub(r"•\t?", "- ", jd)

    # Collapse extra newlines
    jd = re.sub(r"\n{3,}", "\n\n", jd)

    return jd.strip()

def clean_job(job):
    """Clean and normalize a single job entry."""
    desc = job.get("Job Description", "")
    reqs = job.get("Job Requirements", "")
    job["Job Description"] = re.sub(r'\s+', ' ', remove_special_chars(desc)).strip()
    job["Job Requirements"] = re.sub(r'\s+', ' ', remove_special_chars(reqs)).strip()

    # Convert JD to markdown
    job["jd"] = jd_to_markdown(job.get("jd", ""))

    # Process salary
    salary_text = job.get("Salary", "").lower()
    salary_numbers = re.findall(r'\d[\d,]*', salary_text)

    if salary_numbers:
        salaries = [int(s.replace(',', '')) for s in salary_numbers]
        if "up to" in salary_text or "tới" in salary_text:
            job["min_salary"] = None
            job["max_salary"] = salaries[0]
        elif "from" in salary_text or "từ" in salary_text:
            job["min_salary"] = salaries[0]
            job["max_salary"] = None
        elif len(salaries) == 1:
            job["min_salary"] = job["max_salary"] = salaries[0]
        else:
            job["min_salary"] = min(salaries)
            job["max_salary"] = max(salaries)
    else:
        job["min_salary"] = job["max_salary"] = None

    # Process expiration date
    expire_text = job.get("Expiration Date", "")
    match = re.search(r'(\d+)', expire_text)
    if match:
        days = int(match.group(1))
        expire_date = datetime.now() + timedelta(days=days)
        job["Expiration Date"] = expire_date.strftime("%Y-%m-%d")
    else:
        job["Expiration Date"] = None

    return job

def main():
    # --- Apply cleaning to all jobs ---
    cleaned_jobs = [clean_job(job) for job in jobs]

    # --- Write cleaned data to JSON in-memory ---
    output_buffer = io.BytesIO()
    json_bytes = json.dumps(cleaned_jobs, ensure_ascii=False, indent=2).encode('utf-8')
    output_buffer.write(json_bytes)
    output_buffer.seek(0)

    # --- Upload cleaned JSON back to S3 ---
    print(f"Uploading cleaned data to s3://{bucket_name}/{output_key}...")
    s3.upload_fileobj(output_buffer, bucket_name, output_key)

    print(f"✅ Cleaning and upload completed: s3://{bucket_name}/{output_key}")
