import os
import json
import google.generativeai as genai
from app.core.config import configs


class ResumeReport:
    def __init__(self):
        api_key = configs.GEMINI_TOKEN

        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel("gemini-2.0-flash")

    def _build_prompt(self, resume_text, jd_text) -> str:
        """
        Builds the prompt for Gemini based on the resume and job description.
        """
        return f"""
You are a recruitment analyst AI.

Given the resume and the job description below, analyze and provide **strict negative and positive detail technical feedback** in the following categories:
- skills_feedback: Does the resume align with required skills? Any weak or or missing skills?
- role_feedback: Does the candidate seem fit for the role/responsibilities?
- experience_feedback: Is the candidate's experience level and domain a match?
- language_feedback: Is the tone, clarity, and professionalism of the resume appropriate?
- benefit_feedback: Are there any overlaps with job benefits or candidate expectations?
- education_feedback: Is the candidate's education suitable or lacking for the role?
- job_type_feedback: Does the candidate's experience suggest preference for the job type (remote/onsite/contract/full-time)?


##Guide
if there is no positive or negative feedback in a section just leave an empty text
Output JSON format:
{{
  "skills_feedback": {{
    "positive": "...",
    "negative": "..."  
  }},
  "role_feedback": {{
    "positive": "...",
    "negative": "..."  
  }},
  "experience_feedback": {{
    "positive": "...",
    "negative": "..."  
  }},
  "language_feedback": {{
    "positive": "...",
    "negative": "..."  
  }},
  "benefit_feedback": {{
    "positive": "...",
    "negative": "..."  
  }},
  "education_feedback": {{
    "positive": "...",
    "negative": "..."  
  }},
  "job_type_feedback": {{
    "positive": "...",
    "negative": "..."  
  }},
}}

Resume:
{resume_text}

Job Description:
{jd_text}

"""

    def report(self, resume_text, jd_text) -> dict:
        """
        Sends the resume text and job description to the Gemini API and returns structured data.
        """
        prompt = self._build_prompt(resume_text=resume_text, jd_text=jd_text)
        response = self.model.generate_content(
            prompt,
            generation_config={
                "temperature": 0.3,
                "top_k": 2,
                "top_p": 0.9,
                "max_output_tokens": 2000,
            },
        )

        try:
            return json.loads(response.text.replace("```", "").replace("json", ""))
        except json.JSONDecodeError as e:
            raise ValueError("Failed to parse response into JSON") from e
