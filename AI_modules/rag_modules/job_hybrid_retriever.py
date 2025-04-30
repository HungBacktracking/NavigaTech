from qdrant_client import QdrantClient, models
from qdrant_client.http.models import Filter, FieldCondition, MatchValue
import cohere
import os
from dotenv import load_dotenv

load_dotenv(
    r"C:\Users\leduc\OneDrive\Desktop\NLP\grab-capstone-project\NavigaTech\AI_modules\.env")


class HybridRetriever:
    DENSE_MODEL = "BAAI/bge-large-en-v1.5"
    SPARSE_MODEL = "prithivida/Splade_PP_en_v1"

    def __init__(self, collection_name, client=None, reranker=None):
        self.collection_name = collection_name
        self.qdrant_client = client or QdrantClient(
            url=os.environ["QDRANT_URL"],
            api_key=os.environ["QDRANT_API_TOKEN"],
        )
        self.reranker = reranker or cohere.Client(
            os.environ["COHERE_API_TOKEN"])

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

    def search(self, text: str, metadata_filter: dict = None, top_k: int = 5):
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

        document_list = [{
            "text": point['text'],
            "metadata": {
                "level": point.get("level"),
                "title": point.get("title"),
                "company": point.get("company"),
                "link": point.get("link"),
                "job_type": point.get("job_type"),
                "location": point.get("location"),
                "keyword": point.get("keyword"),
                "salary": point.get("salary"),
                "description": point.get("description")
            }
        } for point in enriched]

        rerank_results = self.reranker.rerank(
            model="rerank-english-v3.0",
            query=text,
            documents=document_list,
            top_n=5,
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
