from qdrant_client import QdrantClient, models
from qdrant_client.http.models import Filter, FieldCondition, MatchValue
import cohere
from app.core.config import configs


class JobRecommendation:
    DENSE_MODEL = "BAAI/bge-large-en-v1.5"
    SPARSE_MODEL = "prithivida/Splade_PP_en_v1"

    def __init__(self, collection_name, qdrant_client=None, reranker=None):
        self.collection_name = collection_name
        self.qdrant_client = qdrant_client or QdrantClient(
            url=configs.QDRANT_URL,
            api_key=configs.QDRANT_API_TOKEN,
        )
        self.reranker = reranker or cohere.Client(configs.COHERE_API_TOKEN)

    @staticmethod
    def _build_metadata_filter(fields: dict):
        """Helper to build metadata filters compatible with Qdrant."""
        if not fields:
            return None

        conditions = [
            FieldCondition(
                key=key,
                match=MatchValue(value=value)
            )
            for key, value in fields.items()
        ]
        return Filter(must=conditions)

    def search(self, text: str, metadata_filter: dict = None, top_k: int = 15):
        """Perform hybrid (dense + sparse) search with optional metadata filtering."""

        query_filter = self._build_metadata_filter(metadata_filter)

        search_result = self.qdrant_client.query_points(
            collection_name=self.collection_name,
            query=models.FusionQuery(
                fusion=models.Fusion.RRF
            ),
            prefetch=[
                models.Prefetch(
                    query=models.Document(text=text, model=self.DENSE_MODEL),
                    using="text-dense",
                    limit=top_k
                ),
                models.Prefetch(
                    query=models.Document(text=text, model=self.SPARSE_MODEL),
                    using="text-sparse",
                    limit=top_k
                ),
            ],
            query_filter=query_filter,
            with_payload=True,
            with_vectors=False,
            limit=top_k,
        ).points

        enriched = []
        for pt in search_result:
            payload = pt.payload or {}
            enriched.append({
                "id": pt.id,
                "score": pt.score,
                "text": payload.get("text"),
                **{k: v for k, v in payload.items() if k != "text"}
            })
            # return enriched
        document_list = [{
            "text": point['text'],
            "metadata": {
                "id": point.get("job_id", "id"),
                "from_site": "",
                "job_url": point.get("job_url", "job_url"),
                "logo_url": point.get("logo_url", "company_logo"),
                "company_name": point.get("company", "company"),
                "job_type": point.get("job_type", "job_type"),
                "job_level": point.get("job_level", "job_level"),
                "job_name": point.get("job_title", "title"),
                "date_posted": point.get("date_posted", "date_posted"),
                "job_description": point.get("job_description", "description"),
                "salary": point.get("salary", "salary"),
                "skills": point.get("skills", "qualifications & skills"),

                # "from_site": "",
                # "job_url": point.get("job_url"),
                # "job_name": point.get("job_title"),
                # "job_level": point.get("job_level"),
                # "job_type": point.get("job_type"),
                # "company_name": point.get("company"),
                # "company_type": "",
                # "company_address": point.get("company_address"),
                # "company_description": point.get("company_description"),
                # "skills": point.get("skills"),
                # "location": point.get("location"),
                # "date_posted": point.get("date_posted"),
                # "salary": point.get("salary"),
                # "job_description": point.get("job_description")
            }
        } for point in enriched]

        rerank_results = self.reranker.rerank(
            model="rerank-english-v3.0",
            query=text,
            documents=document_list,
            top_n=top_k,
        )

        final_results = []
        for idx, result in enumerate(rerank_results.results, 1):
            doc = document_list[result.index]
            res = {
                "score": result.relevance_score,
                "text": doc['text'],
                "metadata": doc['metadata']
            }
            final_results.append(res)

        return final_results
