import time
import pandas as pd
import numpy as np
import re
from tqdm import tqdm
import google.generativeai as genai
import json
import os
from dotenv import load_dotenv


load_dotenv(".env")

genai.configure(api_key=os.environ["GEMINI_TOKEN"])
ge_model = genai.GenerativeModel("gemini-2.0-flash")



def job_parser(jd_text):
    gemini_input = f"""
    You are an expert in job description analysis. Your task is to extract structured information from unstructured job descriptions.

    Given the job description below, return the following fields in **valid JSON format**:

    1. **job_level** — e.g., Internship, Entry-Level, Mid-Level, Senior, Director, etc.
    2. **qualifications & skills** — A list of required or preferred degrees, educational background, certifications, or prior experience.
    3. **responsibilities** — A list of key responsibilities and tasks mentioned in the role.
    4. **benefits** — A list of perks, learning outcomes, or benefits associated with the role (e.g., mentorship, flexibility, health insurance, skill development, 13th month salary, performance bonus, etc.).
    5. **salary** — A string or range if specified (e.g., "$50,000 - $70,000 per year"). If not mentioned, return an empty string.
    6. **min_salary** — Extract the lowest number from the `salary` field **only if it clearly represents an actual salary amount**. Do NOT include numbers related to bonuses, months, or benefits (e.g., "13th month salary" or "3 months probation"). Return as a number or null.
    7. **max_salary** — Extract the highest number from the `salary` field with the same rule: only if it clearly represents a salary. Otherwise, return null.

    **IMPORTANT RULES**
    - `min_salary` and `max_salary` must reflect real salary figures (e.g., $1,000/month or 15–20 million VND/month).
    - Ignore values like "13th month", "3-month bonus", "up to 6% performance reward" unless they explicitly define a fixed salary.
    - If no valid number is found for salary, return empty string for `salary`, and null for both `min_salary` and `max_salary`.
    - If the salary mentions only general phrases like "competitive salary", "13th month salary", "bonus", or "performance-based income" without specific numeric values, set "salary" to an empty string and both "min_salary" and "max_salary" to null.

    The output must follow this format exactly:

    ```json
    {{
        "job_level": "<string>",
        "qualifications & skills": [
            "<string>",
            ...
        ],
        "responsibilities": [
            "<string>",
            ...
        ],
        "benefits": [
            "<string>",
            ...
        ],
        "salary": "<string>",
        "min_salary": <number|null>,
        "max_salary": <number|null>
    }}
    ```

    Now parse the job description:
    {jd_text}

    Return in JSON format only.
    """


    res = ge_model.generate_content(
        gemini_input,
        generation_config={
            "temperature": 0.2,
            "top_k": 2,
            "top_p": 0.9,
            "max_output_tokens": 2000,
        },
    )

    if not res.candidates or not res.candidates[0].content.parts:
        raise ValueError("Gemini không trả lại nội dung (possibly too long or unsafe).")

    cleaned = res.text.replace("```json", "").replace("```", "").strip()
    job_parse = json.loads(cleaned)

    return job_parse


MAX_RETRIES = 5
RETRY_DELAY = 10  # giây
RETRY_LENGTHS = [1.0, 0.9, 0.75, 0.6, 0.5] 

def extract_salary_range(salary_str):
    if not salary_str:
        return None, None
    matches = re.findall(r'(\d[\d,]*)', salary_str)
    if len(matches) == 1:
        value = int(matches[0].replace(",", ""))
        return value, value
    elif len(matches) >= 2:
        min_val = int(matches[0].replace(",", ""))
        max_val = int(matches[1].replace(",", ""))
        return min_val, max_val
    return None, None

def robust_job_parser(jd_text):
    for attempt, ratio in enumerate(RETRY_LENGTHS):
        try:
            shortened_text = jd_text[:int(len(jd_text) * ratio)]
            return job_parser(shortened_text)
        except Exception as e:
            error_msg = str(e)
            if "429" in error_msg:
                print(f"[Quota Retry {attempt + 1}] Quota exceeded. Waiting {RETRY_DELAY} seconds...")
                time.sleep(RETRY_DELAY)
            elif "Gemini không trả lại nội dung" in error_msg or "response to contain a valid `Part`" in error_msg:
                print(f"[Retry {attempt + 1}] Có thể input quá dài. Thử rút ngắn (tỷ lệ={ratio:.2f})...")
                time.sleep(1)
            else:
                print(f"[Error] Không phải lỗi quota: {e}")
                break
    return None

def enrich_row(row):
    if not row['description'] or pd.isna(row['description']):
        return row

    parsed = robust_job_parser(row['description'])
    if parsed:
        if not row.get('job_level') or pd.isna(row['job_level']) or row['job_level'] == "":
            row['job_level'] = parsed.get("job_level", "")

        if not row.get('salary') or pd.isna(row['salary']) or row['salary'] == "":
            row['salary'] = parsed.get("salary", "")

        row['qualifications & skills'] = parsed.get("qualifications & skills", [])
        row['responsibilities'] = parsed.get("responsibilities", [])
        row['benefits'] = parsed.get("benefits", [])

        salary_str = row.get("salary", "")
        row["min_salary"] = parsed.get("min_salary")
        row["max_salary"] = parsed.get("max_salary")

        if row["min_salary"] is None or row["max_salary"] is None:
            min_sal, max_sal = extract_salary_range(salary_str)
            row["min_salary"] = min_sal
            row["max_salary"] = max_sal

    return row


input_path = "output/vietnam_jobs_20250420_201745.json"
output_path = "clean1/vietnam_jobs_cleaned.json"


os.makedirs(os.path.dirname(output_path), exist_ok=True)

# Đọc file đầu vào
def clean_text(text):
    if not text:
        return ""
    allowed_chars = r"+\-@.,:$/"
    text = re.sub(rf"//([{allowed_chars}])", r"\1", text)
    text = re.sub(r"//+", " ", text)
    text = text.replace("\\", "")
    text = re.sub(rf"[^\w\sÀ-ỹ{allowed_chars}]", " ", text, flags=re.UNICODE)
    text = re.sub(r"\s+", " ", text)
    return text.strip()

def process_json_to_df(input_file):
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    jobs = data if isinstance(data, list) else [data]
    for job in jobs:
        job['description'] = clean_text(job.get('description', ''))
        job['company_description'] = clean_text(job.get('company_description', ''))
    return pd.DataFrame(jobs)

df = process_json_to_df(input_path)

with open(output_path, "w", encoding="utf-8") as f:
    f.write("[\n")
    first = True

    for idx, (_, row) in enumerate(tqdm(df.iterrows(), total=len(df))):
        row = enrich_row(row)
        row_dict = row.where(pd.notnull(row), None).to_dict()

        if not first:
            f.write(",\n")
        else:
            first = False

        json.dump(row_dict, f, ensure_ascii=False, indent=2)

    f.write("\n]")

# Giai đoạn lọc các trường cần thiết
FIELDS_TO_KEEP = [
    "id", "title", "location", "job_type", "job_level", "salary",
    "min_salary", "max_salary", "date_posted", "job_url",
    "company_logo", "company", "company_industry", "company_addresses",
    "company_description", "skills", "description",
    "qualifications & skills", "benefits", "responsibilities"
]

input_path = "clean1/vietnam_jobs_cleaned.json"
output_path = "output2/vietnam_jobs_selected_fields.json"


os.makedirs(os.path.dirname(output_path), exist_ok=True)

def extract_selected_fields(input_file, output_file):
    with open(input_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    filtered_data = []
    for job in data:
        filtered_job = {field: job.get(field, None) for field in FIELDS_TO_KEEP}
        filtered_data.append(filtered_job)

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(filtered_data, f, ensure_ascii=False, indent=2)

    print(f"✅ Đã lưu {len(filtered_data)} job vào '{output_file}'")


extract_selected_fields(input_path, output_path)