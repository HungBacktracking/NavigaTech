import time
import pandas as pd
import numpy as np
import re
from tqdm import tqdm
import google.generativeai as genai
import json
import os
from dotenv import load_dotenv
import boto3
from io import StringIO, BytesIO
import datetime

# Load biến môi trường
load_dotenv("/opt/airflow/utils/.env")

# Lấy thông tin từ .env
AWS_ACCESS_KEY_ID = os.environ["AWS_ACCESS_KEY_ID"]
AWS_SECRET_ACCESS_KEY = os.environ["AWS_SECRET_ACCESS_KEY"]
AWS_BUCKET_NAME = os.environ["AWS_S3_BUCKET"]
AWS_REGION = os.environ.get("AWS_REGION", "ap-southeast-1") 

# Khởi tạo client S3
s3_client = boto3.client(
    "s3",
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=AWS_REGION
)

# Danh sách các token Gemini
TOKENS = [
    os.environ["GEMINI_TOKEN_1"],
    os.environ["GEMINI_TOKEN_2"],
    os.environ["GEMINI_TOKEN_3"],
    os.environ["GEMINI_TOKEN_4"],
    os.environ["GEMINI_TOKEN_5"],
    os.environ["GEMINI_TOKEN_6"],
    os.environ["GEMINI_TOKEN_7"],
    os.environ["GEMINI_TOKEN_8"]
]

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
    """Gửi yêu cầu phân tích mô tả công việc."""
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
    job_parse = json.loads(cleaned)

    return job_parse

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

def process_json_from_s3(s3_key):
    response = s3_client.get_object(Bucket=AWS_BUCKET_NAME, Key=s3_key)
    content = response['Body'].read().decode('utf-8')
    data = json.loads(content)
    jobs = data if isinstance(data, list) else [data]
    for job in jobs:
        job['description'] = clean_text(job.get('description', ''))
        job['company_description'] = clean_text(job.get('company_description', ''))
    return pd.DataFrame(jobs)

def write_json_to_s3(data_list, s3_key):
    json_str = json.dumps(data_list, ensure_ascii=False, indent=2)
    s3_client.put_object(Body=json_str.encode('utf-8'), Bucket=AWS_BUCKET_NAME, Key=s3_key)
    print(f"Đã lưu {len(data_list)} job lên S3 tại '{s3_key}'")


def main():
    timestamp = datetime.datetime.now().strftime("%Y%m%d")
    input_s3_key = f"raw/linkedin_indeed_jobs_{timestamp}.json"
    output_s3_key = f"clean1/linkedin_indeed_jobs_cleaned_{timestamp}.json"

    # Đọc từ S3
    df = process_json_from_s3(input_s3_key)
    print(f"Đã load {len(df)} job từ S3")

    # Enrich
    result_data = []
    for idx, (_, row) in enumerate(tqdm(df.iterrows(), total=len(df))):
        row = enrich_row(row)
        print(f"[DONE] Đã xử lý job: {idx + 1}/{len(df)}")
        row_dict = row.where(pd.notnull(row), None).to_dict()
        result_data.append(row_dict)

    # Ghi lên S3
    write_json_to_s3(result_data, output_s3_key)



# timestamp = datetime.datetime.now().strftime("%Y%m%d")
# # ========== MAIN ==========
# input_s3_key = f"raw/linkedin_indeed_jobs_{timestamp}.json"
# output_s3_key = f"clean1/linkedin_indeed_jobs_cleaned_{timestamp}.json"

# import logging

# logger = logging.getLogger(__name__)
# logger.setLevel(logging.INFO)

# # Đọc từ S3
# df = process_json_from_s3(input_s3_key)
# print(f"Đã load {len(df)} job từ S3")
# # Enrich
# result_data = []
# for idx, (_, row) in enumerate(tqdm(df.iterrows(), total=len(df))):
#     row = enrich_row(row)
#     logger.info(f"[DONE] Đã xử lý job: {idx + 1}/{len(df)}")
#     row_dict = row.where(pd.notnull(row), None).to_dict()
#     result_data.append(row_dict)

# # Ghi lên S3
# write_json_to_s3(result_data, output_s3_key)









# import time
# import pandas as pd
# import numpy as np
# import re
# from tqdm import tqdm
# import google.generativeai as genai
# import json
# import os
# from dotenv import load_dotenv
# import boto3
# from concurrent.futures import ThreadPoolExecutor, as_completed
# import datetime
# import threading
# import json
# import os
# import logging
# print("🔧 Bắt đầu chạy script")
# logger = logging.getLogger(__name__)
# logger.info("🔧 Script bắt đầu chạy")

# output_file_path = "/opt/airflow/data/clean1/jobs_cleaned.json"  # hoặc đường dẫn file trên Airflow Worker
# write_lock = threading.Lock()


# # Load biến môi trường
# load_dotenv("/opt/airflow/utils/.env")

# # Lấy thông tin từ .env
# AWS_ACCESS_KEY_ID = os.environ["AWS_ACCESS_KEY_ID"]
# AWS_SECRET_ACCESS_KEY = os.environ["AWS_SECRET_ACCESS_KEY"]
# AWS_BUCKET_NAME = os.environ["AWS_S3_BUCKET"]
# AWS_REGION = os.environ.get("AWS_REGION", "ap-southeast-1")

# # Khởi tạo S3 client
# s3_client = boto3.client(
#     "s3",
#     aws_access_key_id=AWS_ACCESS_KEY_ID,
#     aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
#     region_name=AWS_REGION
# )

# # Danh sách token Gemini
# TOKENS = [
#     os.environ["GEMINI_TOKEN_1"],
#     os.environ["GEMINI_TOKEN_2"],
#     os.environ["GEMINI_TOKEN_3"],
#     os.environ["GEMINI_TOKEN_4"],
#     os.environ["GEMINI_TOKEN_5"],
#     os.environ["GEMINI_TOKEN_6"],
#     os.environ["GEMINI_TOKEN_7"],
#     os.environ["GEMINI_TOKEN_8"]
# ]

# # ==== Hàm xử lý Gemini ====

# def configure_genai_token(index):
#     genai.configure(api_key=TOKENS[index])
#     model = genai.GenerativeModel("gemini-2.0-flash")
#     return model

# def job_parser(jd_text, model):
#     prompt = f"""
#     You are an expert in job description analysis. Your task is to extract structured information from unstructured job descriptions.

#     Given the job description below, return the following fields in **valid JSON format**:

#     1. **job_level**
#     2. **qualifications & skills**
#     3. **responsibilities**
#     4. **benefits**
#     5. **salary**
#     6. **min_salary**
#     7. **max_salary**

#     IMPORTANT RULES:
#     - Only extract real salary numbers.
#     - Ignore bonus, 13th month salary if not actual salary amount.
#     - If no real salary, set salary as "", min_salary and max_salary as null.
#     - qualifications & skills, responsibilities, and benefits must be a **single-line string**, no bullet points, no newlines.

#     Output JSON format:

#     ```json
#     {{
#         "job_level": "<string>",
#         "qualifications & skills": "<string>",
#         "responsibilities": "<string>",
#         "benefits": "<string>",
#         "salary": "<string>",
#         "min_salary": <number|null>,
#         "max_salary": <number|null>
#     }}
#     ```

#     Now parse this description:
#     {jd_text}

#     Return JSON only.
#     """

#     res = model.generate_content(
#         prompt,
#         generation_config={
#             "temperature": 0.2,
#             "top_k": 2,
#             "top_p": 0.9,
#             "max_output_tokens": 2000,
#         },
#     )

#     if not res.candidates or not res.candidates[0].content.parts:
#         raise ValueError("Gemini không trả lại nội dung.")

#     cleaned = res.text.replace("```json", "").replace("```", "").strip()
#     return json.loads(cleaned)

# def robust_job_parser(jd_text, model):
#     RETRY_LENGTHS = [1.0, 0.9, 0.75, 0.6, 0.5]
#     for attempt, ratio in enumerate(RETRY_LENGTHS):
#         try:
#             shortened_text = jd_text[:int(len(jd_text) * ratio)]
#             return job_parser(shortened_text, model)
#         except Exception as e:
#             if "429" in str(e):
#                 print(f"[Quota Retry {attempt+1}] Quota exceeded. Đợi 10s...")
#                 time.sleep(10)
#             elif "Gemini không trả lại nội dung" in str(e) or "response to contain a valid `Part`" in str(e):
#                 print(f"[Retry {attempt+1}] Có thể input quá dài, thử rút ngắn ({ratio:.2f})...")
#                 time.sleep(1)
#             else:
#                 print(f"[Error] Không phải lỗi quota: {e}")
#                 break
#     return None

# def extract_salary_range(salary_str):
#     if not salary_str:
#         return None, None
#     numbers = re.findall(r'(\d[\d,]*)', salary_str)
#     if len(numbers) == 1:
#         val = int(numbers[0].replace(",", ""))
#         return val, val
#     elif len(numbers) >= 2:
#         min_val = int(numbers[0].replace(",", ""))
#         max_val = int(numbers[1].replace(",", ""))
#         return min_val, max_val
#     return None, None

# def clean_text(text):
#     if not text:
#         return ""
#     allowed = r"+\-@.,:$/"
#     text = re.sub(rf"//([{allowed}])", r"\1", text)
#     text = re.sub(r"//+", " ", text)
#     text = text.replace("\\", "")
#     text = re.sub(rf"[^\w\sÀ-ỹ{allowed}]", " ", text, flags=re.UNICODE)
#     text = re.sub(r"\s+", " ", text)
#     return text.strip()

# def enrich_row(row, model):
#     if not row['description'] or pd.isna(row['description']):
#         return row
#     parsed = robust_job_parser(row['description'], model)
#     if parsed:
#         if not row.get('job_level') or pd.isna(row['job_level']) or row['job_level'] == "":
#             row['job_level'] = parsed.get("job_level", "")
#         if not row.get('salary') or pd.isna(row['salary']) or row['salary'] == "":
#             row['salary'] = parsed.get("salary", "")
#         row['qualifications & skills'] = parsed.get("qualifications & skills", "")
#         row['responsibilities'] = parsed.get("responsibilities", "")
#         row['benefits'] = parsed.get("benefits", "")
#         salary_str = row.get("salary", "")
#         row["min_salary"] = parsed.get("min_salary")
#         row["max_salary"] = parsed.get("max_salary")
#         if row["min_salary"] is None or row["max_salary"] is None:
#             min_sal, max_sal = extract_salary_range(salary_str)
#             row["min_salary"] = min_sal
#             row["max_salary"] = max_sal
#     return row

# def process_json_from_s3(s3_key):
#     obj = s3_client.get_object(Bucket=AWS_BUCKET_NAME, Key=s3_key)
#     content = obj['Body'].read().decode('utf-8')
#     data = json.loads(content)
#     jobs = data if isinstance(data, list) else [data]
#     # for job in jobs:
#     #     job['description'] = clean_text(job.get('description', ''))
#     #     job['company_description'] = clean_text(job.get('company_description', ''))
#     return pd.DataFrame(jobs)



# def write_json_to_s3(data_list, s3_key):
#     json_str = json.dumps(data_list, ensure_ascii=False, indent=2)
#     s3_client.put_object(Body=json_str.encode('utf-8'), Bucket=AWS_BUCKET_NAME, Key=s3_key)
#     print(f"✅ Đã lưu {len(data_list)} job lên S3 tại '{s3_key}'")




# # === WORKER function cho thread ===
# def worker(row_token_pair):
#     row, token_index = row_token_pair
#     model = configure_genai_token(token_index)
#     return enrich_row(row, model)


# # # === MAIN ===
# # timestamp = datetime.datetime.now().strftime("%Y%m%d")
# # input_s3_key = f"raw/linkedin_indeed_jobs_{timestamp}.json"
# # output_s3_key = f"clean1/linkedin_indeed_jobs_cleaned_{timestamp}.json"


# # df = process_json_from_s3(input_s3_key)
# # logger.info(f"📦 Đã load {len(df)} job từ S3")
# # # Gán token index theo round-robin
# # print(df)
# # row_token_pairs = [
# #     (row, idx % len(TOKENS))
# #     for idx, (_, row) in enumerate(df.iterrows())
# # ]
# # print("start")
# # result_data = []
# # logger.info("🚀 Bắt đầu xử lý bằng ThreadPoolExecutor")
# # with ThreadPoolExecutor(max_workers=len(TOKENS)) as executor:
# #     futures = [executor.submit(worker, pair) for pair in row_token_pairs]
# #     for f in tqdm(as_completed(futures), total=len(futures)):
# #         try:
# #             row_result = f.result()
# #             row_dict = row_result.where(pd.notnull(row_result), None).to_dict()
# #             result_data.append(row_dict)
# #         except Exception as e:
# #             print(f"[ERROR] Lỗi xử lý row: {e}")
# # logger.info("✅ Hoàn thành xử lý toàn bộ")
# # print(result_data)
# # write_json_to_s3(result_data, output_s3_key)



# def main():
#     timestamp = datetime.datetime.now().strftime("%Y%m%d")
#     input_s3_key = f"raw/linkedin_indeed_jobs_{timestamp}.json"
#     output_s3_key = f"clean1/linkedin_indeed_jobs_cleaned_{timestamp}.json"

#     df = process_json_from_s3(input_s3_key)
#     print(f"📦 Đã load {len(df)} job từ S3")

#     # Gán token index theo round-robin
#     row_token_pairs = [
#         (row, idx % len(TOKENS))
#         for idx, (_, row) in enumerate(df.iterrows())
#     ]

#     result_data = []
#     print("🚀 Bắt đầu xử lý bằng ThreadPoolExecutor")

#     # Dùng ThreadPoolExecutor để xử lý nhiều công việc cùng lúc
#     with ThreadPoolExecutor(max_workers=len(TOKENS)) as executor:
#         futures = [executor.submit(worker, pair) for pair in row_token_pairs]
#         for f in tqdm(as_completed(futures), total=len(futures)):
#             try:
#                 print("start")
#                 row_result = f.result()
#                 row_dict = row_result.where(pd.notnull(row_result), None).to_dict()
#                 result_data.append(row_dict)
#             except Exception as e:
#                 print(f"[ERROR] Lỗi xử lý row: {e}")

#     logger.info("✅ Hoàn thành xử lý toàn bộ")
#     write_json_to_s3(result_data, output_s3_key)
