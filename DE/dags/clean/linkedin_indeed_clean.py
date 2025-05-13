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
# from io import StringIO, BytesIO
# import datetime

# # Load biến môi trường
# load_dotenv("/opt/airflow/utils/.env")

# # Lấy thông tin từ .env
# AWS_ACCESS_KEY_ID = os.environ["AWS_ACCESS_KEY_ID"]
# AWS_SECRET_ACCESS_KEY = os.environ["AWS_SECRET_ACCESS_KEY"]
# AWS_BUCKET_NAME = os.environ["AWS_S3_BUCKET"]
# AWS_REGION = os.environ.get("AWS_REGION", "ap-southeast-1") 

# # Khởi tạo client S3
# s3_client = boto3.client(
#     "s3",
#     aws_access_key_id=AWS_ACCESS_KEY_ID,
#     aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
#     region_name=AWS_REGION
# )

# # Danh sách các token Gemini
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

# current_token_idx = 0
# genai.configure(api_key=TOKENS[current_token_idx])
# ge_model = genai.GenerativeModel("gemini-2.0-flash")

# MAX_RETRIES = 5
# RETRY_DELAY = 10
# RETRY_LENGTHS = [1.0, 0.9, 0.75, 0.6, 0.5]

# def configure_genai_token(index):
#     genai.configure(api_key=TOKENS[index])
#     global ge_model
#     ge_model = genai.GenerativeModel("gemini-2.0-flash")
#     print(f"[Token] Đã đổi sang token {index + 1}")


# def job_parser(jd_text):
#     """Gửi yêu cầu phân tích mô tả công việc."""
#     gemini_input = f"""
#     You are an expert in job description analysis. Your task is to extract structured information from unstructured job descriptions.

#     Given the job description below, return the following fields in **valid JSON format**:

#     1. **job_level**
#     2. **qualifications & skills**
#     3. **responsibilities**
#     4. **benefits**
#     5. **salary**

#     IMPORTANT RULES:
#     - Only extract real salary numbers.
#     - Ignore bonus, 13th month salary if not actual salary amount.
#     - If no real salary, set salary as "",
#     - qualifications & skills, responsibilities, and benefits must be a **single-line string**, no bullet points, no newlines.

#     Output JSON format:

#     ```json
#     {{
#         "job_level": "<string>",
#         "qualifications & skills": "<string>",
#         "responsibilities": "<string>",
#         "benefits": "<string>",
#         "salary": "<string>",
#     }}
#     ```

#     Now parse this description:
#     {jd_text}

#     Return JSON only.
#     """

#     res = ge_model.generate_content(
#         gemini_input,
#         generation_config={
#             "temperature": 0.2,
#             "top_k": 2,
#             "top_p": 0.9,
#             "max_output_tokens": 2000,
#         },
#     )

#     if not res.candidates or not res.candidates[0].content.parts:
#         raise ValueError("Gemini không trả lại nội dung (possibly too long or unsafe).")

#     cleaned = res.text.replace("```json", "").replace("```", "").strip()
#     job_parse = json.loads(cleaned)

#     return job_parse

# def robust_job_parser(jd_text):
#     global current_token_idx
#     while current_token_idx < len(TOKENS):
#         for attempt, ratio in enumerate(RETRY_LENGTHS):
#             try:
#                 shortened_text = jd_text[:int(len(jd_text) * ratio)]
#                 return job_parser(shortened_text)
#             except Exception as e:
#                 error_msg = str(e)
#                 if "429" in error_msg:
#                     print(f"[Quota Retry {attempt + 1}] Quota exceeded. Waiting {RETRY_DELAY} seconds...")
#                     time.sleep(RETRY_DELAY)
#                 elif "Gemini không trả lại nội dung" in error_msg or "response to contain a valid `Part`" in error_msg:
#                     print(f"[Retry {attempt + 1}] Input có thể quá dài. Thử rút ngắn (tỷ lệ={ratio:.2f})...")
#                     time.sleep(1)
#                 else:
#                     print(f"[Error] Không phải lỗi quota: {e}")
#                     break
#         current_token_idx += 1
#         if current_token_idx < len(TOKENS):
#             configure_genai_token(current_token_idx)
#             time.sleep(2)
#         else:
#             print("Đã hết token.")
#             break
#     return None

# def enrich_row(row):
#     if not row['description'] or pd.isna(row['description']):
#         return row
#     parsed = robust_job_parser(row['description'])
#     if parsed:
#         if not row.get('job_level') or pd.isna(row['job_level']) or row['job_level'] == "":
#             row['job_level'] = parsed.get("job_level", "")
#         if not row.get('salary') or pd.isna(row['salary']) or row['salary'] == "":
#             row['salary'] = parsed.get("salary", "")
#         row['qualifications & skills'] = parsed.get("qualifications & skills", [])
#         row['responsibilities'] = parsed.get("responsibilities", [])
#         row['benefits'] = parsed.get("benefits", [])

#     return row

# def process_json_from_s3(s3_key):
#     response = s3_client.get_object(Bucket=AWS_BUCKET_NAME, Key=s3_key)
#     content = response['Body'].read().decode('utf-8')
#     data = json.loads(content)
#     jobs = data if isinstance(data, list) else [data]
#     return pd.DataFrame(jobs)

# def write_json_to_s3(data_list, s3_key):
#     json_str = json.dumps(data_list, ensure_ascii=False, indent=2)
#     s3_client.put_object(Body=json_str.encode('utf-8'), Bucket=AWS_BUCKET_NAME, Key=s3_key)
#     print(f"Đã lưu {len(data_list)} job lên S3 tại '{s3_key}'")


# def main():
#     timestamp = datetime.datetime.now().strftime("%Y%m%d")
#     input_s3_key = f"raw/linkedin_indeed_jobs_{timestamp}.json"
#     output_s3_key = f"clean1/linkedin_indeed_jobs_cleaned_{timestamp}.json"

#     # Đọc từ S3
#     df = process_json_from_s3(input_s3_key)
#     print(f"Đã load {len(df)} job từ S3")

#     # Enrich
#     result_data = []
#     for idx, (_, row) in enumerate(tqdm(df.iterrows(), total=len(df))):
#         row = enrich_row(row)
#         print(f"[DONE] Đã xử lý job: {idx + 1}/{len(df)}")
#         row_dict = row.where(pd.notnull(row), None).to_dict()
#         result_data.append(row_dict)

#     # Ghi lên S3
#     write_json_to_s3(result_data, output_s3_key)


import os
import re
import time
import json
import datetime
from io import StringIO, BytesIO

import pandas as pd
import numpy as np
import boto3
from dotenv import load_dotenv
from tqdm import tqdm
import google.generativeai as genai

# Load environment variables
load_dotenv("/opt/airflow/utils/.env")

# AWS configuration
AWS_ACCESS_KEY_ID = os.environ["AWS_ACCESS_KEY_ID"]
AWS_SECRET_ACCESS_KEY = os.environ["AWS_SECRET_ACCESS_KEY"]
AWS_BUCKET_NAME = os.environ["AWS_S3_BUCKET"]
AWS_REGION = os.environ.get("AWS_REGION", "ap-southeast-1")

# Gemini API tokens
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

# S3 client
s3_client = boto3.client(
    "s3",
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=AWS_REGION
)

# Gemini configuration
current_token_idx = 0
genai.configure(api_key=TOKENS[current_token_idx])
ge_model = genai.GenerativeModel("gemini-2.0-flash")

# Retry settings
MAX_RETRIES = 5
RETRY_DELAY = 10
RETRY_LENGTHS = [1.0, 0.9, 0.75, 0.6, 0.5]


def configure_genai_token(index):
    """Cấu hình lại Gemini API khi đổi token."""
    genai.configure(api_key=TOKENS[index])
    global ge_model
    ge_model = genai.GenerativeModel("gemini-2.0-flash")
    print(f"Switched to token {index + 1}")



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

def parse_job_description(jd_text):
    """Gửi mô tả công việc đến Gemini và trả về kết quả phân tích."""
    prompt = f"""
    You are an expert in job description analysis. Your task is to extract structured information from unstructured job descriptions.

    Given the job description below, return the following fields in **valid JSON format**:

    1. **job_level**
    2. **qualifications & skills**
    3. **responsibilities**
    4. **benefits**
    5. **salary**

    IMPORTANT RULES:
    - Only extract real salary numbers.
    - Ignore bonus, 13th month salary if not actual salary amount.
    - If no real salary, set salary as "".
    - qualifications & skills, responsibilities, and benefits must be a **single-line string**, no bullet points, no newlines.

    Output JSON format:

    {{
        "job_level": "<string>",
        "qualifications & skills": "<string>",
        "responsibilities": "<string>",
        "benefits": "<string>",
        "salary": "<string>"
    }}

    Now parse this description:
    {clean_text(jd_text)}

    Return JSON only.
    """

    response = ge_model.generate_content(
        prompt,
        generation_config={
            "temperature": 0.2,
            "top_k": 2,
            "top_p": 0.9,
            "max_output_tokens": 2000,
        },
    )

    if not response.candidates or not response.candidates[0].content.parts:
        raise ValueError("Gemini did not return valid content.")

    raw_text = response.text.replace("```json", "").replace("```", "").strip()
    try:
        return json.loads(raw_text)
    except json.JSONDecodeError as e:
        raise ValueError(f"JSON parsing failed: {e}\nRaw Gemini output:\n{raw_text}")


def robust_parse_description(jd_text):
    """Gọi Gemini với cơ chế retry và đổi token khi gặp lỗi."""
    global current_token_idx

    while current_token_idx < len(TOKENS):
        for attempt, ratio in enumerate(RETRY_LENGTHS):
            try:
                shortened = jd_text[:int(len(jd_text) * ratio)]
                return parse_job_description(shortened)
            except Exception as e:
                error_msg = str(e)
                if "429" in error_msg:
                    print(f"Quota exceeded. Retry {attempt + 1}, waiting {RETRY_DELAY} seconds...")
                    time.sleep(RETRY_DELAY)
                elif "Gemini did not return" in error_msg or "valid `Part`" in error_msg:
                    print(f"Retry {attempt + 1}: Trimming input to {ratio:.2f} length...")
                    time.sleep(1)
                else:
                    print(f"Unexpected error: {e}")
                    break
        current_token_idx += 1
        if current_token_idx < len(TOKENS):
            configure_genai_token(current_token_idx)
            time.sleep(2)
        else:
            print("All tokens exhausted.")
            break
    return None


def enrich_job_row(row):
    """Phân tích và thêm thông tin vào một dòng dữ liệu công việc."""
    if not row.get('description') or pd.isna(row['description']):
        return row

    try:
        parsed = robust_parse_description(row['description'])
        if parsed:
            if not row.get('job_level'):
                row['job_level'] = parsed.get('job_level', "")
            if not row.get('salary'):
                row['salary'] = parsed.get('salary', "")
            row['qualifications & skills'] = parsed.get("qualifications & skills", "")
            row['responsibilities'] = parsed.get("responsibilities", "")
            row['benefits'] = parsed.get("benefits", "")
    except Exception as e:
        print(f"[SKIP] Failed to parse row due to: {e}")
    return row


def read_json_from_s3(s3_key):
    """Đọc file JSON từ S3 và trả về DataFrame."""
    response = s3_client.get_object(Bucket=AWS_BUCKET_NAME, Key=s3_key)
    content = response['Body'].read().decode('utf-8')
    data = json.loads(content)
    return pd.DataFrame(data if isinstance(data, list) else [data])


def write_json_to_s3(data_list, s3_key):
    """Ghi danh sách dict lên S3 dưới dạng JSON."""
    json_str = json.dumps(data_list, ensure_ascii=False, indent=2)
    s3_client.put_object(Body=json_str.encode('utf-8'), Bucket=AWS_BUCKET_NAME, Key=s3_key)
    print(f"Saved {len(data_list)} jobs to S3 at '{s3_key}'")


def main():
    timestamp = datetime.datetime.now().strftime("%Y%m%d")
    input_s3_key = f"raw/linkedin_indeed_jobs_{timestamp}.json"
    output_s3_key = f"clean1/linkedin_indeed_jobs_cleaned_{timestamp}.json"

    print(f"Reading jobs from S3: {input_s3_key}")
    df = read_json_from_s3(input_s3_key)

    print(f"Enriching {len(df)} job descriptions...")
    result_data = []
    for _, row in tqdm(df.iterrows(), total=len(df)):
        enriched_row = enrich_job_row(row)
        row_dict = enriched_row.where(pd.notnull(enriched_row), None).to_dict()
        result_data.append(row_dict)

    print(f"Writing enriched data to S3: {output_s3_key}")
    write_json_to_s3(result_data, output_s3_key)


if __name__ == "__main__":
    main()




