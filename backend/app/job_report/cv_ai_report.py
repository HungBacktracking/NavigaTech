import json
import google.generativeai as genai
from google.generativeai import GenerationConfig
from llama_index.core import StorageContext, load_index_from_storage, Settings
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.gemini import Gemini
from llama_index.core.retrievers import VectorIndexRetriever
from llama_index.core.query_engine import RetrieverQueryEngine
from app.core.config import configs


class ResumeReport:
    """
    Analyze a resume vs. job description with multi-agent debate
    """

    def __init__(self,
        turns: int = 2,
        temperature: float = 0.5,
        db_path: str = "app/courses_db",
    ):

        genai.configure(api_key=configs.GEMINI_TOKEN)
        self.db_path = db_path
        self.chat = genai.GenerativeModel("gemini-2.0-flash")
        self.model = "gemini-2.0-flash"
        self.embbeding_model = HuggingFaceEmbedding(
            model_name="BAAI/bge-large-en-v1.5")
        self.llm = Gemini(
            model_name='models/gemini-2.0-flash',
            api_key=configs.GEMINI_TOKEN,
            max_tokens=9000,
            temperature=0.6,
        )
        Settings.llm = self.llm
        Settings.embed_model = self.embbeding_model
        self.turns = turns
        self.temperature = temperature
        self.config = {
            "affirmative_meta": "You are a career coach that comparing and analysing ##resume## to ##job##",
            "affirm_prompt": "List strengths of the candidate and reason why candidate fit with the job",
            "negative_meta": "You are a devil advocate and you always disagree with opinion and explain why the ##resume## is not suitable for ##job##",
            "neg_prompt": "List weaknesses/gaps between resume and job description",
            "judge_meta": "You are an objective HR manager that judge the debate on if ##resume## is suitable ##job##",
            "judge_prompt": """ 
            Based on affirmative: ##aff## and negative: ##neg##, provide final detail structured feedback and detail step by step improve recommendations for the candidate to have higher chances to get the job also recommend interview questions that may in candidate weaknesses. 

            **OUTPUT FORMAT**: JSON and in each JSON field contain MARKDOWN text with structure heading and sub-heading 

            **SAMPLE OUTPUT FORMAT**: 
            { 
                "overall_assessment": < Markdown text>, 
                "strength_details": <Markdown text>, 
                "weakness_concerns": <Markdown text>, 
                "recommendations": <Markdown text>, 
                "questions": <Markdown text>, 
                "conclusion": <Markdown text> 
            } 
            **Do not include double quotation mark in a text** 

            - Overall Assessment (200 tokens length) 
            - Strengths (2000 tokens length): 
            - Weaknesses and Concerns (1500 tokens length): 
            + Sample structure: 
                1.  ## Lack of Explicit AI/ML Experience: ... 
                    *   **Impact:** ... 
                    *   **Concern Level:** High. 

                2.  ## Generative AI Blind Spot: ... 
                    *   **Impact:** ... 
                    *   **Concern Level:** Critical. 

            - Recommendations (3000 tokens length): 
            + sample structure: 
                1.  ##Gain Explicit AI/ML Experience: This is the most crucial step. Hung needs to actively seek out opportunities to gain hands-on experience with AI/ML. 
                    *   **Actionable Steps:** 
                        *   **Personal Projects:** Develop personal AI/ML projects using Python and relevant libraries (TensorFlow, PyTorch, scikit-learn). Focus on projects that demonstrate a clear understanding of AI/ML concepts and techniques. Examples include: 
                            *   Image classification using convolutional neural networks. 
                            *   Sentiment analysis using natural language processing. 
                            *   Time series forecasting using recurrent neural networks. 
                        *   **Online Courses/Certifications:** Complete online courses or certifications on AI/ML from reputable platforms like Coursera, edX, or Udacity. Focus on courses that provide hands-on experience with AI/ML tools and techniques. 
                        *   **Kaggle Competitions:** Participate in Kaggle competitions to gain experience working with real-world datasets and solving challenging AI/ML problems. 
                        *   **Contribute to Open-Source AI/ML Projects:** Contribute to open-source AI/ML projects to gain experience working with experienced developers and learning best practices. 

            - Recommended Interview Questions targeting weaknesses (1500 tokens length): 
            + Only provide question not answer 
            - Conclusion (500 tokens length) 
            **Do not include double quotation mark in a text** 
            """
        }
        self.storage_context = StorageContext.from_defaults(
            persist_dir=self.db_path)
        self.course_index = load_index_from_storage(
            storage_context=self.storage_context, embed_model=self.embbeding_model)
        self.course_retriever = VectorIndexRetriever(
            index=self.course_index,
            similarity_top_k=25
        )
        self.query_engine = RetrieverQueryEngine(
            retriever=self.course_retriever
        )

    def call_model(self, messages: list[dict]) -> str:
        """
        Call the Gemini ChatCompletion endpoint with given messages.
        """
        gen_config = GenerationConfig(
            temperature=self.temperature,
            max_output_tokens=10000
        )

        res = self.chat.generate_content(
            contents=messages, generation_config=gen_config)

        return res.text

    def _build_history(self, role: str, resume: str, job_desc: str) -> list[dict]:

        repl = {"##resume##": resume, "##job##": job_desc}

        def apply(text: str) -> str:
            for k, v in repl.items():
                text = text.replace(k, v)
            return text

        history = []

        if role == "affirmative":
            history.append({
                "role": "user",
                "parts": apply(self.config["affirmative_meta"])
            })
            history.append({
                "role": "user",
                "parts": apply(self.config["affirm_prompt"])
            })
        elif role == "negative":
            history.append({
                "role": "user",
                "parts": apply(self.config["negative_meta"])
            })
            history.append({
                "role": "user",
                "parts": apply(self.config["neg_prompt"])
            })
        elif role == "judge":
            history.append({
                "role": "user",
                "parts": apply(self.config["judge_meta"])
            })
        return history

    def analyze(self, resume: str, job_desc: str) -> str:
        """
        Run the debate and return final structured feedback.
        """

        hist_aff = self._build_history("affirmative", resume, job_desc)
        hist_neg = self._build_history("negative", resume, job_desc)
        for _ in range(self.turns):
            # Agent debates
            resp_aff = self.call_model(hist_aff)
            hist_neg.append({"role": "user", "parts": resp_aff})
            resp_neg = self.call_model(hist_neg)
            hist_aff.append({"role": "user", "parts": resp_neg})

        hist_jud = self._build_history("judge", resume, job_desc)
        final_user = self.config["judge_prompt"] \
            .replace("##aff##", resp_aff) \
            .replace("##neg##", resp_neg)
        hist_jud.append({"role": "user", "parts": final_user})

        return self.call_model(hist_jud)

    def build_roadmap(self, analyze_ouput, jd_text):
        chat_input = {
            "weaknesses": analyze_ouput["weakness_concerns"],
            "recommendation": analyze_ouput["recommendations"]
        }
        chat_query = f""" 
        You are a carrer and skills growth expert. You need to recommend detail step by step roadmap with courses information based on **weaknesses** and **recommendations** for candidate to have higher chance apply for job position. 

        **Guide**: 
        1. Roadmap must contain relevant course information and URL 
        2. Roadmap must have specific time (1-2 months, etc) 

        Weaknesses and Concerns: 
        {chat_input["weaknesses"]} 
        Previous Recommendations: 
        {chat_input["recommendation"]} 
        {jd_text} 

        **Each phase must contain courses with URL** 
        Now generate a detail step by step roadmap with courses information based on **weaknesses** and **recommendations**. 
        Only return the step by step roadmap do not add any greeting stuffs. 

        OUTPUT FORMAT must be MARKDOWN with structure heading and sub heading. 
        """
        analyze_ouput["roadmap"] = self.query_engine.query(chat_query).response
        return analyze_ouput

    def run(self, resume, jd):
        feedback = self.analyze(resume=resume, job_desc=jd)
        data = json.loads(feedback.replace("```", "").replace("json", ""))
        data = self.build_roadmap(data, jd_text=jd)
        for k, v in data.items():
            data[k] = v.replace("\n", "\n\n")

        return data
