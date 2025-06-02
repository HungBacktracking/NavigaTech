import json
from typing import List, Dict, Any, Tuple
from neo4j import AsyncSession
import asyncio
from llama_index.llms.gemini import Gemini
import re


class GraphIngestionService:
    def __init__(self, neo4j_driver, llm: Gemini):
        self.driver = neo4j_driver
        self.llm = llm
        
    async def ingest_jobs(self, job_data: List[Dict[str, Any]]):
        async with self.driver.session() as session:
            for job in job_data:
                await self._create_job_graph(session, job)
    
    async def ingest_courses(self, course_data: List[Dict[str, Any]]):
        async with self.driver.session() as session:
            for course in course_data:
                await self._create_course_graph(session, course)
    
    async def _create_job_graph(self, session: AsyncSession, job: Dict[str, Any]):
        # Create Career node
        await session.run(
            """
            MERGE (c:Career {id: $job_id, title: $title, url: $url})
            SET c.location = $location,
                c.job_type = $job_type,
                c.job_level = $job_level,
                c.salary = $salary,
                c.description = $description
            """,
            job_id=job['id'],
            title=job['title'],
            url=job.get('job_url', ''),
            location=job.get('location', ''),
            job_type=job.get('job_type', ''),
            job_level=job.get('job_level', ''),
            salary=job.get('salary', ''),
            description=job.get('description', '')
        )
        
        # Extract and create competency relationships
        competencies = await self._extract_competencies_from_job(job)
        for comp_type, items in competencies.items():
            for item in items:
                await self._create_competency_relationship(
                    session, job['id'], comp_type, item, 'job'
                )
        
        # Create taxonomy relationships
        if job.get('company'):
            await session.run(
                """
                MERGE (i:Industry {name: $company})
                MERGE (c:Career {id: $job_id})
                MERGE (c)-[:IN_INDUSTRY]->(i)
                """,
                company=job['company'],
                job_id=job['id']
            )
    
    async def _create_course_graph(self, session: AsyncSession, course: Dict[str, Any]):
        # Create Course node
        await session.run(
            """
            MERGE (c:Course {title: $title, url: $url})
            SET c.website = $website,
                c.organization = $organization,
                c.instructor = $instructor,
                c.level = $level,
                c.description = $description
            """,
            title=course['title'],
            url=course.get('url', ''),
            website=course.get('website', ''),
            organization=course.get('organization', ''),
            instructor=course.get('instructor', ''),
            level=course.get('level', ''),
            description=course.get('description', '')
        )
        
        # Create competency relationships from structured data
        if 'competencies' in course:
            for comp_type, items in course['competencies'].items():
                for item in items:
                    await self._create_competency_relationship(
                        session, course['title'], comp_type, item, 'course'
                    )
        
        # Create skill relationships
        if 'skills' in course:
            for skill in course['skills']:
                await self._create_competency_relationship(
                    session, course['title'], 'soft_skills', skill, 'course'
                )
        
        # Create organization relationships
        if course.get('organization'):
            await session.run(
                """
                MERGE (o:Organization {name: $org})
                MERGE (c:Course {title: $title})
                MERGE (o)-[:COLLABORATES_WITH]->(c)
                """,
                org=course['organization'],
                title=course['title']
            )
    
    async def _extract_competencies_from_job(self, job: Dict[str, Any]) -> Dict[str, List[str]]:
        """Extract competencies from job description using LLM"""
        
        # First try to parse from structured fields
        competencies = {
            'programming_languages': [],
            'frameworks': [],
            'platforms': [],
            'tools': [],
            'knowledge': [],
            'soft_skills': [],
            'certifications': []
        }
        
        # Parse skills field if available
        if job.get('skills'):
            skills = [s.strip() for s in job['skills'].split(',')]
            for skill in skills:
                categorized = await self._categorize_skill(skill)
                if categorized:
                    comp_type, normalized_skill = categorized
                    competencies[comp_type].append(normalized_skill)
        
        # Extract from description and requirements using LLM
        text = f"{job.get('description', '')} {job.get('requirements', '')}"
        if text.strip():
            extracted = await self._extract_competencies_with_llm(text)
            for comp_type, items in extracted.items():
                competencies[comp_type].extend(items)
        
        # Deduplicate
        for comp_type in competencies:
            competencies[comp_type] = list(set(competencies[comp_type]))
        
        return competencies
    
    async def _categorize_skill(self, skill: str) -> Tuple[str, str]:
        """Use LLM to categorize a single skill"""
        prompt = f"""
        Categorize the following skill into one of these types:
        - programming_languages: Programming languages (e.g., Python, Java)
        - frameworks: Frameworks and libraries (e.g., Spring, React)
        - platforms: Cloud platforms and operating systems (e.g., AWS, Linux)
        - tools: Development tools and databases (e.g., Git, MySQL)
        - knowledge: Technical knowledge areas (e.g., Algorithms, Machine Learning)
        - certifications: Required certifications (e.g., AWS Certified)
        - soft_skills: Soft skills (e.g., Communication, Leadership) or if the skill does not fit into any of the above categories.
        
        Return ONLY a JSON object with the keys "type" and "name".
        The "type" should be the category name (e.g., "programming_languages").
        The "name" should be the original skill string.
        
        Skill: {skill}
        """
        
        try:
            response = await self.llm.acomplete(prompt)
            json_match = re.search(r'\{.*\}', response.text, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group())
                if "type" in result and "name" in result:
                    # Ensure the type is one of the expected categories
                    valid_types = [
                        'programming_languages', 'frameworks', 'platforms',
                        'tools', 'knowledge', 'soft_skills', 'certifications'
                    ]
                    if result["type"] in valid_types:
                        return result["type"], result["name"]
                    else:
                        return 'soft_skills', result["name"]
        except Exception as e:
            # Log the error or handle it as appropriate
            print(f"Error categorizing skill '{skill}' with LLM: {e}")
            pass
        
        # Default to soft skills if LLM categorization fails
        return 'soft_skills', skill
    
    async def _extract_competencies_with_llm(self, text: str) -> Dict[str, List[str]]:
        """Use LLM to extract competencies from unstructured text"""
        prompt = f"""
        Extract technical competencies from the following job description. 
        Categorize them into:
        - programming_languages: Programming languages (e.g., Python, Java)
        - frameworks: Frameworks and libraries (e.g., Spring, React)
        - platforms: Cloud platforms and operating systems (e.g., AWS, Linux)
        - tools: Development tools and databases (e.g., Git, MySQL)
        - knowledge: Technical knowledge areas (e.g., Algorithms, Machine Learning)
        - soft_skills: Soft skills (e.g., Communication, Leadership)
        - certifications: Required certifications (e.g., AWS Certified)
        
        Return ONLY a JSON object with these categories as keys and lists of items as values.
        
        Text: {text[:2000]}
        """
        
        try:
            response = await self.llm.acomplete(prompt)
            # Parse JSON from response
            json_match = re.search(r'\{.*\}', response.text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        except:
            pass
        
        return {
            'programming_languages': [],
            'frameworks': [],
            'platforms': [],
            'tools': [],
            'knowledge': [],
            'soft_skills': [],
            'certifications': []
        }
    
    async def _create_competency_relationship(
        self, 
        session: AsyncSession, 
        entity_id: str, 
        comp_type: str, 
        comp_value: str,
        entity_type: str  # 'job' or 'course'
    ):
        """Create competency nodes and relationships"""
        
        # Map competency types to node labels
        comp_label_map = {
            'programming_languages': 'ProgrammingLanguage',
            'frameworks': 'Framework',
            'platforms': 'Platform',
            'tools': 'Tool',
            'knowledge': 'Knowledge',
            'soft_skills': 'SoftSkill',
            'certifications': 'Certification'
        }
        
        comp_label = comp_label_map.get(comp_type, 'Competency')
        
        # Create competency node and relationship
        if entity_type == 'job':
            query = f"""
            MERGE (comp:{comp_label} {{name: $comp_value}})
            MERGE (c:Career {{id: $entity_id}})
            MERGE (c)-[:REQUIRES{{type: $comp_type}}]->(comp)
            """
        else:  # course
            query = f"""
            MERGE (comp:{comp_label} {{name: $comp_value}})
            MERGE (c:Course {{title: $entity_id}})
            MERGE (c)-[:TEACHES{{type: $comp_type}}]->(comp)
            """
        
        await session.run(
            query,
            entity_id=entity_id,
            comp_value=comp_value,
            comp_type=comp_type
        )
    
    async def create_indices(self):
        """Create Neo4j indices for better query performance"""
        async with self.driver.session() as session:
            # Create indices
            indices = [
                "CREATE INDEX career_id IF NOT EXISTS FOR (c:Career) ON (c.id)",
                "CREATE INDEX career_title IF NOT EXISTS FOR (c:Career) ON (c.title)",
                "CREATE INDEX course_title IF NOT EXISTS FOR (c:Course) ON (c.title)",
                "CREATE INDEX course_url IF NOT EXISTS FOR (c:Course) ON (c.url)",
                "CREATE INDEX org_name IF NOT EXISTS FOR (o:Organization) ON (o.name)",
                "CREATE INDEX industry_name IF NOT EXISTS FOR (i:Industry) ON (i.name)",
                "CREATE INDEX prog_lang_name IF NOT EXISTS FOR (p:ProgrammingLanguage) ON (p.name)",
                "CREATE INDEX framework_name IF NOT EXISTS FOR (f:Framework) ON (f.name)",
                "CREATE INDEX platform_name IF NOT EXISTS FOR (p:Platform) ON (p.name)",
                "CREATE INDEX tool_name IF NOT EXISTS FOR (t:Tool) ON (t.name)",
                "CREATE INDEX knowledge_name IF NOT EXISTS FOR (k:Knowledge) ON (k.name)",
                "CREATE INDEX softskill_name IF NOT EXISTS FOR (s:SoftSkill) ON (s.name)",
                "CREATE INDEX cert_name IF NOT EXISTS FOR (c:Certification) ON (c.name)"
            ]
            
            for index in indices:
                await session.run(index) 