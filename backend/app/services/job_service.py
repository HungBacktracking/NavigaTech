import uuid
from typing import Optional, List
from uuid import UUID

from app.convert.job import to_favorite_job_response
from app.exceptions.custom_error import CustomError
from app.job_report.cv_ai_report import ResumeReport
from app.job_report.cv_grading import ResumeScorer
from app.model.favorite_job import FavoriteJob
from app.model.job import Job
from app.recommendation.job_recommendation import JobRecommendation
from app.repository.favorite_job_repository import FavoriteJobRepository
from app.repository.job_repository import JobRepository
from app.schema.job_schema import JobSearchRequest, JobFavoriteResponse, JobResponse, FavoriteJobRequest
from app.services.base_service import BaseService


class JobService(BaseService):
    def __init__(
        self,
        job_repository: JobRepository,
        favorite_job_repository: FavoriteJobRepository
    ):
        self.job_repository = job_repository
        self.favorite_job_repository = favorite_job_repository
        super().__init__(job_repository)
        self.scorer: ResumeScorer = ResumeScorer()
        self.reporter: ResumeReport = ResumeReport()
        self.recommendation = JobRecommendation("job_description")

    def search_job(self, request: JobSearchRequest, user_id: UUID) -> list[JobResponse]:
        rows: List[tuple[Job, Optional[FavoriteJob]]] = (
            self.job_repository.search_job(request, user_id)
        )

        results: List[JobResponse] = []
        for job, fav in rows:
            results.append(
                JobResponse(
                    id=job.id,
                    job_url=job.job_url,
                    logo_url=job.logo_url,
                    job_name=job.job_name,
                    company_name=job.company_name,
                    company_type=job.company_type,
                    company_address=job.company_address,
                    company_description=job.company_description,
                    job_type=job.job_type,
                    skills=job.skills,
                    location=job.location,
                    date_posted=job.date_posted,
                    job_description=job.job_description,
                    job_requirement=job.job_requirement,
                    benefit=job.benefit,
                    is_expired=job.is_expired,

                    is_analyze=fav.is_analyze if fav else False,
                    resume_url=fav.resume_url if fav else None,
                    is_favorite=fav.is_favorite if fav else False,
                )
            )

        return results

    def get_user_favorite_jobs_with_analytics(self, user_id: UUID) -> List[JobFavoriteResponse]:
        rows = self.job_repository.find_favorite_job_with_analytics(user_id)

        return [
            to_favorite_job_response(job, fav, analytic)
            for job, fav, analytic in rows
        ]




    def get_job_recommendation(self, user_id: UUID):
        resume_text = """
                    {'summary': 'An AI Engineer intern specializing in Large Language Models (LLMs) with experience in fine-tuning and optimizing NLP and Generative AI models. Proficient in building web applications and model fine-tuning, with a focus on prompt engineering and transfer learning. Familiar with HuggingFace, YOLO, Pytorch, Flask, NodeJS, and ReactJS.',
                     'skills': ['Pytorch',
                      'Tensorflow',
                      'scikit-learn',
                      'pandas',
                      'numpy',
                      'matplotlib',
                      'HuggingFace',
                      'LLamaIndex',
                      'LangChains',
                      'NLTK',
                      'Gemini LLM',
                      'CohereAI',
                      'YOLO',
                      'EasyOCR',
                      'Roboflow',
                      'Flask',
                      'NodeJS',
                      'Postman',
                      'ReactJS',
                      'Redux',
                      'Streamlit',
                      'Gradio',
                      'MaterialUI',
                      'MongoDB',
                      'PinconeDB',
                      'ChromaDB',
                      'MySQL',
                      'Google Scholar',
                      'ACL anathology',
                      'Prompt engineering',
                      'Transfer learning',
                      'NLP',
                      'Generative AI',
                      'RAG',
                      'RESTapi',
                      'OpenCV'],
                     'basic_info': {'full_name': 'Le Duc Tai',
                      'university': 'University of Information Technology of Ho Chi Minh city (UIT)',
                      'education_level': 'BS',
                      'majors': ['Computer Science', 'GPA: 3.5'],
                      'email': 'leductai2201@gmail.com',
                      'github': 'https://github.com/NBTailee',
                      'linkedin': 'https://www.linkedin.com/in/%C4%91%E1%BB%A9c-t%C3%A0i-l%C3%AA-5a512b236/'},
                     'work_experience': [],
                     'project_experience': [{'project_name': 'UIT Agent with multi flow answering system',
                       'project_description': 'Implements a system to distinguish casual conversation queries and route them appropriately. Utilizes HyDE Query Transformation to enhance search performance for complex queries. Combines BM25 and Semantic Search for precise and contextually relevant results. Ensures accurate historical context retrieval through metadata filtering. Optimizes search result order based on relevance and context using reranking mechanisms. Leverages HuggingFace for advanced natural language understanding and response generation. Multi-stage query pipeline with modular end-to-end resolution. Tech Stack: Pinecone, LlamaIndex, Hugging Face, Gemini, Cohere, Flask, ReactJS.'},
                      {'project_name': 'AI information retrieval Web Application',
                       'project_description': 'Extracted token length, conducted sentiment analysis, emotion classification, and summarized text in English and Vietnamese. Fine-tuned "phoBART-syllable-base" for superior Vietnamese text summarization with QLora and Quantization techniques. Implemented object detection, optical character recognition (OCR), and image captioning using zero-shot learning models from Ultralytics and EasyOCR. Developed capabilities for audio-to-text conversion and sound classification.'},
                      {'project_name': 'RAG chatbot for course information',
                       'project_description': 'Designed and implemented a Retrieval-Augmented Generation (RAG) application utilizing the Vietstral-7B model from HuggingFace. Integrated advanced LangChains and CohereAI capabilities to enhance model performance. Utilized ChromaDB as the retrieval database, employing Cosine similarity and Reranker techniques for efficient and accurate data retrieval from large datasets. Enabled context-aware responses by feeding retrieved data into the LLM. Developed an intuitive user interface for the application using Gradio.'},
                      {'project_name': 'Median Judgment Classification in 7 Languages',
                       'project_description': 'Implemented stacked embeddings, averaged embeddings, and Natural Language Inference (NLI) with BERT-based and generative models. Enhanced model performance through custom tokens, data augmentation, and Named Entity Recognition (NER)-based preprocessing. Achieved 0.596 Krippendorff’s α score, significantly improving baseline classification results. Machine Learning & NLP: BERT, RoBERTa, XLM-R, BART, Cosine Similarity, NLI. Data Processing: Stratified K-Fold Cross-Validation, Lemmatization, Text Expansion. Development Frameworks: Hugging Face, PyTorch, TensorFlow. Fine-tuned models on Kaggle P100 GPUs using AdamW & AdaFactor optimizers'},
                      {'project_name': 'Stereotype classification in Spanish',
                       'project_description': 'Finetuning BETO, RoBERTa, XLM-RoBERTa, mDeBERTa-v3, DeHATEbert. Finetuning XLM-RoBERTa-twitter-hate. Using ensemble learning methods: Hard-voting, Soft-voting, Stacking. Make use of Adapter Head to improve performance. Apply Handcraft-Features for BERT-based models. Finetuning SVM, RandomForest with GridSearchCV, cross-validation.'},
                      {'project_name': 'Detecting Violation of Helmet Rule for Motorcyclists',
                       'project_description': 'Developed an AI-powered system to detect motorcyclist helmet violations using state-of-the-art object detection models. Addressed Key Challenges: Tackled unbalanced data and small object detection issues by fine-tuning YOLOv8 with a p2 head and implementing the SAHI algorithm to enhance precision and recall. Advanced Object Detection Models: Fine-tuned Real-Time DETR for accurate object detection and integrated the latest YOLOv9 for improved efficiency. Deep Learning & Computer Vision: YOLOv8, YOLOv9, DETR, SAHI algorithm. Model Optimization: Fine-tuning, small object detection enhancement, precision-recall improvement. Development Frameworks: PyTorch, TensorFlow, OpenCV.'}],
                     'award': [{'award_name': 'Top 3rd CoMeDi competition track 1 of COLING 2025 conference'},
                      {'award_name': 'Top 8th in SemEval 2025 track 9 The Food Hazard Detection Challenge of ACL conference.'},
                      {'award_name': 'Top 9th DETEST-Dis IberLef 2024 competition track 1 of SEPLN conference'},
                      {'award_name': 'Top 34th in AI City Challenge 2024 competition Track 5'},
                      {'award_name': 'Data Scientist Associate Certificate - Datacamp'},
                      {'award_name': 'IBM Data Science Specialization - IBM'},
                      {'award_name': 'Machine Learning Specialization - DeepLearning.io'},
                      {'award_name': 'SQL (Intermediate) Certificate - Hackerrank'}]}

                    """

        return self.recommendation.search(resume_text)

    def analyze_job(self, job_id: UUID, user_id: UUID):
        job: Job = self.job_repository.find_by_id(job_id)
        if not job:
            raise CustomError.NOT_FOUND.as_exception()

        job_dict = job.model_dump()
        jd_text = rf"""\
                Title: {job_dict.get("job_name", "")}
                Job level: {job_dict.get("job_type", "")}
                Working type: {job_dict.get("job_type", "")}
                Company: {job_dict.get("company_name", "")}

                Description: {job_dict.get("job_description", "")}\
                Benefit: {job_dict.get("benefit", "")}\
                Requirements: {job_dict.get("job_requirement", "")}\\
                Skills: {" ".join(job_dict.get("skills", ""))}
            """

        resume_text = """
            {'summary': 'An AI Engineer intern specializing in Large Language Models (LLMs) with experience in fine-tuning and optimizing NLP and Generative AI models. Proficient in building web applications and model fine-tuning, with a focus on prompt engineering and transfer learning. Familiar with HuggingFace, YOLO, Pytorch, Flask, NodeJS, and ReactJS.',
             'skills': ['Pytorch',
              'Tensorflow',
              'scikit-learn',
              'pandas',
              'numpy',
              'matplotlib',
              'HuggingFace',
              'LLamaIndex',
              'LangChains',
              'NLTK',
              'Gemini LLM',
              'CohereAI',
              'YOLO',
              'EasyOCR',
              'Roboflow',
              'Flask',
              'NodeJS',
              'Postman',
              'ReactJS',
              'Redux',
              'Streamlit',
              'Gradio',
              'MaterialUI',
              'MongoDB',
              'PinconeDB',
              'ChromaDB',
              'MySQL',
              'Google Scholar',
              'ACL anathology',
              'Prompt engineering',
              'Transfer learning',
              'NLP',
              'Generative AI',
              'RAG',
              'RESTapi',
              'OpenCV'],
             'basic_info': {'full_name': 'Le Duc Tai',
              'university': 'University of Information Technology of Ho Chi Minh city (UIT)',
              'education_level': 'BS',
              'majors': ['Computer Science', 'GPA: 3.5'],
              'email': 'leductai2201@gmail.com',
              'github': 'https://github.com/NBTailee',
              'linkedin': 'https://www.linkedin.com/in/%C4%91%E1%BB%A9c-t%C3%A0i-l%C3%AA-5a512b236/'},
             'work_experience': [],
             'project_experience': [{'project_name': 'UIT Agent with multi flow answering system',
               'project_description': 'Implements a system to distinguish casual conversation queries and route them appropriately. Utilizes HyDE Query Transformation to enhance search performance for complex queries. Combines BM25 and Semantic Search for precise and contextually relevant results. Ensures accurate historical context retrieval through metadata filtering. Optimizes search result order based on relevance and context using reranking mechanisms. Leverages HuggingFace for advanced natural language understanding and response generation. Multi-stage query pipeline with modular end-to-end resolution. Tech Stack: Pinecone, LlamaIndex, Hugging Face, Gemini, Cohere, Flask, ReactJS.'},
              {'project_name': 'AI information retrieval Web Application',
               'project_description': 'Extracted token length, conducted sentiment analysis, emotion classification, and summarized text in English and Vietnamese. Fine-tuned "phoBART-syllable-base" for superior Vietnamese text summarization with QLora and Quantization techniques. Implemented object detection, optical character recognition (OCR), and image captioning using zero-shot learning models from Ultralytics and EasyOCR. Developed capabilities for audio-to-text conversion and sound classification.'},
              {'project_name': 'RAG chatbot for course information',
               'project_description': 'Designed and implemented a Retrieval-Augmented Generation (RAG) application utilizing the Vietstral-7B model from HuggingFace. Integrated advanced LangChains and CohereAI capabilities to enhance model performance. Utilized ChromaDB as the retrieval database, employing Cosine similarity and Reranker techniques for efficient and accurate data retrieval from large datasets. Enabled context-aware responses by feeding retrieved data into the LLM. Developed an intuitive user interface for the application using Gradio.'},
              {'project_name': 'Median Judgment Classification in 7 Languages',
               'project_description': 'Implemented stacked embeddings, averaged embeddings, and Natural Language Inference (NLI) with BERT-based and generative models. Enhanced model performance through custom tokens, data augmentation, and Named Entity Recognition (NER)-based preprocessing. Achieved 0.596 Krippendorff’s α score, significantly improving baseline classification results. Machine Learning & NLP: BERT, RoBERTa, XLM-R, BART, Cosine Similarity, NLI. Data Processing: Stratified K-Fold Cross-Validation, Lemmatization, Text Expansion. Development Frameworks: Hugging Face, PyTorch, TensorFlow. Fine-tuned models on Kaggle P100 GPUs using AdamW & AdaFactor optimizers'},
              {'project_name': 'Stereotype classification in Spanish',
               'project_description': 'Finetuning BETO, RoBERTa, XLM-RoBERTa, mDeBERTa-v3, DeHATEbert. Finetuning XLM-RoBERTa-twitter-hate. Using ensemble learning methods: Hard-voting, Soft-voting, Stacking. Make use of Adapter Head to improve performance. Apply Handcraft-Features for BERT-based models. Finetuning SVM, RandomForest with GridSearchCV, cross-validation.'},
              {'project_name': 'Detecting Violation of Helmet Rule for Motorcyclists',
               'project_description': 'Developed an AI-powered system to detect motorcyclist helmet violations using state-of-the-art object detection models. Addressed Key Challenges: Tackled unbalanced data and small object detection issues by fine-tuning YOLOv8 with a p2 head and implementing the SAHI algorithm to enhance precision and recall. Advanced Object Detection Models: Fine-tuned Real-Time DETR for accurate object detection and integrated the latest YOLOv9 for improved efficiency. Deep Learning & Computer Vision: YOLOv8, YOLOv9, DETR, SAHI algorithm. Model Optimization: Fine-tuning, small object detection enhancement, precision-recall improvement. Development Frameworks: PyTorch, TensorFlow, OpenCV.'}],
             'award': [{'award_name': 'Top 3rd CoMeDi competition track 1 of COLING 2025 conference'},
              {'award_name': 'Top 8th in SemEval 2025 track 9 The Food Hazard Detection Challenge of ACL conference.'},
              {'award_name': 'Top 9th DETEST-Dis IberLef 2024 competition track 1 of SEPLN conference'},
              {'award_name': 'Top 34th in AI City Challenge 2024 competition Track 5'},
              {'award_name': 'Data Scientist Associate Certificate - Datacamp'},
              {'award_name': 'IBM Data Science Specialization - IBM'},
              {'award_name': 'Machine Learning Specialization - DeepLearning.io'},
              {'award_name': 'SQL (Intermediate) Certificate - Hackerrank'}]}

            """

        return self.reporter.report(resume_text, jd_text)

    def generate_resume(self, job_id: UUID, user_id: UUID):
        pass

    def score_job(self, job_id: UUID, user_id: UUID):
        job: Job = self.job_repository.find_by_id(job_id)
        if not job:
            raise CustomError.NOT_FOUND.as_exception()

        job_dict = job.model_dump()
        jd_text = rf"""\
            Title: {job_dict.get("job_name", "")}
            Job level: {job_dict.get("job_type", "")}
            Working type: {job_dict.get("job_type", "")}
            Company: {job_dict.get("company_name", "")}
            
            Description: {job_dict.get("job_description", "")}\
            Benefit: {job_dict.get("benefit", "")}\
            Requirements: {job_dict.get("job_requirement", "")}\\
            Skills: {" ".join(job_dict.get("skills", ""))}
        """

        resume_text = """
        {'summary': 'An AI Engineer intern specializing in Large Language Models (LLMs) with experience in fine-tuning and optimizing NLP and Generative AI models. Proficient in building web applications and model fine-tuning, with a focus on prompt engineering and transfer learning. Familiar with HuggingFace, YOLO, Pytorch, Flask, NodeJS, and ReactJS.',
         'skills': ['Pytorch',
          'Tensorflow',
          'scikit-learn',
          'pandas',
          'numpy',
          'matplotlib',
          'HuggingFace',
          'LLamaIndex',
          'LangChains',
          'NLTK',
          'Gemini LLM',
          'CohereAI',
          'YOLO',
          'EasyOCR',
          'Roboflow',
          'Flask',
          'NodeJS',
          'Postman',
          'ReactJS',
          'Redux',
          'Streamlit',
          'Gradio',
          'MaterialUI',
          'MongoDB',
          'PinconeDB',
          'ChromaDB',
          'MySQL',
          'Google Scholar',
          'ACL anathology',
          'Prompt engineering',
          'Transfer learning',
          'NLP',
          'Generative AI',
          'RAG',
          'RESTapi',
          'OpenCV'],
         'basic_info': {'full_name': 'Le Duc Tai',
          'university': 'University of Information Technology of Ho Chi Minh city (UIT)',
          'education_level': 'BS',
          'majors': ['Computer Science', 'GPA: 3.5'],
          'email': 'leductai2201@gmail.com',
          'github': 'https://github.com/NBTailee',
          'linkedin': 'https://www.linkedin.com/in/%C4%91%E1%BB%A9c-t%C3%A0i-l%C3%AA-5a512b236/'},
         'work_experience': [],
         'project_experience': [{'project_name': 'UIT Agent with multi flow answering system',
           'project_description': 'Implements a system to distinguish casual conversation queries and route them appropriately. Utilizes HyDE Query Transformation to enhance search performance for complex queries. Combines BM25 and Semantic Search for precise and contextually relevant results. Ensures accurate historical context retrieval through metadata filtering. Optimizes search result order based on relevance and context using reranking mechanisms. Leverages HuggingFace for advanced natural language understanding and response generation. Multi-stage query pipeline with modular end-to-end resolution. Tech Stack: Pinecone, LlamaIndex, Hugging Face, Gemini, Cohere, Flask, ReactJS.'},
          {'project_name': 'AI information retrieval Web Application',
           'project_description': 'Extracted token length, conducted sentiment analysis, emotion classification, and summarized text in English and Vietnamese. Fine-tuned "phoBART-syllable-base" for superior Vietnamese text summarization with QLora and Quantization techniques. Implemented object detection, optical character recognition (OCR), and image captioning using zero-shot learning models from Ultralytics and EasyOCR. Developed capabilities for audio-to-text conversion and sound classification.'},
          {'project_name': 'RAG chatbot for course information',
           'project_description': 'Designed and implemented a Retrieval-Augmented Generation (RAG) application utilizing the Vietstral-7B model from HuggingFace. Integrated advanced LangChains and CohereAI capabilities to enhance model performance. Utilized ChromaDB as the retrieval database, employing Cosine similarity and Reranker techniques for efficient and accurate data retrieval from large datasets. Enabled context-aware responses by feeding retrieved data into the LLM. Developed an intuitive user interface for the application using Gradio.'},
          {'project_name': 'Median Judgment Classification in 7 Languages',
           'project_description': 'Implemented stacked embeddings, averaged embeddings, and Natural Language Inference (NLI) with BERT-based and generative models. Enhanced model performance through custom tokens, data augmentation, and Named Entity Recognition (NER)-based preprocessing. Achieved 0.596 Krippendorff’s α score, significantly improving baseline classification results. Machine Learning & NLP: BERT, RoBERTa, XLM-R, BART, Cosine Similarity, NLI. Data Processing: Stratified K-Fold Cross-Validation, Lemmatization, Text Expansion. Development Frameworks: Hugging Face, PyTorch, TensorFlow. Fine-tuned models on Kaggle P100 GPUs using AdamW & AdaFactor optimizers'},
          {'project_name': 'Stereotype classification in Spanish',
           'project_description': 'Finetuning BETO, RoBERTa, XLM-RoBERTa, mDeBERTa-v3, DeHATEbert. Finetuning XLM-RoBERTa-twitter-hate. Using ensemble learning methods: Hard-voting, Soft-voting, Stacking. Make use of Adapter Head to improve performance. Apply Handcraft-Features for BERT-based models. Finetuning SVM, RandomForest with GridSearchCV, cross-validation.'},
          {'project_name': 'Detecting Violation of Helmet Rule for Motorcyclists',
           'project_description': 'Developed an AI-powered system to detect motorcyclist helmet violations using state-of-the-art object detection models. Addressed Key Challenges: Tackled unbalanced data and small object detection issues by fine-tuning YOLOv8 with a p2 head and implementing the SAHI algorithm to enhance precision and recall. Advanced Object Detection Models: Fine-tuned Real-Time DETR for accurate object detection and integrated the latest YOLOv9 for improved efficiency. Deep Learning & Computer Vision: YOLOv8, YOLOv9, DETR, SAHI algorithm. Model Optimization: Fine-tuning, small object detection enhancement, precision-recall improvement. Development Frameworks: PyTorch, TensorFlow, OpenCV.'}],
         'award': [{'award_name': 'Top 3rd CoMeDi competition track 1 of COLING 2025 conference'},
          {'award_name': 'Top 8th in SemEval 2025 track 9 The Food Hazard Detection Challenge of ACL conference.'},
          {'award_name': 'Top 9th DETEST-Dis IberLef 2024 competition track 1 of SEPLN conference'},
          {'award_name': 'Top 34th in AI City Challenge 2024 competition Track 5'},
          {'award_name': 'Data Scientist Associate Certificate - Datacamp'},
          {'award_name': 'IBM Data Science Specialization - IBM'},
          {'award_name': 'Machine Learning Specialization - DeepLearning.io'},
          {'award_name': 'SQL (Intermediate) Certificate - Hackerrank'}]}

        """

        return self.scorer.final_score(resume_text, jd_text)

    def add_to_favorite(self, job_id: uuid, user_id: uuid):
        job: Job = self.job_repository.find_by_id(job_id)
        if not job:
            raise CustomError.NOT_FOUND.as_exception()

        request = FavoriteJobRequest(
            job_id=job_id,
            user_id=user_id,
            is_favorite=True
        )

        fav_job = self.favorite_job_repository.find_by_user_id(user_id)
        if fav_job:
            self.favorite_job_repository.update(fav_job.id, request)
        else:
            self.favorite_job_repository.create(request)

        return self.get_user_favorite_jobs_with_analytics(user_id)

    def remove_from_favorite(self, job_id: uuid, user_id: uuid):
        job: Job = self.job_repository.find_by_id(job_id)
        if not job:
            raise CustomError.NOT_FOUND.as_exception()

        fav_job = self.favorite_job_repository.find_by_user_id(user_id)
        if fav_job:
            request = FavoriteJobRequest(
                job_id=job_id,
                user_id=user_id,
                is_favorite=False
            )
            self.favorite_job_repository.update(fav_job.id, request)
        else:
            raise CustomError.NOT_FOUND.as_exception()

        return self.get_user_favorite_jobs_with_analytics(user_id)






