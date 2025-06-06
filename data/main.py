import os
import json
from datetime import datetime

import boto3
from botocore.exceptions import ClientError
from dotenv import load_dotenv
import time
from typing import Dict, Any, List
import google.generativeai as genai

load_dotenv()

# Gemini API tokens (rotate to avoid rate limiting)
TOKENS: List[str] = [
    os.environ["GEMINI_TOKEN_1"],
    os.environ["GEMINI_TOKEN_2"],
    os.environ["GEMINI_TOKEN_3"],
    os.environ["GEMINI_TOKEN_4"],
    os.environ["GEMINI_TOKEN_5"],
    os.environ["GEMINI_TOKEN_6"],
    os.environ["GEMINI_TOKEN_7"],
    os.environ["GEMINI_TOKEN_8"],
    os.environ["GEMINI_TOKEN_9"],
    os.environ["GEMINI_TOKEN_10"]
]

# Retry settings
MAX_RETRIES = 10
RETRY_DELAY_SECONDS = 5

# Job type & level taxonomy
VALID_JOB_TYPES = ["Internship", "Contract", "Full-time", "Part-time", "Freelancer"]
VALID_JOB_LEVELS = ["Intern", "Entry-level", "Junior", "Mid-level", "Senior", "Leader", "Principal"]

# Configure initial Gemini client
token_index = 0
genai.configure(api_key=TOKENS[token_index])
ge_model = genai.GenerativeModel("gemini-2.0-flash")


def rotate_token():
    """
    Rotate to the next API token in a round-robin fashion.
    """
    global token_index, ge_model
    token_index = (token_index + 1) % len(TOKENS)
    genai.configure(api_key=TOKENS[token_index])
    ge_model = genai.GenerativeModel("gemini-2.0-flash")
    print(f"Rotated to Gemini token index {token_index}")


def build_llm_prompt(raw_item: Dict[str, Any]) -> str:
    prompt = f"""
        You are given a scraped job posting with these attributes in JSON format:

        {json.dumps(raw_item, ensure_ascii=False)}

        Transform it into a normalized JSON object with exactly these keys:
        - from_site (Vietnamworks or Linkedin or Indeed)
        - title 
        - company 
        - location (English)
        - date_posted (ISO format YYYY-MM-DD)
        - job_url
        - company_logo
        - job_type (one of: {', '.join(VALID_JOB_TYPES)}, classify based on description or the origin)
        - job_level (one of: {', '.join(VALID_JOB_LEVELS)}, classify based on description or the origin)
        - competencies (an object with the following subkeys, each must be a list of strings. If you cannot find any items for a subkey, return an empty list.)
            • programming_languages: Extract any explicit mentions of languages (e.g., Python, Java, C++) 
              from the title, description, or other text fields.
            • frameworks: Look for framework names (e.g., Django, Flask, React, Spring) in title, description, or anywhere in the raw data.
            • platforms: Identify cloud or deployment platforms (e.g., AWS, Azure, GCP, Heroku) or OS/platform-specific mentions in the posting.
            • tools: List any developer tools or CI/CD tools (e.g., Docker, Git, Jenkins, Kubernetes, Terraform) mentioned.
            • knowledge: Include any domain-specific knowledge topics (e.g., Algorithms, Data Structures, Networking, Security) described in the posting.
            • soft_skills: Capture interpersonal or general skills (e.g., Communication, Teamwork, Problem-solving, Leadership); look for phrases like "strong communication skills" or "team player".
            • certifications: Extract any certifications (e.g., "Certified Security Developer", "PMP", "AWS Certified Solutions Architect") mentioned explicitly.
        - description (English, markdown format suitable for frontend display)

        Rules:
        1. Convert any relative date strings like "3 days ago" or "1 month ago" into an absolute date in ISO format, assuming today is {datetime.now().strftime("%Y-%m-%d")}.
        2. job_type should be determined from the original "job_type" field; if missing or ambiguous, infer from description or set to null.
        3. job_level should be one of the valid levels; infer from "job_level", or from description context. If uncertain, set to null.
        4. Translate any non-English text (for location, description, job_type, job_level) into English.
        5. Ensure "description" is full markdown with proper line breaks and bullets if list-like and maybe headings, bold, italics if it is suitable.
        6. Preserve "job_url" and "company_logo" as-is.
        7. Output only valid JSON. Do not include any extra keys.
        8. If any field is missing or cannot be determined, set it to null (except competencies, which should be an object with empty lists if no data).

        Return only the normalized JSON. CONTAINS ONLY ENGLISH in description, translate the headings, and everything in description. 
        Do not remain null in job_type and job_level.
        IMPORTANT: Return exactly one JSON object. Do NOT wrap it in triple backticks or any markdown. The response must start with {{ and end with }} and contain no other text. DO NOT RESPONSE LIKE ```json ```.
    """
    return prompt.strip()


def call_gemini_llm(prompt: str) -> Dict[str, Any]:
    for attempt in range(MAX_RETRIES):
        try:
            response = ge_model.generate_content(
                prompt,
                generation_config={
                    "temperature": 0.0,
                    "max_output_tokens": 10000,
                },
            )
            text = response.text.strip()
            text = text.replace("`", "")
            text = text.replace("'", "")
            text = text.replace("json", "")

            # Ensure valid JSON
            normalized = json.loads(text)
            return normalized

        except json.JSONDecodeError as jde:
            print(f"JSON parse error on attempt {attempt + 1}: {jde}. Rotating token and retrying.")
            rotate_token()
            time.sleep(RETRY_DELAY_SECONDS)

        except Exception as e:
            print(f"Error calling Gemini on attempt {attempt + 1}: {e}. Rotating token and retrying.")
            rotate_token()
            time.sleep(RETRY_DELAY_SECONDS)

    # If all retries fail, raise an exception
    raise RuntimeError("Exceeded max retries when calling Gemini LLM")

def process_item(item) -> Dict[str, Any]:
    raw_dict = dict(item)

    # Build prompt for normalization
    prompt = build_llm_prompt(raw_dict)

    try:
        normalized: str = call_gemini_llm(prompt)
        print("-------------")
        print(normalized)
        print("--------------")

    except Exception as err:
        print(f"Failed to normalize item {raw_dict.get('job_url')}: {err}")
        # Optionally, return raw item or drop
        return raw_dict  # or raise DropItem()

    # Merge normalized fields back into item
    return normalized


def upload_to_s3():
    try:
        s3 = boto3.client(
            's3',
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
            region_name=os.getenv("AWS_REGION")
        )

        bucket_name = os.getenv("AWS_S3_BUCKET")
        s3_key = f"data/job_data.json"

        local_path = "job_data.json"
        print(f"Uploading {local_path} to s3://{bucket_name}/{s3_key}...")
        s3.upload_file(local_path, bucket_name, s3_key)
        print(f"Upload completed: s3://{bucket_name}/{s3_key}")

    except ClientError as e:
        print(f"Failed to upload to S3: {e}")

def is_valid(item):
    description = item.get("description")
    competencies = item.get("competencies")

    if competencies is None or description is None or description.strip() == "":
        return False

    return True


def process():
    with open('job_raw_data.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    for i, old_job in enumerate(data):
        job = process_item(old_job)
        data[i] = job

    with open('job_data.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def remove_invalid():
    with open('job_data.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    filtered = [item for item in data if is_valid(item)]

    with open('job_data.json', 'w', encoding='utf-8') as f:
        json.dump(filtered, f, ensure_ascii=False, indent=4)

    print(f"Removed invalid jobs. Kept {len(filtered)}/{len(data)} items.")

# process()
remove_invalid()
upload_to_s3()
