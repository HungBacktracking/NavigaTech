from typing import List, Dict, Any, Optional
import json
import pandas as pd
from pathlib import Path
import asyncio
from datetime import datetime


class EvaluationDataset:
    """Manages evaluation datasets for testing the Hybrid RAG system"""
    
    def __init__(self, dataset_path: Optional[str] = None):
        self.dataset_path = dataset_path
        self.queries = []
        self.ground_truth = {}
        
        if dataset_path:
            self.load_dataset(dataset_path)
    
    def load_dataset(self, path: str):
        """Load evaluation dataset from JSON file"""
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        self.queries = data.get('queries', [])
        self.ground_truth = data.get('ground_truth', {})
    
    def save_dataset(self, path: str):
        """Save evaluation dataset to JSON file"""
        data = {
            'queries': self.queries,
            'ground_truth': self.ground_truth,
            'metadata': {
                'created_at': datetime.now().isoformat(),
                'num_queries': len(self.queries)
            }
        }
        
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def add_query(self, query_id: str, question: str, domain: str = 'general',
                  relevant_docs: List[str] = None, reference_answer: str = None,
                  relevance_scores: Dict[str, float] = None):
        """Add a query with ground truth to the dataset"""
        query = {
            'id': query_id,
            'question': question,
            'domain': domain
        }
        self.queries.append(query)
        
        self.ground_truth[query_id] = {
            'relevant_docs': relevant_docs or [],
            'reference_answer': reference_answer or '',
            'relevance_scores': relevance_scores or {}
        }
    
    def get_query_batch(self, batch_size: int = 10, offset: int = 0) -> List[Dict[str, Any]]:
        """Get a batch of queries for evaluation"""
        return self.queries[offset:offset + batch_size]
    
    def create_it_domain_dataset(self) -> 'EvaluationDataset':
        """Create a specialized IT domain evaluation dataset"""
        # Job-related queries
        self.add_query(
            'job_001',
            'What are the required skills for a Data Engineer position?',
            'job',
            relevant_docs=['job_de_001', 'job_de_002', 'job_de_003'],
            reference_answer='A Data Engineer typically requires skills in SQL, Python, data warehousing, ETL processes, cloud platforms (AWS/Azure/GCP), big data technologies (Spark, Hadoop), and database management.',
            relevance_scores={'job_de_001': 1.0, 'job_de_002': 0.9, 'job_de_003': 0.8}
        )
        
        self.add_query(
            'job_002',
            'Find senior backend developer jobs with Python experience',
            'job',
            relevant_docs=['job_be_001', 'job_be_002', 'job_be_003', 'job_be_004'],
            reference_answer='Senior backend developer positions with Python typically require 5+ years of experience, proficiency in Python frameworks (Django/Flask/FastAPI), database design, REST APIs, microservices architecture, and DevOps practices.',
            relevance_scores={'job_be_001': 1.0, 'job_be_002': 0.95, 'job_be_003': 0.9, 'job_be_004': 0.85}
        )
        
        # Course-related queries
        self.add_query(
            'course_001',
            'What courses should I take to learn machine learning?',
            'course',
            relevant_docs=['course_ml_001', 'course_ml_002', 'course_ml_003'],
            reference_answer='To learn machine learning, start with courses covering linear algebra, statistics, Python programming, then progress to ML fundamentals, deep learning, and specialized topics like NLP or computer vision.',
            relevance_scores={'course_ml_001': 1.0, 'course_ml_002': 0.9, 'course_ml_003': 0.85}
        )
        
        self.add_query(
            'course_002',
            'Recommend cloud computing certification courses',
            'course',
            relevant_docs=['course_cloud_001', 'course_cloud_002', 'course_cloud_003'],
            reference_answer='For cloud computing certifications, consider AWS Certified Solutions Architect, Azure Administrator, Google Cloud Professional Cloud Architect courses. Start with fundamentals before pursuing professional certifications.',
            relevance_scores={'course_cloud_001': 1.0, 'course_cloud_002': 0.95, 'course_cloud_003': 0.9}
        )
        
        # Skill-based queries
        self.add_query(
            'skill_001',
            'What programming languages are most in-demand for full-stack developers?',
            'skill',
            relevant_docs=['skill_fs_001', 'skill_fs_002', 'job_fs_001'],
            reference_answer='Full-stack developers should know JavaScript (React/Vue/Angular for frontend, Node.js for backend), Python or Java for backend, SQL for databases, and familiarity with TypeScript is increasingly valuable.',
            relevance_scores={'skill_fs_001': 1.0, 'skill_fs_002': 0.9, 'job_fs_001': 0.8}
        )
        
        # Career path queries
        self.add_query(
            'career_001',
            'How can I transition from software developer to DevOps engineer?',
            'career',
            relevant_docs=['career_devops_001', 'course_devops_001', 'job_devops_001'],
            reference_answer='To transition to DevOps, learn CI/CD tools (Jenkins, GitLab CI), containerization (Docker, Kubernetes), infrastructure as code (Terraform), cloud platforms, monitoring tools, and scripting languages like Python and Bash.',
            relevance_scores={'career_devops_001': 1.0, 'course_devops_001': 0.85, 'job_devops_001': 0.8}
        )
        
        # Complex queries requiring both job and course information
        self.add_query(
            'complex_001',
            'I want to become a data scientist. What jobs should I target and what courses should I take?',
            'complex',
            relevant_docs=['job_ds_001', 'job_ds_002', 'course_ds_001', 'course_ds_002', 'career_ds_001'],
            reference_answer='For data science, target junior data analyst or ML engineer roles initially. Take courses in statistics, Python/R programming, machine learning, data visualization, and SQL. Build a portfolio with real projects.',
            relevance_scores={
                'job_ds_001': 0.9, 'job_ds_002': 0.85, 
                'course_ds_001': 1.0, 'course_ds_002': 0.95, 
                'career_ds_001': 0.9
            }
        )
        
        return self
    
    def to_dataframe(self) -> pd.DataFrame:
        """Convert dataset to pandas DataFrame for analysis"""
        data = []
        for query in self.queries:
            gt = self.ground_truth.get(query['id'], {})
            data.append({
                'query_id': query['id'],
                'question': query['question'],
                'domain': query['domain'],
                'num_relevant_docs': len(gt.get('relevant_docs', [])),
                'has_reference_answer': bool(gt.get('reference_answer')),
                'has_relevance_scores': bool(gt.get('relevance_scores'))
            })
        
        return pd.DataFrame(data)


class TestCase:
    """Represents a single test case for evaluation"""
    
    def __init__(self, query_id: str, question: str, ground_truth: Dict[str, Any]):
        self.query_id = query_id
        self.question = question
        self.ground_truth = ground_truth
        self.results = {}
    
    def add_retrieval_results(self, retrieved_docs: List[Dict[str, Any]]):
        """Add retrieval results to test case"""
        self.results['retrieved_docs'] = retrieved_docs
        self.results['retrieval_timestamp'] = datetime.now().isoformat()
    
    def add_generation_results(self, generated_answer: str, latency: float):
        """Add generation results to test case"""
        self.results['generated_answer'] = generated_answer
        self.results['generation_latency'] = latency
        self.results['generation_timestamp'] = datetime.now().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert test case to dictionary"""
        return {
            'query_id': self.query_id,
            'question': self.question,
            'ground_truth': self.ground_truth,
            'results': self.results
        } 