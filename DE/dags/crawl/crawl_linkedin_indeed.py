import os
import json
import datetime
import pandas as pd
import numpy as np
from dotenv import load_dotenv
from jobspy import scrape_jobs
from concurrent.futures import ThreadPoolExecutor, as_completed
import boto3
from botocore.exceptions import ClientError

# Load environment variables
load_dotenv("/opt/airflow/utils/.env")

# --- Constants ---
KEYWORDS = [
    "Data Engineer"
]
COUNTRY = "Vietnam"
MAX_THREADS = 5
BUCKET_NAME = os.getenv("AWS_S3_BUCKET")
AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_REGION = os.getenv("AWS_REGION")


def scrape_keyword(keyword):
    try:
        jobs = scrape_jobs(
            site_name=["linkedin", "indeed"],
            search_term=keyword,
            location=COUNTRY,
            country_indeed=COUNTRY,
            results_wanted=5,
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
                print(f"[Error] Processing '{kw}': {e}")
    return pd.concat(all_jobs, ignore_index=True) if all_jobs else pd.DataFrame()


def check_bucket_exists(s3_client, bucket_name):
    try:
        s3_client.head_bucket(Bucket=bucket_name)
        return True
    except ClientError as e:
        if e.response['Error']['Code'] == '404':
            print(f"[Error] Bucket '{bucket_name}' does not exist.")
        else:
            print(f"[Error] Checking bucket: {e}")
        return False


def upload_to_s3(file_path, bucket_name, s3_key):
    try:
        session = boto3.session.Session(
            aws_access_key_id=AWS_ACCESS_KEY,
            aws_secret_access_key=AWS_SECRET_KEY,
            region_name=AWS_REGION
        )
        s3 = session.client('s3')

        if not check_bucket_exists(s3, bucket_name):
            print("⛔ Upload aborted: bucket not found.")
            return

        s3.upload_file(file_path, bucket_name, s3_key)
        print(f"✅ Uploaded: s3://{bucket_name}/{s3_key}")
    except Exception as e:
        print(f"[Error] Upload failed: {e}")


def save_jobs_to_json(df, output_path):
    clean_df = df.replace({np.nan: None, pd.NaT: None})
    jobs_json = clean_df.to_dict(orient="records")

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(jobs_json, f, ensure_ascii=False, indent=2, default=str)


# --- MAIN ---
def main():
    all_jobs_df = scrape_all_keywords(KEYWORDS)

    if all_jobs_df.empty:
        print("⚠️ No data scraped. Skipping export and upload.")
        return

    # Drop duplicate job URLs
    if 'job_url' in all_jobs_df.columns:
        all_jobs_df = all_jobs_df.drop_duplicates(subset=['job_url'], keep='first')
    else:
        url_cols = [col for col in all_jobs_df.columns if 'url' in col.lower()]
        if url_cols:
            all_jobs_df = all_jobs_df.drop_duplicates(subset=[url_cols[0]], keep='first')

    # Export to JSON
    timestamp = datetime.datetime.now().strftime("%Y%m%d")
    local_path = f"/opt/airflow/data/raw/linkedin_indeed_jobs_{timestamp}.json"
    s3_key = f"raw/linkedin_indeed_jobs_{timestamp}.json"

    save_jobs_to_json(all_jobs_df, local_path)
    print(f"📁 Saved local file: {local_path}")

    # Upload to S3
    print(f"⬆️ Uploading to S3...")
    upload_to_s3(local_path, BUCKET_NAME, s3_key)


if __name__ == "__main__":
    main()
