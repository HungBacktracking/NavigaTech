import os
import uuid
import json
import boto3
from datetime import datetime
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
from dateutil.parser import parse

load_dotenv()

# AWS config
aws_access_key = os.environ['AWS_ACCESS_KEY_ID_DE']
aws_secret_key = os.environ['AWS_SECRET_ACCESS_KEY_DE']
aws_region = os.environ.get('AWS_REGION_DE', 'ap-southeast-1')
bucket_name = os.environ['AWS_S3_BUCKET_DE']

# # PostgreSQL config
# pg_user = os.environ['PG_USER']
# pg_pass = os.environ['PG_PASS']
# pg_host = os.environ['PG_HOST']
# pg_port = os.environ.get('PG_PORT', '5432')
# pg_db = os.environ['PG_DB']

# Kết nối đến S3 và đọc file JSON
s3 = boto3.client(
    's3',
    aws_access_key_id=aws_access_key,
    aws_secret_access_key=aws_secret_key,
    region_name=aws_region
)

response = s3.get_object(Bucket=bucket_name, Key='clean2/final_20250510.json')
jobs = json.loads(response['Body'].read())

# database
DB: str = os.getenv("DB", "postgresql")
DB_USER: str = os.getenv("DB_USER")
DB_PASSWORD: str = os.getenv("DB_PASSWORD")
DB_HOST: str = os.getenv("DB_HOST")
DB_PORT: str = os.getenv("DB_PORT", "5432")
DB_ENGINE: str = os.getenv("DB_ENGINE", "postgresql")

DATABASE_URI_FORMAT: str = "{db_engine}://{user}:{password}@{host}:{port}/{database}"

DATABASE_URI: str = "{db_engine}://{user}:{password}@{host}:{port}/{database}".format(
    db_engine=DB_ENGINE,
    user=DB_USER,
    password=DB_PASSWORD,
    host=DB_HOST,
    port=DB_PORT,
    database="local"
)

# Kết nối đến PostgreSQL
engine = create_engine(f'{DATABASE_URI}')



with engine.connect() as conn:
    for job in jobs:
        job_id = str(uuid.uuid4())
        now = datetime.utcnow()

        created_at = job.get('created_at') or now
        updated_at = job.get('updated_at') or now
        deleted_at = job.get('deleted_at') or None

        # Parse date_posted nếu có
        raw_date = job.get("date_posted")
        try:
            date_posted = parse(raw_date).date() if raw_date else None
        except Exception:
            date_posted = None

        # Gán mặc định cho các cột NOT NULL nếu thiếu
        job_url = job.get("job_url") or ""
        logo_url = job.get("company_logo") or ""
        job_name = job.get("title") or "N/A"
        company_name = job.get("company") or "N/A"

        # Xác định from_site từ job_url
        from_site = None
        job_url_lower = job_url.lower()
        if "linkedin" in job_url_lower:
            from_site = "linkedin"
        elif "indeed" in job_url_lower:
            from_site = "indeed"
        elif "vietnamworks" in job_url_lower:
            from_site = "vietnamworks"

        stmt = text("""
            INSERT INTO job (
                id, job_url, logo_url, job_name, job_level, job_type, from_site,
                company_name, company_type, company_address, company_description,
                skills, location, date_posted, job_description, job_requirement,
                benefit, created_at, updated_at, deleted_at
            ) VALUES (
                :id, :job_url, :logo_url, :job_name, :job_level, :job_type, :from_site,
                :company_name, :company_type, :company_address, :company_description,
                :skills, :location, :date_posted, :job_description, :job_requirement,
                :benefit, :created_at, :updated_at, :deleted_at
            )
            ON CONFLICT (id) DO NOTHING
        """)

        params = {
            "id": job_id,
            "job_url": job_url,
            "logo_url": logo_url,
            "job_name": job_name,
            "job_level": job.get("job_level"),
            "job_type": job.get("job_type"),
            "from_site": from_site,
            "company_name": company_name,
            "company_type": job.get("job_type"),
            "company_address": job.get("company_address"),
            "company_description": job.get("company_description"),
            "skills": job.get("skills"),
            "location": job.get("location"),
            "date_posted": date_posted,
            "job_description": job.get("job_description"),
            "job_requirement": job.get("qualifications & skills"),
            "benefit": job.get("benefit"),
            "created_at": created_at,
            "updated_at": updated_at,
            "deleted_at": deleted_at
        }

        try:
            with conn.begin():
                conn.execute(stmt, params)
        except Exception as e:
            print(f"❌ Insert lỗi dòng job_id={job_id}: {e}")

print("✅ Hoàn tất insert tất cả job.")