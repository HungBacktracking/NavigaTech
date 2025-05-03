import json
import os
from datetime import datetime

FIELDS_TO_KEEP = [
    "id", "title", "location", "job_type", "job_level", "salary",
    "min_salary", "max_salary", "date_posted", "job_url",
    "company_logo", "company", "company_industry", "company_addresses",
    "company_description", "skills", "description",
    "qualifications & skills", "benefits", "responsibilities", "search_keyword"
]


timestamp = datetime.now().strftime("%Y%m%d")
OUTPUT_DIR = "/opt/airflow/data/clean2"
VIETNAMWORKS_FILE = f"/opt/airflow/data/clean1/vietnamworks_jobs_cleaned_{timestamp}.json"
LINKEDIN_INDEED_FILE = f"/opt/airflow/data/clean1/linkedin_indeed_jobs_cleaned_{timestamp}.json"
FINAL_OUTPUT_FILE = os.path.join(OUTPUT_DIR, f"final_{timestamp}.json")

def normalize_job(job):
    """Chuyển dữ liệu từ VietnamWorks hoặc Indeed/LinkedIn về chung 1 chuẩn."""
    if "Tiêu đề" in job:  # VietnamWorks dạng
        normalized = {
            "id": job.get("id", None),
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
            "min_salary": job.get("min_salary", None),
            "max_salary": job.get("max_salary", None),
            # Các field VietnamWorks không có thì để None
            "job_type": None,
            "job_level": None,
            "company_logo": None,
            "company_industry": None,
            "company_addresses": None,
            "company_description": "",
            "skills": None,
            "benefits": "",
            "search_keyword": job.get("Từ khóa", ""),
            "end_date": job.get("Ngày hết hạn", "")
        }
    else:  # LinkedIn hoặc Indeed
        normalized = {
            "id": job.get("id", None),
            "title": job.get("title", ""),
            "job_url": job.get("job_url", ""),
            "company": job.get("company", ""),
            "company_url": job.get("company_url", ""),
            "salary": job.get("salary", ""),
            "location": job.get("location", ""),
            "date_posted": job.get("date_posted", None),
            "description": job.get("description", ""),
            "responsibilities": job.get("responsibilities", ""),
            "qualifications & skills": job.get("qualifications & skills", ""),
            "min_salary": job.get("min_salary", None),
            "max_salary": job.get("max_salary", None),
            "job_type": job.get("job_type", None),
            "job_level": job.get("job_level", None),
            "company_logo": job.get("company_logo", None),
            "company_industry": job.get("company_industry", None),
            "company_addresses": job.get("company_addresses", None),
            "company_description": job.get("company_description", ""),
            "skills": job.get("skills", None),
            "benefits": job.get("benefits", ""),
            "search_keyword": job.get("search_keyword", ""),
            "end_date": None
        }

    # Chỉ giữ lại những trường cần thiết
    return {field: normalized.get(field, None) for field in FIELDS_TO_KEEP}


def load_jobs(file_path):
    """Đọc file JSON."""
    if not os.path.exists(file_path):
        print(f"⚠️ Warning: {file_path} không tồn tại. Bỏ qua.")
        return []
    
    with open(file_path, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
            if isinstance(data, dict):
                data = [data]
            return data
        except json.JSONDecodeError:
            print(f"❌ Error: Không thể đọc file {file_path}")
            return []


def save_jobs(jobs, output_path):
    """Ghi danh sách jobs vào file JSON."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(jobs, f, ensure_ascii=False, indent=2)
    print(f"✅ Saved {len(jobs)} jobs to {output_path}")


def main():
    vietnamworks_jobs = load_jobs(VIETNAMWORKS_FILE)
    linkedin_indeed_jobs = load_jobs(LINKEDIN_INDEED_FILE)

    all_jobs = vietnamworks_jobs + linkedin_indeed_jobs
    normalized_jobs = [normalize_job(job) for job in all_jobs]

    save_jobs(normalized_jobs, FINAL_OUTPUT_FILE)


if __name__ == "__main__":
    main()
