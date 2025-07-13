import asyncio
import json
import os
import sys
import boto3

from llama_index.llms.gemini import Gemini
from neo4j import AsyncGraphDatabase
from pathlib import Path

# Add the backend directory to path
sys.path.append(str(Path(__file__).parent))

from app.services.graph_ingestion_service import GraphIngestionService


async def ingest_data():
    """Ingest job and course data into Neo4j"""
    
    # Get services
    neo4j_driver =AsyncGraphDatabase.driver(
        uri=os.getenv("NEO4J_URI"),
        auth=(os.getenv("NEO4J_USERNAME"), os.getenv("NEO4J_PASSWORD")),
        max_connection_pool_size=50,
    )
    llm = Gemini(
        model_name='models/gemini-2.0-flash',
        api_key=os.getenv("GEMINI_TOKEN"),
        max_tokens=1000,
        temperature=0.7
    )

    s3 = boto3.client(
        's3',
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_KEY"),
        region_name=os.getenv("AWS_REGION")
    )
    bucket_name = os.getenv('AWS_S3_BUCKET_NAME')
    
    ingestion_service = GraphIngestionService(neo4j_driver)
    
    # Create indices first
    print("Creating Neo4j indices...")
    await ingestion_service.create_indices()
    print("Indices created successfully.")
    
    # Load job data
    print("\nLoading job data...")
    job_response = s3.get_object(Bucket=bucket_name, Key='data/job_data.json')
    job_data = json.loads(job_response['Body'].read())
    
    if isinstance(job_data, dict):
        job_data = [job_data]
    
    print(f"Ingesting {len(job_data)} jobs...")
    await ingestion_service.ingest_jobs(job_data)
    print("Jobs ingested successfully.")
    
    # Load course data
    print("\nLoading course data...")
    course_response = s3.get_object(Bucket=bucket_name, Key='data/course_data.json')
    course_data = json.loads(course_response['Body'].read())
    
    if isinstance(course_data, dict):
        course_data = [course_data]
    
    print(f"Ingesting {len(course_data)} courses...")
    await ingestion_service.ingest_courses(course_data)
    print("Courses ingested successfully.")
    
    # Close driver
    await neo4j_driver.close()
    
    print("\nData ingestion completed!")


if __name__ == "__main__":
    asyncio.run(ingest_data()) 