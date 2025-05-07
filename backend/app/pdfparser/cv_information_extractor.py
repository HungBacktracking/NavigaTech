import json


class ResumeParser:
    def __init__(self, llm_model):
        """
        Initializes the parser with the resume text and optional .env file path for API key.
        """

        self.llm_model = llm_model

    def _build_prompt(self, resume_text) -> str:
        """
        Builds the prompt for Gemini based on the resume.
        """
        return f"""
You are an AI assistant that extracts structured information from resumes.  

Given the raw resume text, analyze and extract the following fields in clean JSON format. Do not include fields that are missing or irrelevant. Use inferred values only when explicitly mentioned or clearly implied. Be concise, accurate and remember using DD-MM-YYYY for dates.

Output Format:
{{
    "introduction": "Generate a concise 2–4 sentence professional introduction that captures the candidate's background, education, and focus areas based on the resume content.",
    "headline": "A brief tagline or summary of the candidate’s professional identity.",
    "name": "Infer the candidate's full name from the resume header or contact section.",
    "phone_number": "Contact telephone number.",
    "location": City, region or/and country where the candidate is based.",
    "education": "A one-line summary of highest education (e.g., “Bachelor of Computer Science, University X”).",
    "skills": [
        {{
            "name": "Extract a clean list of technical and soft skills mentioned in the resume. Avoid duplicates.",
        }}
    ],
    "experiences": [
        {{
            "title": "Extract the job title held by the candidate.",
            "company_name": "Name of the company where the candidate worked.",
            "location": "Location of the job (city/country if available).",
            "employment_type": "e.g., Full-time, Internship, Part-time or null.",
            "start_date": "Start date of employment. In DD-MM-YYYY format, or do not include if unknown.",
            "end_date": "End date of employment. In DD-MM-YYYY format, or do not include if unknown.",
            "description": "Summarize main responsibilities, technologies used, and notable achievements for the role.",
            "achievements": "List any notable achievements, contributions or metrics."
        }}
    ],
    "projects": [
        {{
            "project_name": "Name of the project as stated in the resume.",
            "role": "Role or responsibility of the candidate in the project.",
            "description": "Summarize what the project did, the candidate’s role, and technologies or tools used.",
            "achievements": "List any notable achievements, contributions or metrics.",
            "start_date": "Start date of the project. In DD-MM-YYYY format, or do not include if unknown.",
            "end_date": "End date of the project. In DD-MM-YYYY format, or do not include if unknown."
        }}
    ],
    "educations": [
        {{
            "major": "Major coursework completed by the candidate.",
            "school_name": "Name of the school.",
            "degree_type": "e.g., Bachelor, Master, PhD.",
            "gpa": "GPA score or null if not available.",
            "description": "Describe the education and the coursework completed. Can contains any honors or notes.",
            "start_date": "Start date of education. In DD-MM-YYYY format, or do not include if unknown.",
            "end_date": "End date of education. In DD-MM-YYYY format, or do not include if unknown.
        }}
    ],
    "awards": [
        {{
            "name": "List academic, professional, or competition-based awards mentioned. Do not include certificates of courses.",
            "description": "Describe the award and the recipient(s).",
            "award_date": "Date of award. In DD-MM-YYYY format, or do not include if unknown.
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
        response = self.llm_model.generate_content(
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
