from typing import List, Dict, Any
from neo4j import AsyncSession, AsyncDriver
import asyncio


class GraphIngestionService:
    def __init__(self, neo4j_driver: AsyncDriver):
        """Initialize with a Neo4j AsyncDriver instance."""
        self.driver = neo4j_driver

    async def ingest_jobs(self, job_data: List[Dict[str, Any]]):
        """Ingest a list of jobs into the Neo4j graph."""
        async with self.driver.session() as session:
            for job in job_data:
                job_id = job.get('job_url') or job.get('id')
                if not job_id:
                    continue
                await self._create_job_graph(session, job, job_id)

    async def ingest_courses(self, course_data: List[Dict[str, Any]]):
        """Ingest a list of courses into the Neo4j graph."""
        async with self.driver.session() as session:
            for course in course_data:
                await self._create_course_graph(session, course)

    async def _create_job_graph(
        self,
        session: AsyncSession,
        job: Dict[str, Any],
        job_id: str
    ):
        # Merge Career node by unique id
        await session.run(
            """
            MERGE (c:Career {id: $job_id})
            SET c.title = $title,
                c.url = $url,
                c.location = $location,
                c.job_type = $job_type,
                c.job_level = $job_level,
                c.salary = $salary,
                c.description = $description
            """,
            job_id=job_id,
            title=job.get('title', ''),
            url=job.get('job_url', ''),
            location=job.get('location', ''),
            job_type=job.get('job_type', ''),
            job_level=job.get('job_level', ''),
            salary=job.get('salary', ''),
            description=job.get('description', '')
        )
        # Structured competencies
        for comp_type, items in job.get('competencies', {}).items():
            for item in items:
                await self._create_competency_relationship(
                    session, job_id, comp_type, item, 'job'
                )
        # Company -> Industry relationship
        if company := job.get('company'):
            await session.run(
                """
                MERGE (i:Industry {name: $company})
                MERGE (c:Career {id: $job_id})
                MERGE (c)-[:IN_INDUSTRY]->(i)
                """,
                company=company,
                job_id=job_id
            )

    async def _create_course_graph(
        self,
        session: AsyncSession,
        course: Dict[str, Any]
    ):
        # Merge Course node by unique URL
        url = course.get('url')
        if not url:
            return
        await session.run(
            """
            MERGE (c:Course {url: $url})
            SET c.title = $title,
                c.website = $website,
                c.organization = $organization,
                c.instructor = $instructor,
                c.level = $level,
                c.description = $description
            """,
            url=url,
            title=course.get('title', ''),
            website=course.get('website', ''),
            organization=course.get('organization', ''),
            instructor=course.get('instructor', ''),
            level=course.get('level', ''),
            description=course.get('description', '')
        )
        # Structured competencies
        for comp_type, items in course.get('competencies', {}).items():
            for item in items:
                await self._create_competency_relationship(
                    session, url, comp_type, item, 'course'
                )
        # Additional skills
        for skill in course.get('skills', []):
            await self._create_competency_relationship(
                session, url, 'soft_skills', skill, 'course'
            )
        # Organization -> Course relationship
        if org := course.get('organization'):
            await session.run(
                """
                MERGE (o:Organization {name: $org})
                MERGE (c:Course {url: $url})
                MERGE (o)-[:COLLABORATES_WITH]->(c)
                """,
                org=org,
                url=url
            )

    async def _create_competency_relationship(
        self,
        session: AsyncSession,
        entity_id: str,
        comp_type: str,
        comp_value: str,
        entity_type: str  # 'job' or 'course'
    ):
        # Map types to labels
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
        # Build query
        if entity_type == 'job':
            query = (
                f"""
                MERGE (comp:{comp_label} {{name: $comp_value}})
                MERGE (e:Career {{id: $entity_id}})
                MERGE (e)-[:REQUIRES {{type: $comp_type}}]->(comp)
                """
            )
        else:
            query = (
                f"""
                MERGE (comp:{comp_label} {{name: $comp_value}})
                MERGE (e:Course {{url: $entity_id}})
                MERGE (e)-[:TEACHES {{type: $comp_type}}]->(comp)
                """
            )
        await session.run(
            query,
            entity_id=entity_id,
            comp_value=comp_value,
            comp_type=comp_type
        )

    async def create_indices(self):
        """Create indexes for faster lookup."""
        async with self.driver.session() as session:
            statements = [
                "CREATE INDEX career_id IF NOT EXISTS FOR (c:Career) ON (c.id)",
                "CREATE INDEX career_url IF NOT EXISTS FOR (c:Career) ON (c.url)",
                "CREATE INDEX course_url IF NOT EXISTS FOR (c:Course) ON (c.url)",
                "CREATE INDEX org_name IF NOT EXISTS FOR (o:Organization) ON (o.name)",
                "CREATE INDEX industry_name IF NOT EXISTS FOR (i:Industry) ON (i.name)",
                "CREATE INDEX prog_lang_name IF NOT EXISTS FOR (p:ProgrammingLanguage) ON (p.name)",
                "CREATE INDEX framework_name IF NOT EXISTS FOR (f:Framework) ON (f.name)",
                "CREATE INDEX platform_name IF NOT EXISTS FOR (pl:Platform) ON (pl.name)",
                "CREATE INDEX tool_name IF NOT EXISTS FOR (t:Tool) ON (t.name)",
                "CREATE INDEX knowledge_name IF NOT EXISTS FOR (k:Knowledge) ON (k.name)",
                "CREATE INDEX softskill_name IF NOT EXISTS FOR (s:SoftSkill) ON (s.name)",
                "CREATE INDEX cert_name IF NOT EXISTS FOR (c:Certification) ON (c.name)"
            ]
            for stmt in statements:
                await session.run(stmt)