from dags.load.job_data_preprocessor import JobDataMapperAndTranslator
from dags.load.qdrant_data_loader import JobDataIngestor
import asyncio
import pandas as pd
from dotenv import load_dotenv
import json
from datetime import datetime


# Load environment variables from .env file (AWS credentials, region, bucket)
load_dotenv("/opt/airflow/utils/.env")



timestamp = datetime.now().strftime("%Y%m%d")


async def load_to_qdrant():
    # Load dữ liệu từ file JSON
    
    with open(f"/opt/airflow/data/clean2/final_{timestamp}.json", "r", encoding="utf-8") as f:
        data = json.load(f)





    data = pd.DataFrame(data)
    selected_columns = [
    "id", "job_url", "company_logo", "company",
    "job_type", "job_level", "title",
    "date_posted", "description", "salary",
    "responsibilities", "qualifications & skills",
    "benefits", "merge_input", "mapped_location",
    "mapped_level", "mapped_job_type"
    ]
    data = data[selected_columns]
    data = JobDataMapperAndTranslator(data).run()
    data=await data
    Ingestor = JobDataIngestor(data, "/opt/airflow/utils/.env", collection_name="job_description_2")
    await Ingestor.run()


def main():
    asyncio.run(load_to_qdrant())