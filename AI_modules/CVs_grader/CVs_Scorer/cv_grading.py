from sentence_transformers import SentenceTransformer, util
import google.generativeai as genai
import os
import json
import re
from dotenv import load_dotenv


class ResumeAnalyzer:
    def __init__(self):
        load_dotenv(
            r"C:\Users\leduc\OneDrive\Desktop\NLP\grab-capstone-project\NavigaTech\AI_modules\.env")
        self.hf_token = os.environ["HF_TOKEN"]
        self.model = SentenceTransformer('all-mpnet-base-v2')
        genai.configure(api_key=os.environ["GEMINI_TOKEN"])
        self.ge_model = genai.GenerativeModel("gemini-2.0-flash")

    def clean_resume(self, text):
        text = text.lower()
        text = re.sub(
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '', text)
        text = re.sub(
            r'(\+?\d{1,3})?[-.\s]?(\(?\d{3}\)?|\d{3})[-.\s]?\d{3}[-.\s]?\d{4}', '', text)
        text = re.sub(r'https?://\S+|www\.\S+', '', text)
        text = re.sub(
            r'\b(Name|Email|Phone|Contact|LinkedIn|Address|Scholar|ORCID)\b[:\s]*', '', text, flags=re.IGNORECASE)
        text = re.sub(r'\s+', ' ', text).strip()
        return text

    def semantic_scoring(self, resume_text, jd_text):
        """
        Calculates semantic similarity between cleaned resume and job description
        using SentenceTransformer cosine similarity.
        """

        resume_text = self.clean_resume(resume_text)
        jd_text = self.clean_resume(jd_text)

        resume_embedding = self.model.encode(
            resume_text, convert_to_tensor=True)
        jd_embedding = self.model.encode(jd_text, convert_to_tensor=True)

        semantic_similarity = util.pytorch_cos_sim(
            resume_embedding, jd_embedding).item()
        return semantic_similarity

    def llm_grading(self, resume_text, jd_text):
        """
        Sends the resume and job description to Gemini LLM for detailed grading.
        Returns structured output with scores, missing skills, and feedback.
        """

        gemini_input = f"""
          You are an expert technical recruiter and career advisor. You will assess a candidate's fit for a role based on a Job Description and their Resume.
          
          **IMPORTANT: NO HALLUCINATIONS**
          - All **strengths**, **weaknesses**, **keywords_missing**, and any referenced skills or experiences must be verbatim present or missing in the `{resume_text}` through exact (case-insensitive) substring matching. Do **not** infer, paraphrase, or assume synonyms. If a term is not found exactly in the resume text, do not list it.
          - Give high detail **strengths**, **weaknesses** and **improvement_advice**.
          
          **SCORING GUIDELINES:**
          - **Strict scoring rubric:** award full points only for explicit requirements; deduct 50% of a component score for any missing critical skill or experience.
          - **No hallucinations:** strengths must be directly present in the resume and relevant to the JD. Any skill or tool not mentioned should not appear in strengths.
          **OUTPUT MUST BE EXACT JSON** (no extra text):

          **IMPORTANT STRENGTHS RULE:**
          Return summarized, concise strengths that meet **both** of the following conditions:
          1. The skill, tool, or experience must appear **verbatim** (case-insensitive substring match) in the resume.
          2. The same skill or keyword must also appear **verbatim** in the job description.
          
          Instead of listing raw keywords, write a short phrase or sentence that **summarizes** each relevant matching skill or experience.
          
          Good Example:
          - “Experience using Python and SQL for backend development and analytics.”
          
          Bad Example:
          - “Python”  
          - “AI”  
          - “LLM” (if not in JD)
          
        
          
          ### Rule for Missing or Weak Areas:
          - you need always to point out missing and weak areas if found. You also need to provide high value detail advices to improve that missing and weak skills.
          
          
          ### Example 
          **Expected Output:**
          ```json
          {{
            "overall_match": {{"overall": 0.40, "experience": 0.75, "skills": 0.30}},
            "missing_or_weak_areas": [
              "No React experience.",
              "No TypeScript skills.",
              "Limited SPA architecture understanding."
            ],
            "keywords_missing": ["React", "TypeScript", "SPA", "Redux"],
            "strengths": [
              "3 years of HTML/CSS/JavaScript development.",
              "Solid Git & GitHub workflow experience."
            ],
            "improvement_advice": [
              "Build a sample React/TypeScript SPA and host it on GitHub Pages.",
              "Complete an online React + Redux tutorial and add it as a project.",
              "Highlight responsive design examples with breakpoints in your resume."
            ]
          }}
          {{
            "overall_match": {{
              "overall": 0.84,
              "experience": 0.85,
              "skills": 0.88,
            }},
            "missing_or_weak_areas": [
              "No explicit experience with container orchestration tools like Kubernetes.",
              "Limited exposure to CI/CD pipeline tools such as Jenkins or CircleCI.",
              "No mention of writing technical documentation or API specs."
            ],
            "keywords_missing": [
              "Kubernetes",
              "CI/CD",
              "Jenkins",
              "CircleCI",
              "API documentation"
            ],
            "strengths": [
              "Strong proficiency in Python, matching backend development requirements.",
              "Hands-on experience building and deploying REST APIs with Flask and FastAPI.",
              "Worked extensively with PostgreSQL and MongoDB for scalable data storage.",
              "Familiar with Docker-based development environments.",
              "Experience with cloud deployment using AWS EC2 and S3 aligns with job needs."
            ],
            "improvement_advice": [
              "Gain familiarity with Kubernetes by containerizing a multi-service app.",
              "Set up a personal CI/CD pipeline using GitHub Actions or Jenkins and document it.",
              "Practice writing clear technical documentation and API specs for your existing projects.",
              "Explore deeper integration of container orchestration into your deployment process."
            ]
          }}
          Now do the task with given data:

          Job Description: {jd_text}
          Candidate Resume: {resume_text}
"""
        res = self.ge_model.generate_content(gemini_input,
                                             generation_config={{
                                                 "temperature": 0.2,
                                                 "top_k": 2,
                                                 "top_p": 0.9,
                                                 "max_output_tokens": 2000,
                                             }},
                                             )

        grading = json.loads(res.text.replace("```", "").replace("json", ""))
        return grading

    def final_score(self, resume_text, jd_text):
        """
        Combines LLM-based grading and semantic similarity to compute a weighted final score.
        Returns the full JSON output with scores and recommendations.
        """

        llm_s = self.llm_grading(resume_text, jd_text)
        se_s = self.semantic_scoring(resume_text, jd_text)
        llm_s["overall_match"]["overall"] = 0.7 * \
            llm_s["overall_match"]["overall"] + 0.3*se_s
        return llm_s
