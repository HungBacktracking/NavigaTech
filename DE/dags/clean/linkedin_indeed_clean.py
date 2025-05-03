import time
import pandas as pd
import numpy as np
import re
from tqdm import tqdm
import google.generativeai as genai
import json
import os
from dotenv import load_dotenv
import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

# Load biến môi trường
load_dotenv("/opt/airflow/utils/.env")

TOKENS = [
    os.environ["GEMINI_TOKEN_1"],
    os.environ["GEMINI_TOKEN_2"],
    os.environ["GEMINI_TOKEN_3"],
    os.environ["GEMINI_TOKEN_4"],
    os.environ["GEMINI_TOKEN_5"],
]

token_lock = threading.Lock()
current_token_idx = 0

genai.configure(api_key=TOKENS[current_token_idx])
ge_model = genai.GenerativeModel("gemini-2.0-flash")

MAX_RETRIES = 5
RETRY_DELAY = 10
RETRY_LENGTHS = [1.0, 0.9, 0.75, 0.6, 0.5]

def configure_genai_token(index):
    genai.configure(api_key=TOKENS[index])
    global ge_model
    ge_model = genai.GenerativeModel("gemini-2.0-flash")
    print(f"[Token] Đã đổi sang token {index + 1}")

def job_parser(jd_text):
    gemini_input = f"""
    You are an expert in job description analysis. Your task is to extract structured information from unstructured job descriptions.
    Given the job description below, return the following fields in **valid JSON format**:

    1. **job_level**
    2. **qualifications & skills**
    3. **responsibilities**
    4. **benefits**
    5. **salary**
    6. **min_salary**
    7. **max_salary**

    IMPORTANT RULES:
    - Only extract real salary numbers.
    - Ignore bonus, 13th month salary if not actual salary amount.
    - If no real salary, set salary as "", min_salary and max_salary as null.
    - qualifications & skills, responsibilities, and benefits must be a **single-line string**, no bullet points, no newlines.

    Output JSON format:

    ```json
    {{
        "job_level": "<string>",
        "qualifications & skills": "<string>",
        "responsibilities": "<string>",
        "benefits": "<string>",
        "salary": "<string>",
        "min_salary": <number|null>,
        "max_salary": <number|null>
    }}
    ```

    Now parse this description:
    {jd_text}

    Return JSON only.
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
    return json.loads(cleaned)

def robust_job_parser(jd_text):
    global current_token_idx

    while current_token_idx < len(TOKENS):
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
                    print(f"[Retry {attempt + 1}] Input có thể quá dài. Thử rút ngắn (tỷ lệ={ratio:.2f})...")
                    time.sleep(1)
                else:
                    print(f"[Error] Không phải lỗi quota: {e}")
                    break

        with token_lock:
            current_token_idx += 1
            if current_token_idx < len(TOKENS):
                configure_genai_token(current_token_idx)
                time.sleep(2)
            else:
                print("[❌] Đã hết token.")
                break

    return None

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

def enrich_row_wrapper(index, row_dict):
    row = pd.Series(row_dict)
    if not row['description'] or pd.isna(row['description']):
        return index, row_dict

    parsed = robust_job_parser(row['description'])
    if parsed:
        row['job_level'] = parsed.get("job_level", row.get("job_level", ""))
        row['salary'] = parsed.get("salary", row.get("salary", ""))
        row['qualifications & skills'] = parsed.get("qualifications & skills", "")
        row['responsibilities'] = parsed.get("responsibilities", "")
        row['benefits'] = parsed.get("benefits", "")
        row["min_salary"] = parsed.get("min_salary")
        row["max_salary"] = parsed.get("max_salary")

        if row["min_salary"] is None or row["max_salary"] is None:
            min_sal, max_sal = extract_salary_range(row["salary"])
            row["min_salary"] = min_sal
            row["max_salary"] = max_sal

    return index, row.where(pd.notnull(row), None).to_dict()

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

# Main
timestamp = datetime.datetime.now().strftime("%Y%m%d")
input_path = f"/opt/airflow/data/raw/linkedin_indeed_jobs_{timestamp}.json"
output_path_cleaned = f"/opt/airflow/data/clean1/linkedin_indeed_jobs_cleaned_{timestamp}.json"
os.makedirs(os.path.dirname(output_path_cleaned), exist_ok=True)

df = process_json_to_df(input_path)

# Threading
results = [None] * len(df)
max_workers = min(2, len(df))  # điều chỉnh theo tài nguyên và số token
with ThreadPoolExecutor(max_workers=max_workers) as executor:
    futures = [executor.submit(enrich_row_wrapper, idx, row.to_dict()) for idx, (_, row) in enumerate(df.iterrows())]
    for future in tqdm(as_completed(futures), total=len(df)):
        idx, enriched = future.result()
        results[idx] = enriched

# Ghi ra file
with open(output_path_cleaned, "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)
