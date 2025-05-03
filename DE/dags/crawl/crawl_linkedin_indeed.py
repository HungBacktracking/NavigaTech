import os
import datetime
import time
import pandas as pd
from jobspy import scrape_jobs
import json
import numpy as np
from concurrent.futures import ThreadPoolExecutor, as_completed

# Tạo thư mục lưu dữ liệu đầu ra nếu chưa tồn tại
output_dir = "/opt/airflow/data/raw"
os.makedirs(output_dir, exist_ok=True)

# Từ khóa tìm kiếm
keywords = [
    "Data Engineer", "Data Analyst", "Data Scientist", "Machine Learning",
    "Artificial Intelligence", "MLOps", "LLM Engineer", "NLP Engineer",
    "Software Engineer", "Backend Developer", "Frontend Developer",
    "Full Stack Developer", "DevOps", "Cloud Engineer", "SRE",
    "Platform Engineer", "Security Engineer", "Big Data Engineer"
]

country = "Vietnam"
MAX_THREADS = 5  # Bạn có thể điều chỉnh tùy theo tài nguyên máy

def scrape_keyword(keyword):
    """Scrape job từ 1 keyword."""
    try:
        jobs = scrape_jobs(
            site_name=["linkedin", "indeed"],
            search_term=keyword,
            location="Vietnam",
            country_indeed=country,
            results_wanted=500,
            linkedin_fetch_description=True,
            verbose=0
        )
        if not jobs.empty:
            jobs["search_keyword"] = keyword
        return jobs
    except Exception as e:
        print(f"[Lỗi] Keyword '{keyword}': {e}")
        return pd.DataFrame()

def scrape_all_keywords(keywords):
    """Scrape đa luồng tất cả từ khóa."""
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
                print(f"[❌] Lỗi khi xử lý '{kw}': {e}")

    return pd.concat(all_jobs, ignore_index=True) if all_jobs else pd.DataFrame()

# Gọi hàm chính để scrape
all_jobs_df = scrape_all_keywords(keywords)

# Xử lý trùng lặp
if not all_jobs_df.empty:
    if 'job_url' in all_jobs_df.columns:
        all_jobs_df = all_jobs_df.drop_duplicates(subset=['job_url'], keep='first')
    else:
        url_columns = [col for col in all_jobs_df.columns if 'url' in col.lower()]
        if url_columns:
            all_jobs_df = all_jobs_df.drop_duplicates(subset=[url_columns[0]], keep='first')

# Xuất dữ liệu ra JSON
timestamp = datetime.datetime.now().strftime("%Y%m%d")
json_output = f"/opt/airflow/data/raw/linkedin_indeed_jobs_{timestamp}.json"

if not all_jobs_df.empty:
    clean_df = all_jobs_df.replace({np.nan: None, pd.NaT: None})
    jobs_json = clean_df.to_dict(orient='records')
    with open(json_output, 'w', encoding='utf-8') as f:
        json.dump(jobs_json, f, ensure_ascii=False, indent=2, default=str)
