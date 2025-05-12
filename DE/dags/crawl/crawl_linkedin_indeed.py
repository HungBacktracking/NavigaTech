import os
import datetime
import pandas as pd
from jobspy import scrape_jobs
import json
import numpy as np
from concurrent.futures import ThreadPoolExecutor, as_completed
import boto3
from botocore.exceptions import ClientError
from dotenv import load_dotenv

load_dotenv("/opt/airflow/utils/.env")

keywords = [
    "Data Engineer", "Data Analyst", "Data Scientist", "Machine Learning",
    "Artificial Intelligence", "MLOps", "LLM Engineer", "NLP Engineer",
    "Software Engineer", "Backend Developer", "Frontend Developer",
    "Full Stack Developer", "DevOps", "Cloud Engineer", "SRE",
    "Platform Engineer", "Security Engineer", "Big Data Engineer"
]

country = "Vietnam"
MAX_THREADS = 5

def scrape_keyword(keyword):
    try:
        jobs = scrape_jobs(
            site_name=["linkedin", "indeed"],
            search_term=keyword,
            location="Vietnam",
            country_indeed=country,
            results_wanted=5000,
            linkedin_fetch_description=True,
            verbose=0
        )
        if not jobs.empty:
            jobs["search_keyword"] = keyword
        return jobs
    except Exception as e:
        print(f"[Error] Keyword '{keyword}': {e}")
        return pd.DataFrame()

def scrape_all_keywords(keywords):
    all_jobs = []
    with ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
        futures = {executor.submit(scrape_keyword, kw): kw for kw in keywords}
        for future in as_completed(futures):
            kw = futures[future]
            try:
                df = future.result()
                if not df.empty:
                    all_jobs.append(df)
            except Exception as e:
                print(f"Error processing '{kw}': {e}")
    return pd.concat(all_jobs, ignore_index=True) if all_jobs else pd.DataFrame()

def check_bucket_exists(s3_client, bucket_name):
    try:
        s3_client.head_bucket(Bucket=bucket_name)
        return True
    except ClientError as e:
        error_code = int(e.response['Error']['Code'])
        if error_code == 404:
            print(f"Bucket '{bucket_name}' does not exist!")
        else:
            print(f"Error checking bucket '{bucket_name}': {e}")
        return False

def upload_to_s3(file_path, bucket_name, s3_key, aws_access_key_id=None, aws_secret_access_key=None, region_name=None):
    try:
        session = boto3.session.Session(
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            region_name=region_name
        )
        s3 = session.client('s3')

        if not check_bucket_exists(s3, bucket_name):
            print(f"Upload aborted because bucket '{bucket_name}' does not exist.")
            return

        s3.upload_file(file_path, bucket_name, s3_key)
        print(f"Uploaded {file_path} to s3://{bucket_name}/{s3_key}")
    except Exception as e:
        print(f"Upload to S3 failed: {e}")

# --- MAIN ---
def main():
    all_jobs_df = scrape_all_keywords(keywords)

    if not all_jobs_df.empty:
        if 'job_url' in all_jobs_df.columns:
            all_jobs_df = all_jobs_df.drop_duplicates(subset=['job_url'], keep='first')
        else:
            url_columns = [col for col in all_jobs_df.columns if 'url' in col.lower()]
            if url_columns:
                all_jobs_df = all_jobs_df.drop_duplicates(subset=[url_columns[0]], keep='first')

        timestamp = datetime.datetime.now().strftime("%Y%m%d")
        json_output = f"/opt/airflow/data/raw/linkedin_indeed_jobs_{timestamp}.json"
        os.makedirs(os.path.dirname(json_output), exist_ok=True)
        clean_df = all_jobs_df.replace({np.nan: None, pd.NaT: None})
        jobs_json = clean_df.to_dict(orient='records')

        with open(json_output, 'w', encoding='utf-8') as f:
            json.dump(jobs_json, f, ensure_ascii=False, indent=2, default=str)

        bucket_name = os.getenv("AWS_S3_BUCKET")
        s3_key = f"raw/linkedin_indeed_jobs_{timestamp}.json"
        aws_access_key_id = os.getenv("AWS_ACCESS_KEY_ID")
        aws_secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY")
        region_name = os.getenv("AWS_REGION")

        print(f"Uploading {json_output} to s3://{bucket_name}/{s3_key}...")
        upload_to_s3(json_output, bucket_name, s3_key, aws_access_key_id, aws_secret_access_key, region_name)
    else:
        print("No data scraped, skipping JSON export and upload.")
