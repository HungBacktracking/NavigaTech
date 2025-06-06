# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

# useful for handling different item types with a single interface
from itemadapter import ItemAdapter

import os
import json
import logging
import time
from typing import Dict, Any, List

from dotenv import load_dotenv
import scrapy
import google.generativeai as genai
from itemadapter import ItemAdapter
from dateutil.relativedelta import relativedelta
from datetime import datetime

from .items import JobItem

load_dotenv()

# AWS S3 configuration
AWS_ACCESS_KEY_ID = os.environ["AWS_ACCESS_KEY_ID"]
AWS_SECRET_ACCESS_KEY = os.environ["AWS_SECRET_ACCESS_KEY"]
AWS_BUCKET_NAME = os.environ["AWS_S3_BUCKET"]
AWS_REGION = os.environ["AWS_REGION"]

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
]

# Retry settings
MAX_RETRIES = 5
RETRY_DELAY_SECONDS = 10

# Job type & level taxonomy
VALID_JOB_TYPES = ["Internship", "Contract", "Full-time", "Part-time", "Freelancer"]
VALID_JOB_LEVELS = ["Intern", "Entry-level", "Junior", "Mid-level", "Senior", "Leader", "Principal"]

# Configure initial Gemini client
token_index = 0
genai.configure(api_key=TOKENS[token_index])
ge_model = genai.GenerativeModel("gemini-2.0-flash")

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def rotate_token():
    """
    Rotate to the next API token in a round-robin fashion.
    """
    global token_index, ge_model
    token_index = (token_index + 1) % len(TOKENS)
    genai.configure(api_key=TOKENS[token_index])
    ge_model = genai.GenerativeModel("gemini-2.0-flash")
    logger.info(f"Rotated to Gemini token index {token_index}")


def build_llm_prompt(raw_item: Dict[str, Any]) -> str:
    prompt = f"""
        You are given a scraped job posting with these attributes in JSON format:

        {json.dumps(raw_item, ensure_ascii=False)}

        Transform it into a normalized JSON object with exactly these keys:
        - from_site
        - title 
        - company 
        - location (English)
        - date_posted (ISO format YYYY-MM-DD)
        - job_url
        - company_logo
        - job_type (one of: {', '.join(VALID_JOB_TYPES)})
        - job_level (one of: {', '.join(VALID_JOB_LEVELS)})
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

        Return only the normalized JSON.
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
            logger.warning(f"JSON parse error on attempt {attempt + 1}: {jde}. Rotating token and retrying.")
            rotate_token()
            time.sleep(RETRY_DELAY_SECONDS)

        except Exception as e:
            logger.error(f"Error calling Gemini on attempt {attempt + 1}: {e}. Rotating token and retrying.")
            rotate_token()
            time.sleep(RETRY_DELAY_SECONDS)

    # If all retries fail, raise an exception
    raise RuntimeError("Exceeded max retries when calling Gemini LLM")


class GeminiNormalizationPipeline:
    """
    Scrapy pipeline that sends each scraped job item to Gemini for normalization.
    """

    def process_item(self, item: JobItem, spider: scrapy.Spider) -> Dict[str, Any]:
        adapter = ItemAdapter(item)
        raw_dict = dict(adapter.asdict())

        # Build prompt for normalization
        prompt = build_llm_prompt(raw_dict)

        try:
            normalized: str = call_gemini_llm(prompt)

        except Exception as err:
            logger.error(f"Failed to normalize item {raw_dict.get('job_url')}: {err}")
            # Optionally, return raw item or drop
            return raw_dict  # or raise DropItem()

        # Merge normalized fields back into item
        return normalized



