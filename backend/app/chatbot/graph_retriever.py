from typing import List, Dict, Any, Optional
from neo4j import AsyncSession
from llama_index.core.schema import NodeWithScore, TextNode, QueryBundle
from llama_index.core.retrievers import BaseRetriever
from llama_index.core.callbacks import CallbackManager
import asyncio


class Neo4jGraphRetriever(BaseRetriever):
    def __init__(
        self,
        neo4j_driver,
        top_k: int = 20,
        callback_manager: Optional[CallbackManager] = None
    ):
        self.driver = neo4j_driver
        self.top_k = top_k
        self._is_initialized = False
        super().__init__(callback_manager=callback_manager)
    
    async def _check_connection(self):
        """Check if Neo4j connection is available"""
        if not self._is_initialized:
            try:
                async with self.driver.session() as session:
                    await session.run("RETURN 1")
                self._is_initialized = True
            except Exception as e:
                print(f"Neo4j connection error: {e}")
                return False
        return True
    
    def _retrieve(self, query_bundle: QueryBundle) -> List[NodeWithScore]:
        """Sync retrieve - runs async method in sync context"""
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # If there's already a running loop, create a task
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(asyncio.run, self._aretrieve(query_bundle))
                    return future.result()
            else:
                return loop.run_until_complete(self._aretrieve(query_bundle))
        except Exception as e:
            print(f"Error in sync retrieve: {e}")
            return []
    
    async def _aretrieve(self, query_bundle: QueryBundle) -> List[NodeWithScore]:
        """Async retrieve from Neo4j graph"""
        # Check connection first
        if not await self._check_connection():
            return []
            
        try:
            query_str = query_bundle.query_str.lower()
            
            # Determine query intent
            if any(word in query_str for word in ['job', 'career', 'position', 'role', 'vacancy']):
                return await self._retrieve_jobs(query_str)
            elif any(word in query_str for word in ['course', 'learn', 'study', 'training', 'education']):
                return await self._retrieve_courses(query_str)
            elif any(word in query_str for word in ['skill', 'competency', 'ability', 'expertise']):
                return await self._retrieve_by_skills(query_str)
            else:
                # Combined search
                jobs = await self._retrieve_jobs(query_str)
                courses = await self._retrieve_courses(query_str)
                return self._merge_results(jobs, courses)
        except Exception as e:
            print(f"Error in graph retrieval: {e}")
            return []
    
    async def _retrieve_jobs(self, query: str) -> List[NodeWithScore]:
        """Retrieve jobs from graph based on query"""
        async with self.driver.session() as session:
            # Extract potential skills from query
            skills = await self._extract_skills_from_query(session, query)
            
            if skills:
                # Search by required skills
                result = await session.run(
                    """
                    MATCH (c:Career)-[r:REQUIRES]->(comp)
                    WHERE comp.name IN $skills
                    WITH c, COUNT(DISTINCT comp) as skill_match
                    ORDER BY skill_match DESC
                    LIMIT $limit
                    MATCH (c)-[:IN_INDUSTRY]->(i:Industry)
                    OPTIONAL MATCH (c)-[:REQUIRES]->(all_comp)
                    WITH c, i, COLLECT(DISTINCT all_comp.name) as required_skills
                    RETURN c.id as id, c.title as title, c.description as description,
                           c.url as url, c.location as location, c.salary as salary,
                           i.name as company, required_skills,
                           'job' as type
                    """,
                    skills=skills,
                    limit=self.top_k
                )
            else:
                # Fallback to text search
                result = await session.run(
                    """
                    MATCH (c:Career)
                    WHERE toLower(c.title) CONTAINS toLower($query)
                       OR toLower(c.description) CONTAINS toLower($query)
                    OPTIONAL MATCH (c)-[:IN_INDUSTRY]->(i:Industry)
                    OPTIONAL MATCH (c)-[:REQUIRES]->(comp)
                    WITH c, i, COLLECT(DISTINCT comp.name) as required_skills
                    RETURN c.id as id, c.title as title, c.description as description,
                           c.url as url, c.location as location, c.salary as salary,
                           i.name as company, required_skills,
                           'job' as type
                    LIMIT $limit
                    """,
                    query=query,
                    limit=self.top_k
                )
            
            nodes = []
            async for record in result:
                text = self._format_job_text(record)
                node = TextNode(
                    text=text,
                    metadata={
                        'id': record['id'],
                        'title': record['title'],
                        'url': record['url'],
                        'type': 'job',
                        'company': record['company'],
                        'required_skills': record['required_skills']
                    }
                )
                nodes.append(NodeWithScore(node=node, score=1.0))
            
            return nodes
    
    async def _retrieve_courses(self, query: str) -> List[NodeWithScore]:
        """Retrieve courses from graph based on query"""
        async with self.driver.session() as session:
            # Extract potential skills from query
            skills = await self._extract_skills_from_query(session, query)
            
            if skills:
                # Search by taught skills
                result = await session.run(
                    """
                    MATCH (c:Course)-[r:TEACHES]->(comp)
                    WHERE comp.name IN $skills
                    WITH c, COUNT(DISTINCT comp) as skill_match
                    ORDER BY skill_match DESC
                    LIMIT $limit
                    OPTIONAL MATCH (c)<-[:COLLABORATES_WITH]-(o:Organization)
                    OPTIONAL MATCH (c)-[:TEACHES]->(all_comp)
                    WITH c, o, COLLECT(DISTINCT all_comp.name) as taught_skills
                    RETURN c.title as title, c.description as description,
                           c.url as url, c.level as level, c.website as website,
                           o.name as organization, taught_skills,
                           'course' as type
                    """,
                    skills=skills,
                    limit=self.top_k
                )
            else:
                # Fallback to text search
                result = await session.run(
                    """
                    MATCH (c:Course)
                    WHERE toLower(c.title) CONTAINS toLower($query)
                       OR toLower(c.description) CONTAINS toLower($query)
                    OPTIONAL MATCH (c)<-[:COLLABORATES_WITH]-(o:Organization)
                    OPTIONAL MATCH (c)-[:TEACHES]->(comp)
                    WITH c, o, COLLECT(DISTINCT comp.name) as taught_skills
                    RETURN c.title as title, c.description as description,
                           c.url as url, c.level as level, c.website as website,
                           o.name as organization, taught_skills,
                           'course' as type
                    LIMIT $limit
                    """,
                    query=query,
                    limit=self.top_k
                )
            
            nodes = []
            async for record in result:
                text = self._format_course_text(record)
                node = TextNode(
                    text=text,
                    metadata={
                        'title': record['title'],
                        'url': record['url'],
                        'type': 'course',
                        'organization': record['organization'],
                        'taught_skills': record['taught_skills']
                    }
                )
                nodes.append(NodeWithScore(node=node, score=1.0))
            
            return nodes
    
    async def _retrieve_by_skills(self, query: str) -> List[NodeWithScore]:
        """Retrieve both jobs and courses based on skills"""
        async with self.driver.session() as session:
            # Find paths between skills and opportunities
            result = await session.run(
                """
                // Find jobs that require skills matching the query
                MATCH (c:Career)-[:REQUIRES]->(skill)
                WHERE toLower(skill.name) CONTAINS toLower($query)
                WITH c, COLLECT(DISTINCT skill.name) as matching_skills, 'job' as type
                LIMIT $half_limit
                
                UNION
                
                // Find courses that teach skills matching the query
                MATCH (course:Course)-[:TEACHES]->(skill)
                WHERE toLower(skill.name) CONTAINS toLower($query)
                WITH course as c, COLLECT(DISTINCT skill.name) as matching_skills, 'course' as type
                LIMIT $half_limit
                
                RETURN c, matching_skills, type
                """,
                query=query,
                half_limit=self.top_k // 2
            )
            
            nodes = []
            async for record in result:
                entity = record['c']
                if record['type'] == 'job':
                    text = f"Job: {entity.get('title', '')}\n"
                    text += f"Skills matched: {', '.join(record['matching_skills'])}\n"
                    text += f"Description: {entity.get('description', '')[:200]}..."
                else:
                    text = f"Course: {entity.get('title', '')}\n"
                    text += f"Skills taught: {', '.join(record['matching_skills'])}\n"
                    text += f"Description: {entity.get('description', '')[:200]}..."
                
                node = TextNode(
                    text=text,
                    metadata={
                        'type': record['type'],
                        'matching_skills': record['matching_skills']
                    }
                )
                nodes.append(NodeWithScore(node=node, score=1.0))
            
            return nodes
    
    async def _extract_skills_from_query(self, session: AsyncSession, query: str) -> List[str]:
        """Extract known skills from query by matching against graph"""
        try:
            # Sanitize query words to prevent injection
            query_words = [word.strip().lower() for word in query.split() if word.strip()]
            
            result = await session.run(
                """
                MATCH (n)
                WHERE (n:ProgrammingLanguage OR n:Framework OR n:Platform 
                   OR n:Tool OR n:Knowledge OR n:SoftSkill OR n:Certification)
                AND toLower(n.name) IN $query_words
                RETURN DISTINCT n.name as skill
                """,
                query_words=query_words
            )
            
            skills = []
            async for record in result:
                skills.append(record['skill'])
            
            return skills
        except Exception as e:
            print(f"Error extracting skills: {e}")
            return []
    
    def _format_job_text(self, record: Dict[str, Any]) -> str:
        """Format job record into text"""
        text = f"Job Title: {record.get('title', 'N/A')}\n"
        text += f"Company: {record.get('company', 'N/A')}\n"
        text += f"Location: {record.get('location', 'N/A')}\n"
        text += f"Salary: {record.get('salary', 'N/A')}\n"
        if record.get('required_skills'):
            # Safely handle skills list
            skills = record['required_skills'][:10] if isinstance(record['required_skills'], list) else []
            text += f"Required Skills: {', '.join(str(s) for s in skills)}\n"
        description = record.get('description', '')
        text += f"Description: {description[:300] if description else 'N/A'}...\n"
        text += f"URL: {record.get('url', '')}"
        return text
    
    def _format_course_text(self, record: Dict[str, Any]) -> str:
        """Format course record into text"""
        text = f"Course Title: {record.get('title', 'N/A')}\n"
        text += f"Organization: {record.get('organization', 'N/A')}\n"
        text += f"Level: {record.get('level', 'N/A')}\n"
        text += f"Website: {record.get('website', 'N/A')}\n"
        if record.get('taught_skills'):
            # Safely handle skills list
            skills = record['taught_skills'][:10] if isinstance(record['taught_skills'], list) else []
            text += f"Skills Taught: {', '.join(str(s) for s in skills)}\n"
        description = record.get('description', '')
        text += f"Description: {description[:300] if description else 'N/A'}...\n"
        text += f"URL: {record.get('url', '')}"
        return text
    
    def _merge_results(self, jobs: List[NodeWithScore], courses: List[NodeWithScore]) -> List[NodeWithScore]:
        """Merge and rank results from different sources"""
        all_results = jobs + courses
        # Sort by score if needed
        all_results.sort(key=lambda x: x.score, reverse=True)
        return all_results[:self.top_k] 