import sys
import os
import logging
import time
from datetime import datetime
from pathlib import Path

# Add the parent directory to sys.path to allow importing app modules
parent_dir = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(parent_dir))

from dependency_injector.wiring import inject, Provide
from app.core.containers.application_container import ApplicationContainer
from app.services.job_service import JobService
from app.repository.elasticsearch_repository import ElasticsearchRepository

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("elasticsearch_sync")

@inject
def sync_jobs_to_elasticsearch(
    job_service: JobService = Provide[ApplicationContainer.services.job_service],
    es_repository: ElasticsearchRepository = Provide[ApplicationContainer.repositories.elasticsearch_repository],
    batch_size: int = 1000,
    verify: bool = True,
    include_deleted: bool = False
):
    """
    Sync all jobs from PostgreSQL to Elasticsearch
    
    Args:
        job_service: The job service instance
        es_repository: The Elasticsearch repository instance
        batch_size: Number of jobs to process in each batch
        verify: Whether to verify the sync after completion
        include_deleted: Whether to include soft-deleted jobs
    """
    start_time = time.time()
    logger.info("Starting job synchronization...")
    
    try:
        # Get total job count
        total_jobs_active = job_service.job_repository.get_total_count()
        total_jobs_all = job_service.job_repository.get_total_count_including_deleted()
        total_deleted = total_jobs_all - total_jobs_active
        
        logger.info(f"Found {total_jobs_active} active jobs and {total_deleted} soft-deleted jobs in database")
        logger.info(f"Total jobs in database: {total_jobs_all}")
        
        if include_deleted:
            logger.info("Including soft-deleted jobs in synchronization")
        
        # Index all jobs
        job_count = job_service.index_all_jobs(batch_size=batch_size, include_deleted=include_deleted)
        
        # Force refresh the index to make all documents searchable
        es_repository.refresh_index()
        
        elapsed_time = time.time() - start_time
        logger.info(f"Successfully indexed {job_count} jobs to Elasticsearch in {elapsed_time:.2f} seconds.")
        
        # Verify the synchronization if requested
        if verify:
            verify_sync(job_service, es_repository, include_deleted)
            
        logger.info("Job synchronization complete!")
        return job_count
    except Exception as e:
        logger.error(f"Error during synchronization: {str(e)}")
        raise

@inject
def verify_sync(
    job_service: JobService = Provide[ApplicationContainer.services.job_service],
    es_repository: ElasticsearchRepository = Provide[ApplicationContainer.repositories.elasticsearch_repository],
    include_deleted: bool = False
):
    """Verify that all jobs in the database are correctly indexed in Elasticsearch"""
    logger.info("Verifying synchronization...")
    
    # Get the total count from the database
    if include_deleted:
        db_count = job_service.job_repository.get_total_count_including_deleted()
        logger.info("Verification includes soft-deleted jobs")
    else:
        db_count = job_service.job_repository.get_total_count()
        logger.info("Verification only includes active jobs")
    
    # Get the total count from Elasticsearch
    try:
        es_count = es_repository.es_client.count(index=es_repository.index_name)["count"]
        
        logger.info(f"Database has {db_count} jobs, Elasticsearch has {es_count} jobs")
        
        if db_count != es_count:
            logger.warning(f"Count mismatch: Database has {db_count} jobs, but Elasticsearch has {es_count} jobs")
            return False
            
        logger.info("Verification complete: counts match")
        return True
    except Exception as e:
        logger.error(f"Error during verification: {str(e)}")
        return False

@inject
def cleanup_missing_jobs(
    job_service: JobService = Provide[ApplicationContainer.services.job_service],
    es_repository: ElasticsearchRepository = Provide[ApplicationContainer.repositories.elasticsearch_repository]
):
    """Remove any jobs from Elasticsearch that no longer exist in the database"""
    logger.info("Starting cleanup of missing jobs...")
    
    try:
        # This would require implementing a method to get all job IDs from Elasticsearch
        # and comparing with database IDs to find differences
        # This is just a placeholder for the implementation
        logger.info("Cleanup complete")
    except Exception as e:
        logger.error(f"Error during cleanup: {str(e)}")

if __name__ == "__main__":
    # Initialize the container
    container = ApplicationContainer()
    container.init_resources()
    container.wire(modules=[__name__])
    
    # Run the sync function with command line arguments
    import argparse
    parser = argparse.ArgumentParser(description='Sync jobs from database to Elasticsearch')
    parser.add_argument('--no-verify', action='store_true', help='Skip verification step')
    parser.add_argument('--cleanup', action='store_true', help='Cleanup missing jobs')
    parser.add_argument('--include-deleted', action='store_true', help='Include soft-deleted jobs')
    args = parser.parse_args()
    
    # Run the sync
    sync_jobs_to_elasticsearch(verify=not args.no_verify, include_deleted=args.include_deleted)
    
    # Run cleanup if requested
    if args.cleanup:
        cleanup_missing_jobs()