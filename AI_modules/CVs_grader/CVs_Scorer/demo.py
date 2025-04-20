import streamlit as st
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from cv_grading import clean_resume, final_score
from Pdf_parser.pdf_parser import read_pdf

st.set_page_config(page_title="CV Grader AI", layout="wide")
st.title("AI CV Grader Demo")
st.markdown("Upload a resume PDF and paste a job description to receive a smart grading report.")

resume_file = st.file_uploader("Upload Resume (PDF)", type=["pdf"])
jd_text_input = st.text_area("Paste Job Description", height=300)

if resume_file and jd_text_input:
    try:
        with st.spinner("Analyzing resume and matching to job description..."):
            resume_text_clean = clean_resume(read_pdf(resume_file))
            jd_text_clean = clean_resume(jd_text_input)

            grading = final_score(resume_text_clean, jd_text_clean)
            # similarity = semantic_scoring(resume_text, jd_text_clean)
            # grading = llm_grading(resume_text, jd_text_clean)

        # st.markdown("---")
        # st.subheader("Semantic Similarity Score")
        # st.success(f"{similarity:.2f}")

        st.markdown("---")
        st.subheader("AI Grading Report")
        st.subheader("LLM Grading Score")
        st.success(f"{grading['overall_match']["overall"]:.4f}")

        if grading.get("skills_missing"):
            st.subheader("Skills You Should Learn/Improve")
            st.markdown("`" + "`, `".join(grading['skills_missing']) + "`")
        
        st.markdown("### Missing or Weak Areas")
        for area in grading.get("missing_or_weak_areas", []):
            st.markdown(f"- {area}")

        st.markdown("### Advice for Improvement")
        for tip in grading.get("advice_on_improvements", []):
            st.markdown(f"- {tip}")

    except Exception as e:
        st.error("An error occurred while processing the file.")
        st.exception(e)

elif resume_file is None and jd_text_input:
    st.info("Please upload your resume in PDF format to continue.")

elif resume_file and not jd_text_input:
    st.info("Please paste the job description to continue.")
# streamlit run C:\Users\leduc\OneDrive\Desktop\NLP\grab-capstone-project\NavigaTech\AI_modules\CVs_grader\CVs_Scorer\demo.py