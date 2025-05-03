import json
import re
import os
from datetime import datetime, timedelta


timestamp = datetime.now().strftime("%Y%m%d")
# Đọc danh sách các job từ file JSON
with open(f"/opt/airflow/data/raw/vietnamworks_jobs_{timestamp}.json", "r", encoding="utf-8") as f:
    jobs = json.load(f)

# Hàm loại bỏ ký tự đặc biệt (chỉ giữ lại chữ, số và dấu cách)
def remove_special_chars(text):
    # Giữ lại chữ cái, số và khoảng trắng
    return re.sub(r'[^a-zA-Z0-9À-ỹà-ỹ\s]', '', text)

# Hàm xử lý từng job
def clean_job(job):
    # Làm sạch văn bản
    desc = job.get("Mô tả công việc", "")
    reqs = job.get("Yêu cầu công việc", "")
    jd = job.get("jd", "")

    # Bỏ ký tự đặc biệt và chuẩn hóa khoảng trắng
    job["Mô tả công việc"] = re.sub(r'\s+', ' ', remove_special_chars(desc)).strip()
    job["Yêu cầu công việc"] = re.sub(r'\s+', ' ', remove_special_chars(reqs)).strip()
    job["jd"] = re.sub(r'\s+', ' ', remove_special_chars(jd)).strip()

    # Xử lý lương
    salary_text = job.get("Lương", "").lower()
    salary_numbers = re.findall(r'\d[\d,]*', salary_text)

    if salary_numbers:
        salaries = [int(s.replace(',', '')) for s in salary_numbers]

        if "tới" in salary_text or "up to" in salary_text:
            job["min_salary"] = None
            job["max_salary"] = salaries[0]
        elif "từ" in salary_text or "from" in salary_text:
            job["min_salary"] = salaries[0]
            job["max_salary"] = None
        elif len(salaries) == 1:
            job["min_salary"] = job["max_salary"] = salaries[0]
        else:
            job["min_salary"] = min(salaries)
            job["max_salary"] = max(salaries)
    else:
        job["min_salary"] = job["max_salary"] = None

    # Xử lý ngày hết hạn
    expire_text = job.get("Ngày hết hạn", "")
    match = re.search(r'(\d+)', expire_text)
    if match:
        days = int(match.group(1))
        expire_date = datetime.now() + timedelta(days=days)
        job["Ngày hết hạn"] = expire_date.strftime("%Y-%m-%d")
    else:
        job["Ngày hết hạn"] = None

    return job

# Áp dụng xử lý cho toàn bộ danh sách
cleaned_jobs = [clean_job(job) for job in jobs]

output_path = f"/opt/airflow/data/clean1/vietnamworks_jobs_cleaned_{timestamp}.json"
os.makedirs(os.path.dirname(output_path), exist_ok=True)
# Ghi lại danh sách đã clean vào file mới
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(cleaned_jobs, f, ensure_ascii=False, indent=2)
