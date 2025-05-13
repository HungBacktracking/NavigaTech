from elasticsearch import Elasticsearch, helpers
from typing import List, Dict, Any, Optional, Tuple
from uuid import UUID
import logging

from app.schema.job_schema import JobSearchRequest


class ElasticsearchRepository:
    def __init__(self, es_client: Elasticsearch):
        self.es_client = es_client
        self.index_name = "jobs"
        self.logger = logging.getLogger(__name__)

        self.create_index()
    
    def create_index(self):
        try:
            if not self.es_client.indices.exists(index=self.index_name):
                mappings = {
                    "properties": {
                        "id": {"type": "keyword"},
                        "job_name": {"type": "text", "analyzer": "standard", "fields": {"keyword": {"type": "keyword"}}},
                        "job_level": {"type": "keyword"},
                        "from_site": {"type": "keyword"},
                        "company_name": {"type": "text", "analyzer": "standard", "fields": {"keyword": {"type": "keyword"}}},
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
                
                settings = {
                    "analysis": {
                        "analyzer": {
                            "standard": {
                                "type": "standard",
                                "max_token_length": 100
                            }
                        }
                    },
                    "index": {
                        "number_of_shards": 1,
                        "number_of_replicas": 1,
                        "refresh_interval": "1s"
                    }
                }
                
                self.es_client.indices.create(
                    index=self.index_name,
                    mappings=mappings,
                    settings=settings
                )
        except Exception as e:
            self.logger.error(f"Error creating Elasticsearch index: {str(e)}")

    def search_jobs(self, request: JobSearchRequest) -> Tuple[List[Dict[str, Any]], int]:
        query = {
            "bool": {
                "must": [],
                "should": []
            }
        }

        if request.query:
            query["bool"]["must"].append({
                "multi_match": {
                    "query": request.query,
                    "fields": ["job_name^3", "job_requirement^2", "skills^2", "location", "company_name", "benefit", "job_description"],
                    "fuzziness": "AUTO",
                    "operator": "or",
                    "minimum_should_match": "70%"
                }
            })

            query["bool"]["should"].append({
                "match_phrase": {
                    "job_name": {
                        "query": request.query,
                        "boost": 5
                    }
                }
            })
            
            query["bool"]["should"].append({
                "match_phrase": {
                    "skills": {
                        "query": request.query,
                        "boost": 4
                    }
                }
            })


        if request.roles:
            role_queries = []
            for role in request.roles:
                role_queries.append({
                    "multi_match": {
                        "query": role,
                        "fields": ["job_name^3", "job_requirement", "job_description"],
                        "type": "phrase_prefix"
                    }
                })
            query["bool"]["must"].append({"bool": {"should": role_queries, "minimum_should_match": 1}})

        if request.levels:
            level_queries = []
            for level in request.levels:
                level_queries.append({
                    "multi_match": {
                        "query": level,
                        "fields": ["job_name^3", "job_level^3", "job_requirement"],
                        "type": "phrase_prefix"
                    }
                })
            query["bool"]["must"].append({"bool": {"should": level_queries, "minimum_should_match": 1}})

        from_val = (request.page - 1) * request.page_size if request.page > 0 else 0
        
        try:
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
        except Exception as e:
            self.logger.error(f"Error searching jobs: {str(e)}")
            return [], 0

    def get_job_by_id(self, job_id: UUID) -> Optional[Dict[str, Any]]:
        try:
            response = self.es_client.get(
                index=self.index_name,
                id=str(job_id)
            )
            return response["_source"]
        except Exception as e:
            self.logger.error(f"Error getting job {job_id}: {str(e)}")
            return None
    
    def delete_job(self, job_id: UUID):
        try:
            self.es_client.delete(
                index=self.index_name,
                id=str(job_id)
            )
        except Exception as e:
            self.logger.error(f"Error deleting job {job_id}: {str(e)}")
        
    def index_bulk_jobs(self, jobs: List[Dict[str, Any]]):
        if not jobs:
            return
            
        try:
            actions = []
            for job in jobs:
                job_id = str(job.get("id"))
                if not job_id:
                    continue

                prepared_job = {k: v for k, v in job.items() if v is not None}

                if "date_posted" in prepared_job and prepared_job["date_posted"] is not None:
                    if not isinstance(prepared_job["date_posted"], str):
                        prepared_job["date_posted"] = prepared_job["date_posted"].isoformat()
                
                actions.append({
                    "_op_type": "index",
                    "_index": self.index_name,
                    "_id": job_id,
                    "_source": prepared_job
                })
            
            if actions:
                success, failed = helpers.bulk(
                    self.es_client, 
                    actions, 
                    refresh=True,
                    stats_only=True,
                    chunk_size=500,
                    max_retries=3
                )
                self.logger.info(f"Bulk indexing complete: {success} successful, {failed} failed")
        except Exception as e:
            self.logger.error(f"Error bulk indexing jobs: {str(e)}")
            raise
            
    def refresh_index(self):
        try:
            self.es_client.indices.refresh(index=self.index_name)
        except Exception as e:
            self.logger.error(f"Error refreshing index: {str(e)}") 