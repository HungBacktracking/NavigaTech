import os
import json
from dotenv import load_dotenv
import google.generativeai as genai


class ResumeParser:
    def __init__(self):
        """
        Initializes the parser with the resume text and optional .env file path for API key.
        """
        load_dotenv(
            r"C:\Users\leduc\OneDrive\Desktop\NLP\grab-capstone-project\NavigaTech\AI_modules\.env")

        api_key = os.environ.get("GEMINI_TOKEN")
        if not api_key:
            raise ValueError(
                "GEMINI_TOKEN not found in environment variables.")

        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel("gemini-2.0-flash")

    def _build_prompt(self, resume_text) -> str:
        """
        Builds the prompt for Gemini based on the resume.
        """
        return f"""
You are an AI assistant that extracts structured information from resumes.  

Given the raw resume text, analyze and extract the following fields in clean JSON format. Do not include fields that are missing or irrelevant. Use inferred values only when explicitly mentioned or clearly implied. Be concise and accurate.

Output Format:
{{
    "summary": "Generate a concise 2–4 sentence professional summary that captures the candidate's background, education, and focus areas based on the resume content.",
    "skills": ["Extract a clean list of technical and soft skills mentioned in the resume. Avoid duplicates."],
    "basic_info": {{
        "full_name": "Infer the candidate's full name from the resume header or contact section.",
        "university": "Extract the name of the most recent or relevant university attended.",
        "education_level": "Detect the highest degree level mentioned (e.g., BS, MS, PhD).",
        "majors": ["List major fields of study or programs, and include GPA if mentioned (e.g., 'Computer Science', 'GPA: 3.8')"],
        "email": "Extract email."
    }},
    "work_experience": [
        {{
            "job_title": "Extract the job title held by the candidate.",
            "company": "Name of the company where the candidate worked.",
            "location": "Location of the job (city/country if available).",
            "duration": "Duration or timeframe of employment (e.g., 'Jun 2020 – Aug 2022').",
            "job_summary": "Summarize main responsibilities, technologies used, and notable achievements for the role."
        }}
    ],
    "project_experience": [
        {{
            "project_name": "Name of the project as stated in the resume.",
            "project_description": "Summarize what the project did, the candidate’s role, and technologies or tools used."
        }}
    ],
    "award": [
        {{
            "award_name": "List academic, professional, or competition-based awards mentioned."
        }}
    ]
}}

Resume Text:
{resume_text}
"""

    def parse(self, resume_text) -> dict:
        """
        Sends the resume text to the Gemini API and returns structured data.
        """
        prompt = self._build_prompt(resume_text=resume_text)
        response = self.model.generate_content(
            prompt,
            generation_config={
                "temperature": 0.2,
                "top_k": 2,
                "top_p": 0.9,
                "max_output_tokens": 2000,
            },
        )

        try:
            return json.loads(response.text.replace("```", "").replace("json", ""))
        except json.JSONDecodeError as e:
            raise ValueError("Failed to parse response into JSON") from e
