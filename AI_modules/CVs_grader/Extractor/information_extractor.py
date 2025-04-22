import pandas as pd
import google.generativeai as genai
import json
import os
from dotenv import load_dotenv

# Cái này để load file .env
load_dotenv(
    r"C:\Users\leduc\OneDrive\Desktop\NLP\grab-capstone-project\NavigaTech\AI_modules\.env")

with open(r"C:\Users\leduc\OneDrive\Desktop\NLP\grab-capstone-project\NavigaTech\AI_modules\data\rag_data\sample_data.json", "rb") as f:
    data = json.load(f)
df = pd.DataFrame(data)

# Cần thêm GEMINI_API TOKEN vào đây
genai.configure(api_key=os.environ["GEMINI_TOKEN"])
ge_model = genai.GenerativeModel("gemini-2.0-flash")


def job_parser(jd_text):
    """
    Take job description and return a JSON contain parsed contents: job level, qualifications, responsibilities, benefits
    """

    gemini_input = f"""
        You are an expert in job description analysis. Your task is to extract structured information from unstructured job descriptions.

        Given the job description below, return the following fields in **valid JSON format**:

        1. **job_level** — e.g., Internship, Entry-Level, Mid-Level, Senior, Director, etc.
        2. **qualifications** — A list of required or preferred degrees, educational background, certifications, or prior experience.
        3. **responsibilities** — A list of key responsibilities and tasks mentioned in the role.
        4. **benefits** — A list of perks, learning outcomes, or benefits associated with the role (e.g., mentorship, flexibility, health insurance, skill development, etc.).

        **IMPORTANT RULES**
        - if any fields missing just return a empty list in that missing field
        The output must follow this format:

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
                ]
        }}

        Now parse job description:
        {jd_text}

        return with JSON format
"""
    res = ge_model.generate_content(gemini_input,
                                    generation_config={
                                        "temperature": 0.2,
                                        "top_k": 2,
                                        "top_p": 0.9,
                                        "max_output_tokens": 2000,
                                    },
                                    )

    job_parse = json.loads(res.text.replace("```", "").replace("json", ""))
    return job_parse
