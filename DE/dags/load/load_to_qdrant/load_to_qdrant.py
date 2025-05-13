from job_data_preprocessor import JobDataMapperAndTranslator
from qdrant_data_loader import JobDataIngestor
import asyncio
import pandas as pd
from dotenv import load_dotenv
import json
from datetime import datetime



# Load environment variables from .env file (AWS credentials, region, bucket)
load_dotenv("/opt/airflow/utils/.env")



timestamp = datetime.now().strftime("%Y%m%d")

# def load_jobs_from_s3(key):
#     try:
#         logger.info(f"⬇Downloading s3://{bucket_name}/{key}")
#         response = s3.get_object(Bucket=bucket_name, Key=key)
#         content = response['Body'].read().decode('utf-8')
#         data = json.loads(content)
#         return data if isinstance(data, list) else [data]
#     except s3.exceptions.NoSuchKey:
#         logger.warning(f"s3://{bucket_name}/{key} does not exist. Skipping.")
#         return []
#     except json.JSONDecodeError:
#         logger.error(f"Failed to decode JSON from s3://{bucket_name}/{key}")
#         return []
#     except Exception as e:
#         logger.error(f"Failed to load s3://{bucket_name}/{key} - {e}")
#         return []


async def load_to_qdrant():
    # Load dữ liệu từ file JSON
    
    with open(f"/opt/airflow/data/clean2/final_{timestamp}.json", "r", encoding="utf-8") as f:
        data = json.load(f)





    data = pd.DataFrame(data)
    print(data.columns)
    selected_columns = [
    "id", "job_url", "company_logo", "company",
    "job_type", "job_level", "title",
    "date_posted", "description", "salary",
    "responsibilities", "qualifications & skills",
    "benefits", "merge_input", "mapped_location",
    "mapped_level", "mapped_job_type", "location"
    ]
    data = JobDataMapperAndTranslator(data).run()
    data=await data
    data = data[selected_columns]
    Ingestor = JobDataIngestor(data, "/opt/airflow/utils/.env", collection_name="job_description_2")
    await Ingestor.run()


def main():
    asyncio.run(load_to_qdrant())

if __name__ == "__main__":
    main()