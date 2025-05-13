from elasticsearch import Elasticsearch
from typing import List, Dict, Any, Optional, Tuple
from uuid import UUID

from app.schema.job_schema import JobSearchRequest


class ElasticsearchRepository:
    def __init__(self, es_client: Elasticsearch):
        self.es_client = es_client
        self.index_name = "jobs"

        self.create_index()
    
    def create_index(self):
        """Create job index with appropriate mappings"""
        if not self.es_client.indices.exists(index=self.index_name):
            mappings = {
                "properties": {
                    "id": {"type": "keyword"},
                    "job_name": {"type": "text", "analyzer": "standard"},
                    "job_level": {"type": "keyword"},
                    "from_site": {"type": "keyword"},
                    "company_name": {"type": "text", "analyzer": "standard"},
                    "company_type": {"type": "keyword"},
                    "job_type": {"type": "keyword"},
                    "skills": {"type": "text", "analyzer": "standard"},
                    "location": {"type": "keyword"},
                    "job_description": {"type": "text", "analyzer": "standard"},
                    "job_requirement": {"type": "text", "analyzer": "standard"},
                    "benefit": {"type": "text", "analyzer": "standard"},
                    "date_posted": {"type": "date"}
                }
            }
            
            self.es_client.indices.create(
                index=self.index_name,
                mappings=mappings
            )

    def search_jobs(self, request: JobSearchRequest) -> Tuple[List[Dict[str, Any]], int]:
        """Search for jobs based on search criteria with pagination"""
        query = {
            "bool": {
                "must": []
            }
        }
        
        # Add search conditions based on request parameters
        query["bool"]["must"].append({
            "multi_match": {
                "query": request.query,
                "fields": ["job_name^3", "job_requirement^2", "skills^2", "location", "company_name", "benefit"],
                "fuzziness": "AUTO"
            }
        })


        if request.roles:
            for role in request.roles:
                query["bool"]["must"].append({
                    "multi_match": {
                        "query": role,
                        "fields": ["job_name^3", "job_requirement"],
                    }
                })

        if request.levels:
            for level in request.levels:
                query["bool"]["must"].append({
                    "multi_match": {
                        "query": level,
                        "fields": ["job_name^3", "job_level^3", "job_requirement"],
                    }
                })

        from_val = (request.page - 1) * request.page_size if request.page > 0 else 0
        
        response = self.es_client.search(
            index=self.index_name,
            query=query,
            sort=[{"date_posted": {"order": "desc"}}],
            from_=from_val,
            size=request.page_size,
            track_total_hits=True,
        )

        hits = [hit["_source"] for hit in response["hits"]["hits"]]
        total = response["hits"]["total"]["value"]

        return hits, total

    def get_job_by_id(self, job_id: UUID) -> Optional[Dict[str, Any]]:
        """Get a job by its ID"""
        try:
            response = self.es_client.get(
                index=self.index_name,
                id=str(job_id)
            )
            return response["_source"]
        except:
            return None
    
    def delete_job(self, job_id: UUID):
        """Delete a job from the index"""
        self.es_client.delete(
            index=self.index_name,
            id=str(job_id)
        )
        
    def index_bulk_jobs(self, jobs: List[Dict[str, Any]]):
        """Index multiple jobs at once"""
        bulk_data = []
        for job in jobs:
            bulk_data.append({"index": {"_index": self.index_name, "_id": str(job.get("id"))}})
            bulk_data.append(job)
        
        if bulk_data:
            self.es_client.bulk(operations=bulk_data, refresh=True) 