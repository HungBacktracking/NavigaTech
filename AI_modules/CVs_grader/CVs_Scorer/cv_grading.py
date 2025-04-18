from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
from sentence_transformers import SentenceTransformer, util
import google.generativeai as genai
import os
import json
import re
from dotenv import load_dotenv


load_dotenv(r"C:\Users\leduc\OneDrive\Desktop\NLP\Grab-project\.env")

hf_token = os.environ["HF_TOKEN"]
model = SentenceTransformer('all-mpnet-base-v2')
genai.configure(api_key=os.environ["GEMINI_TOKEN"])
ge_model = genai.GenerativeModel("gemini-2.0-flash")


def clean_resume(text):
    text = text.lower()
    text = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '', text)
    text = re.sub(r'(\+?\d{1,3})?[-.\s]?(\(?\d{3}\)?|\d{3})[-.\s]?\d{3}[-.\s]?\d{4}', '', text)
    text = re.sub(r'https?://\S+|www\.\S+', '', text)
    text = re.sub(r'\b(Name|Email|Phone|Contact|LinkedIn|Address|Scholar|ORCID)\b[:\s]*', '', text, flags=re.IGNORECASE)
    text = re.sub(r'\s+', ' ', text).strip()
    return text



def semantic_scoring(resume_text, jd_text):
    
    resume_text = clean_resume(resume_text)
    jd_text = clean_resume(jd_text)
   
    resume_embedding = model.encode(resume_text, convert_to_tensor=True)
    jd_embedding = model.encode(jd_text, convert_to_tensor=True)

    semantic_similarity = util.pytorch_cos_sim(resume_embedding, jd_embedding).item()

    return semantic_similarity

def llm_grading(resume_text: str, jd_text: str):
    gemini_input = f"""
    You are an expert technical recruiter and career advisor.

    Given the following job description and candidate resume, do the following:

    1. **Score the overall match from 0 to 1 it is a float number** based on how well the candidate fits the job requirements.
    - if the job title or work is not relevent just return very low score.
    2. **List missing or weak areas**
    3. **Advise on improvements** – suggest what the candidate can add to their CV to better match the role.
    4. **List keywords that missing in resume**
    5. Be concise but clear, and format the response in Markdown for readability.
    6. **OUTPUT FORMAT MUST BE JSON:**

    Respond only in the exact JSON format shown below. Do not add any text outside the JSON block.

    ---

    **Job Description:**
    {jd_text}

    ---

    **Candidate Resume:**
    {resume_text}

    
    **Sample Output Format**
    ```json
    {{
      "overall_match": 0.43,
      "missing_or_weak_areas": [
        "No exposure to Unity, Unreal, or any game engine tools.",
        "No specific focus on AI for game development or visual recognition.",
        "Missing essential programming languages used in games (C#, C++).",
        "Limited evidence of direct involvement in collaborative game or AI projects."
      ],
      "advice_on_improvements": [
        "Start learning Unity or Unreal Engine and build a simple demo.",
        "Pick up a course or tutorial in C++ or C# and implement a basic game mechanic.",
        "Look into AI tasks relevant to game development like enemy pathfinding or procedural world generation.",
        "Engage in team-based AI projects and include your role in collaboration and design."
      ],
      "skills_missing": [
        "Unity",
        "Unreal Engine",
        "C#",
        "C++",
        "Game AI Concepts",
        "Team Collaboration in Game Projects"
      ]
    }}
    ```
    **Sample Output Format**
    {{
      "overall_match": 0.91,
      "missing_or_weak_areas": [],
      "advice_on_improvements": [
        "Continue building advanced AI mechanics such as adaptive enemy behaviors or procedural world systems.",
        "Consider contributing to open-source game AI libraries or plugins for Unity/Unreal.",
        "Explore optimization techniques for real-time AI decision-making under hardware constraints."
      ],
      "skills_missing": []
    }}

    {{
      "overall_match": 0.17,
      "missing_or_weak_areas": [
        "No formal education in pharmacology, chemistry, or medicine.",
        "Lacks required certifications or licensure (e.g., PharmD, pharmacy board exams).",
        "No knowledge of drug interactions, prescriptions, or patient safety protocols.",
        "No clinical experience or understanding of healthcare systems and regulations."
      ],
      "advice_on_improvements": [
        "Enroll in a formal pharmacy program to gain necessary credentials.",
        "Complete internship or training at a certified pharmacy or hospital.",
        "Gain understanding of pharmacokinetics, patient care, and ethical practice.",
        "Prepare for and pass pharmacy licensing exams (e.g., NAPLEX)."
      ],
      "skills_missing": [
        "Pharmacology",
        "Prescription Drug Knowledge",
        "Clinical Experience",
        "Pharmacy Licensure",
        "Healthcare Regulations",
        "Patient Counseling",
        "Medical Ethics"
      ]
    }}



    """

    res = ge_model.generate_content(gemini_input, 
        generation_config={
            "temperature": 0.6,
            "top_k": 3,
            "top_p": 0.9,
            "max_output_tokens": 1000,
        },
        
    )

    grading = json.loads(res.text.replace("```", "").replace("json", ""))
    return grading


def final_score(resume_text, jd_text):
    llm_s = llm_grading(resume_text, jd_text)
    se_s = semantic_scoring(resume_text, jd_text)

    score = 0.7*llm_s["overall_match"] + 0.3*se_s
    llm_s["overall_match"] = score 
    return llm_s


