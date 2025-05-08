import os
import json
import pandas as pd
from dotenv import load_dotenv
from qdrant_client import QdrantClient, models
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from job_data_preprocessor import JobDataMapperAndTranslator
from tqdm import tqdm
import asyncio


class JobDataIngestor:
    def __init__(self, json_path, env_path, collection_name):
        load_dotenv(env_path)

        self.json_path = json_path
        self.collection_name = collection_name or "job_description"
        self.dense_vector_name = "text-dense"
        self.sparse_vector_name = "text-sparse"
        self.dense_model_name = "BAAI/bge-large-en-v1.5"
        self.sparse_model_name = "prithivida/Splade_PP_en_v1"

        self.embed_model = HuggingFaceEmbedding(
            model_name=self.dense_model_name)
        from llama_index.core import Settings
        Settings.embed_model = self.embed_model

        self.qdrant_client = QdrantClient(
            url=os.environ["QDRANT_URL"],
            api_key=os.environ["QDRANT_API_TOKEN"],
        )

        self.df = None
        self.documents = []
        self.metadata = []

    def load_json_to_dataframe(self):
        with open(self.json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.df = pd.DataFrame(data)

    async def preprocess_data(self):
        mapper = JobDataMapperAndTranslator(self.df)
        self.df = await mapper.run()

    def reset_qdrant_collection(self):
        if self.qdrant_client.collection_exists(self.collection_name):
            self.qdrant_client.delete_collection(
                collection_name=self.collection_name)

        self.qdrant_client.create_collection(
            collection_name=self.collection_name,
            vectors_config={
                self.dense_vector_name: models.VectorParams(
                    size=self.qdrant_client.get_embedding_size(
                        self.dense_model_name),
                    distance=models.Distance.COSINE,
                )
            },
            sparse_vectors_config={
                self.sparse_vector_name: models.SparseVectorParams()
            },
        )

    def build_documents(self):
        for _, row in self.df.iterrows():
            meta = {
                "job_id": row["id"],
                "job_url": row["job_url"],
                "logo_url": row["company_logo"],
                "company": row["company"],
                "job_type": row["job_type"],
                "job_level": row["job_level"],
                "job_title": row["title"],
                "date_posted": row["date_posted"],
                "job_description": row["description"],
                "salary": row["salary"],
                "job_requirement": row["responsibilities"],
                "skills": row["qualifications & skills"],
                "benefit": row["benefit"],


                "text": row["merge_input"],
                "qdrant_location": row["mapped_location"],
                "qdrant_level": row["mapped_level"],
                "qdrant_job_type": row["mapped_job_type"],
            }

            dense_doc = models.Document(
                text=row["merge_input"], model=self.dense_model_name)
            sparse_doc = models.Document(
                text=row["merge_input"], model=self.sparse_model_name)

            self.documents.append({
                self.dense_vector_name: dense_doc,
                self.sparse_vector_name: sparse_doc,
            })
            self.metadata.append(meta)

    def upload_to_qdrant(self):
        self.qdrant_client.upload_collection(
            collection_name=self.collection_name,
            vectors=self.documents,
            payload=self.metadata,
            parallel=4,
            ids=tqdm(range(len(self.documents)))
        )

    async def run(self):
        self.load_json_to_dataframe()
        await self.preprocess_data()
        self.reset_qdrant_collection()
        self.build_documents()
        self.upload_to_qdrant()


# if __name__ == "__main__":
#     json_path = r"C:\Users\leduc\OneDrive\Desktop\NLP\grab-capstone-project\NavigaTech\AI_modules\data\rag_data\sample.json"
#     env_path = r"C:\Users\leduc\OneDrive\Desktop\NLP\grab-capstone-project\NavigaTech\AI_modules\.env"

#     ingestor = JobDataIngestor(json_path, env_path, collection_name="test")
#     asyncio.run(ingestor.run())
