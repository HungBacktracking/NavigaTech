import sys
import os
from pathlib import Path

# Add the parent directory to sys.path to allow importing app modules
parent_dir = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(parent_dir))

from dependency_injector.wiring import inject, Provide
from app.core.containers.application_container import ApplicationContainer
from app.services.job_service import JobService


@inject
def sync_jobs_to_elasticsearch(
    job_service: JobService = Provide[ApplicationContainer.services.job_service]
):
    """Sync all jobs from PostgreSQL to Elasticsearch"""
    print("Starting job synchronization...")
    
    job_count = job_service.index_all_jobs()
    
    print(f"Successfully indexed {job_count} jobs to Elasticsearch.")
    print("Job synchronization complete!")


if __name__ == "__main__":
    # Initialize the container
    container = ApplicationContainer()
    container.init_resources()
    container.wire(modules=[__name__])
    
    # Run the sync function
    sync_jobs_to_elasticsearch() 