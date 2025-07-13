"""
Dataset Generator for Hybrid RAG Evaluation
Generates high-quality evaluation datasets for IT domain QA
"""

import asyncio
import json
import random
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from pathlib import Path
import pandas as pd
from dataclasses import dataclass, asdict
from enum import Enum
import logging
from tqdm.asyncio import tqdm as async_tqdm

from llama_index.core import Document
from llama_index.llms.gemini import Gemini
from llama_index.core.llms import ChatMessage
import google.generativeai as genai

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class QueryType(Enum):
    """Types of queries for evaluation"""
    JOB_SEARCH = "job_search"
    COURSE_RECOMMENDATION = "course_recommendation"
    SKILL_MATCHING = "skill_matching"
    CAREER_PATH = "career_path"
    COMPARATIVE = "comparative"
    MULTI_HOP = "multi_hop"


@dataclass
class EvaluationSample:
    """Single evaluation sample"""
    query_id: str
    query: str
    query_type: QueryType
    ground_truth_answer: str
    expected_sources: List[str]  # Expected document IDs
    metadata: Dict[str, Any]
    context_documents: List[str]  # Actual document contents
    difficulty: str  # easy, medium, hard


class DatasetGenerator:
    """Generates evaluation datasets for Hybrid RAG system"""
    
    def __init__(
        self,
        llm: Optional[Gemini] = None,
        api_key: Optional[str] = None,
        output_dir: str = "evaluation_datasets"
    ):
        self.llm = llm or self._create_default_llm(api_key)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # IT domain-specific templates
        self.query_templates = self._load_query_templates()
        self.skills_list = self._load_skills_list()
        
    def _create_default_llm(self, api_key: str) -> Gemini:
        """Create default LLM for dataset generation"""
        return Gemini(
            model_name='models/gemini-2.0-flash-exp',
            api_key=api_key,
            temperature=0.7,
            max_tokens=2048
        )
    
    def _load_query_templates(self) -> Dict[QueryType, List[str]]:
        """Load query templates for different types"""
        return {
            QueryType.JOB_SEARCH: [
                "Find {level} {role} jobs requiring {skill1} and {skill2}",
                "What {role} positions are available in {location} with {skill}?",
                "Show me remote {role} jobs with salary above {salary}",
                "Find entry-level {role} positions that don't require {skill}"
            ],
            QueryType.COURSE_RECOMMENDATION: [
                "Recommend courses to learn {skill} for {level} developers",
                "What courses should I take to transition from {role1} to {role2}?",
                "Find advanced {skill} courses with hands-on projects",
                "Suggest certification courses for {skill} professionals"
            ],
            QueryType.SKILL_MATCHING: [
                "What skills do I need for a {role} position at {company_type}?",
                "How can I improve my {skill1} to get {role} jobs?",
                "What's the skill gap between {role1} and {role2}?",
                "Which skills are most in-demand for {role} in 2024?"
            ],
            QueryType.CAREER_PATH: [
                "Create a learning path from {current_role} to {target_role}",
                "What's the typical career progression for a {role}?",
                "How long does it take to become a senior {role}?",
                "What certifications help advance from {level} to senior {role}?"
            ],
            QueryType.COMPARATIVE: [
                "Compare {skill1} vs {skill2} for {role} positions",
                "Which is better for career growth: {option1} or {option2}?",
                "Compare job opportunities for {role1} vs {role2}",
                "What pays more: {skill1} or {skill2} expertise?"
            ],
            QueryType.MULTI_HOP: [
                "Find {role} jobs that require {skill1}, then recommend courses to learn it",
                "What skills from {course} help qualify for {role} at {company_type}?",
                "Show career path from {role1} to {role2} with required courses",
                "Find jobs matching my skills in {skill1} and {skill2}, then suggest improvement courses"
            ]
        }
    
    def _load_skills_list(self) -> Dict[str, List[str]]:
        """Load IT skills categorized by type"""
        return {
            "programming_languages": ["Python", "Java", "JavaScript", "TypeScript", "Go", "Rust", "C++", "C#", "Swift", "Kotlin"],
            "frameworks": ["React", "Angular", "Vue.js", "Django", "FastAPI", "Spring Boot", "Express.js", "Next.js", "Flutter", "TensorFlow"],
            "databases": ["PostgreSQL", "MongoDB", "Redis", "Elasticsearch", "Cassandra", "MySQL", "Neo4j", "DynamoDB"],
            "cloud": ["AWS", "Azure", "GCP", "Docker", "Kubernetes", "Terraform", "CloudFormation"],
            "tools": ["Git", "Jenkins", "GitLab CI", "CircleCI", "Jira", "Confluence", "Grafana", "Prometheus"],
            "ai_ml": ["Machine Learning", "Deep Learning", "NLP", "Computer Vision", "RAG", "LLMs", "PyTorch", "Scikit-learn"],
            "roles": ["Software Engineer", "Data Engineer", "ML Engineer", "DevOps Engineer", "Full Stack Developer", 
                     "Backend Developer", "Frontend Developer", "Data Scientist", "Cloud Architect", "Technical Lead"],
            "levels": ["Junior", "Mid-level", "Senior", "Staff", "Principal", "Entry-level"],
            "company_types": ["FAANG", "startup", "enterprise", "consultancy", "fintech", "e-commerce"]
        }
    
    async def generate_dataset(
        self,
        num_samples_per_type: int = 50,
        include_hard_negatives: bool = True,
        include_multi_hop: bool = True
    ) -> pd.DataFrame:
        """Generate comprehensive evaluation dataset"""
        logger.info("Starting dataset generation...")
        samples = []
        
        # Generate samples for each query type
        for query_type in QueryType:
            if query_type == QueryType.MULTI_HOP and not include_multi_hop:
                continue
                
            logger.info(f"Generating {num_samples_per_type} samples for {query_type.value}")
            type_samples = await self._generate_samples_for_type(
                query_type, 
                num_samples_per_type,
                include_hard_negatives
            )
            samples.extend(type_samples)
        
        # Convert to DataFrame
        df = pd.DataFrame([asdict(s) for s in samples])
        
        # Save dataset
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = self.output_dir / f"eval_dataset_{timestamp}.csv"
        df.to_csv(output_file, index=False)
        
        # Also save in JSON format for better structure preservation
        json_file = self.output_dir / f"eval_dataset_{timestamp}.json"
        with open(json_file, 'w') as f:
            json.dump([asdict(s) for s in samples], f, indent=2, default=str)
        
        logger.info(f"Dataset saved to {output_file} and {json_file}")
        return df
    
    async def _generate_samples_for_type(
        self,
        query_type: QueryType,
        num_samples: int,
        include_hard_negatives: bool
    ) -> List[EvaluationSample]:
        """Generate samples for specific query type"""
        samples = []
        templates = self.query_templates[query_type]
        
        for i in async_tqdm(range(num_samples), desc=f"Generating {query_type.value}"):
            # Random template and parameters
            template = random.choice(templates)
            params = self._generate_template_params(query_type)
            
            # Generate query
            query = template.format(**params)
            
            # Generate ground truth and context
            sample = await self._generate_sample_with_llm(
                query, 
                query_type,
                params,
                include_hard_negatives
            )
            
            samples.append(sample)
            
            # Small delay to avoid rate limiting
            await asyncio.sleep(0.1)
        
        return samples
    
    def _generate_template_params(self, query_type: QueryType) -> Dict[str, str]:
        """Generate random parameters for query templates"""
        skills = self.skills_list
        
        params = {
            "skill": random.choice(skills["programming_languages"] + skills["frameworks"]),
            "skill1": random.choice(skills["programming_languages"]),
            "skill2": random.choice(skills["frameworks"]),
            "role": random.choice(skills["roles"]),
            "role1": random.choice(skills["roles"]),
            "role2": random.choice(skills["roles"]),
            "level": random.choice(skills["levels"]),
            "location": random.choice(["San Francisco", "New York", "London", "Berlin", "Singapore", "Remote"]),
            "salary": random.choice(["$100k", "$120k", "$150k", "$200k"]),
            "company_type": random.choice(skills["company_types"]),
            "current_role": random.choice(skills["roles"][:5]),  # Junior roles
            "target_role": random.choice(skills["roles"][5:]),  # Senior roles
            "option1": random.choice(skills["cloud"]),
            "option2": random.choice(skills["cloud"]),
            "course": f"{random.choice(skills['ai_ml'])} Masterclass"
        }
        
        return params
    
    async def _generate_sample_with_llm(
        self,
        query: str,
        query_type: QueryType,
        params: Dict[str, str],
        include_hard_negatives: bool
    ) -> EvaluationSample:
        """Generate complete sample using LLM"""
        
        # Determine difficulty based on query complexity
        difficulty = self._assess_difficulty(query, query_type)
        
        prompt = f"""
You are creating evaluation data for a Hybrid RAG system in the IT recruitment and education domain.

Generate a comprehensive answer and relevant context for this query:
Query: {query}
Query Type: {query_type.value}
Parameters: {json.dumps(params)}

Please provide:
1. A detailed, accurate answer (2-4 paragraphs)
2. List of 3-5 relevant source documents that would contain this information
3. The actual content of those source documents (each 100-200 words)
4. Any specific skills, requirements, or recommendations mentioned

Format your response as JSON:
{{
    "answer": "detailed answer here",
    "sources": ["source1_id", "source2_id", ...],
    "documents": [
        {{"id": "source1_id", "content": "document content", "type": "job|course", "metadata": {{}}}},
        ...
    ],
    "key_entities": ["skill1", "skill2", "company1", ...]
}}
"""
        
        try:
            response = self.llm.complete(prompt)
            result = json.loads(response.text)
            
            # Create evaluation sample
            sample = EvaluationSample(
                query_id=f"{query_type.value}_{datetime.now().timestamp()}",
                query=query,
                query_type=query_type,
                ground_truth_answer=result["answer"],
                expected_sources=result["sources"],
                metadata={
                    "params": params,
                    "key_entities": result.get("key_entities", []),
                    "generated_at": datetime.now().isoformat()
                },
                context_documents=[doc["content"] for doc in result["documents"]],
                difficulty=difficulty
            )
            
            # Add hard negatives if requested
            if include_hard_negatives:
                sample.metadata["hard_negatives"] = await self._generate_hard_negatives(query, result["documents"])
            
            return sample
            
        except Exception as e:
            logger.error(f"Error generating sample: {e}")
            # Return a basic sample on error
            return EvaluationSample(
                query_id=f"{query_type.value}_{datetime.now().timestamp()}",
                query=query,
                query_type=query_type,
                ground_truth_answer="Error generating answer",
                expected_sources=[],
                metadata={"error": str(e), "params": params},
                context_documents=[],
                difficulty="unknown"
            )
    
    def _assess_difficulty(self, query: str, query_type: QueryType) -> str:
        """Assess query difficulty"""
        # Simple heuristic based on query characteristics
        word_count = len(query.split())
        
        if query_type == QueryType.MULTI_HOP:
            return "hard"
        elif query_type in [QueryType.COMPARATIVE, QueryType.CAREER_PATH]:
            return "medium" if word_count < 15 else "hard"
        else:
            return "easy" if word_count < 10 else "medium"
    
    async def _generate_hard_negatives(self, query: str, documents: List[Dict]) -> List[str]:
        """Generate hard negative examples - similar but incorrect documents"""
        hard_negatives = []
        
        for doc in documents[:2]:  # Generate 2 hard negatives
            prompt = f"""
Generate a similar but incorrect document for this query. 
The document should be related but not answer the query correctly.

Query: {query}
Original correct document: {doc['content']}

Generate a hard negative document (similar topic but different details):
"""
            try:
                response = self.llm.complete(prompt)
                hard_negatives.append(response.text)
            except Exception as e:
                logger.error(f"Error generating hard negative: {e}")
        
        return hard_negatives
    
    async def augment_with_your_data(
        self,
        job_data_path: Optional[str] = None,
        course_data_path: Optional[str] = None
    ) -> pd.DataFrame:
        """Augment dataset with your actual job and course data"""
        logger.info("Augmenting dataset with real data...")
        
        samples = []
        
        if job_data_path:
            job_samples = await self._create_samples_from_jobs(job_data_path)
            samples.extend(job_samples)
        
        if course_data_path:
            course_samples = await self._create_samples_from_courses(course_data_path)
            samples.extend(course_samples)
        
        df = pd.DataFrame([asdict(s) for s in samples])
        
        # Save augmented dataset
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = self.output_dir / f"augmented_dataset_{timestamp}.csv"
        df.to_csv(output_file, index=False)
        
        return df
    
    async def _create_samples_from_jobs(self, job_data_path: str) -> List[EvaluationSample]:
        """Create evaluation samples from real job data"""
        # Implementation depends on your job data format
        # This is a template
        samples = []
        
        with open(job_data_path, 'r') as f:
            jobs = json.load(f)
        
        for job in jobs[:100]:  # Limit to 100 jobs
            # Create different query types for each job
            samples.extend(await self._generate_job_queries(job))
        
        return samples
    
    async def _generate_job_queries(self, job: Dict) -> List[EvaluationSample]:
        """Generate various queries for a single job"""
        samples = []
        
        # Query 1: Direct job search
        query1 = f"Find {job.get('title', 'software engineer')} jobs at {job.get('company', 'tech companies')}"
        
        # Query 2: Skill-based search
        skills = job.get('required_skills', [])
        if skills:
            query2 = f"Show me jobs requiring {' and '.join(skills[:2])}"
        
        # Add more query variations...
        
        return samples
    
    async def _create_samples_from_courses(self, course_data_path: str) -> List[EvaluationSample]:
        """Create evaluation samples from real course data"""
        # Similar implementation for courses
        pass 