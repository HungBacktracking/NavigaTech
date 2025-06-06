import os
from typing import List

from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()

ENV: str = ""


class Configs(BaseSettings):
    ENV: str = os.getenv("ENV", "dev")
    API: str = "/api"
    API_V1_STR: str = "/api/v1"
    API_V2_STR: str = "/api/v2"
    PROJECT_NAME: str = "NavigaTech"
    ENV_DATABASE_MAPPER: dict = {
        "prod": "prod",
        "dev": "dev",
        "test": "test",
        "local": "local",
    }
    DB_ENGINE_MAPPER: dict = {
        "postgresql": "postgresql",
        "mysql": "mysql+pymysql",
    }

    PROJECT_ROOT: str = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    DATETIME_FORMAT: str = "%Y-%m-%dT%H:%M:%S"
    DATE_FORMAT: str = "%Y-%m-%d"

    SECRET_KEY: str = os.getenv("SECRET_KEY", "")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 30  # 60 minutes * 24 hours * 30 days = 30 days

    BACKEND_CORS_ORIGINS: List[str] = ["*"]

    DB: str = os.getenv("DB", "postgresql")
    DB_USER: str = os.getenv("DB_USER")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD")
    DB_HOST: str = os.getenv("DB_HOST")
    DB_PORT: str = os.getenv("DB_PORT", "5432")
    DB_ENGINE: str = os.getenv("DB_ENGINE", "postgresql")

    DATABASE_URI_FORMAT: str = "{db_engine}://{user}:{password}@{host}:{port}/{database}"

    DATABASE_URI: str = "{db_engine}://{user}:{password}@{host}:{port}/{database}".format(
        db_engine=DB_ENGINE,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT,
        database=ENV_DATABASE_MAPPER[ENV]
    )

    REPLICA_DB_USER: str = os.getenv("REPLICA_DB_USER", DB_USER)
    REPLICA_DB_PASSWORD: str = os.getenv("REPLICA_DB_PASSWORD", DB_PASSWORD)
    REPLICA_DB_HOST: str = os.getenv("REPLICA_DB_HOST")
    REPLICA_DB_PORT: str = os.getenv("REPLICA_DB_PORT", "5432")
    REPLICA_DB_ENGINE: str = os.getenv("REPLICA_DB_ENGINE", DB_ENGINE)

    REPLICA_DATABASE_URI: str = "{db_engine}://{user}:{password}@{host}:{port}/{database}".format(
        db_engine=REPLICA_DB_ENGINE,
        user=REPLICA_DB_USER,
        password=REPLICA_DB_PASSWORD,
        host=REPLICA_DB_HOST if REPLICA_DB_HOST else DB_HOST,
        port=REPLICA_DB_PORT,
        database=ENV_DATABASE_MAPPER[ENV]
    )

    MONGO_DB_URI: str = os.getenv("MONGO_DB_URI")
    MONGO_DB_NAME: str = os.getenv("MONGO_DB_NAME")

    REDIS_HOST: str = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT: str = os.getenv("REDIS_PORT", "6379")
    REDIS_PASSWORD: str = os.getenv("REDIS_PASSWORD", "")
    REDIS_DB: int = int(os.getenv("REDIS_DB", "0"))
    REDIS_DEFAULT_TIMEOUT: int = int(os.getenv("REDIS_DEFAULT_TIMEOUT", 3600))

    QDRANT_URL: str = os.getenv("QDRANT_URL")
    QDRANT_API_TOKEN: str = os.getenv("QDRANT_API_TOKEN")
    QDRANT_COLLECTION_NAME: str = os.getenv("QDRANT_COLLECTION_NAME", "job_description_2")

    COURSE_DB: str = os.getenv("COURSE_DB", "app/courses_db")

    ELASTICSEARCH_URL: str = os.getenv("ELASTICSEARCH_URL", "http://elasticsearch:9200")

    KAFKA_BOOTSTRAP_SERVERS: str = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
    KAFKA_CONSUMER_GROUP: str = os.getenv("KAFKA_CONSUMER_GROUP", "navigatech-app")

    HF_TOKEN: str = os.getenv("HF_TOKEN")
    GEMINI_MODEL_NAME: str = os.getenv("GEMINI_MODEL_NAME", "gemini-pro")
    GEMINI_TOKEN: str = os.getenv("GEMINI_TOKEN")
    MAX_TOKENS: int = int(os.getenv("MAX_TOKENS", 10240))
    TEMPERATURE: float = float(os.getenv("TEMPERATURE", 0.7))
    EMBEDDING_MODEL_NAME: str = os.getenv("EMBEDDING_MODEL_NAME", "BAAI/bge-large-en-v1.5")
    SCORING_MODEL_NAME: str = os.getenv("SCORING_MODEL_NAME", "all-mpnet-base-v2")

    TOP_K: int = int(os.getenv("TOP_K", 15))
    TOKEN_LIMIT: int = int(os.getenv("TOKEN_LIMIT", 2048))

    COHERE_API_TOKEN: str = os.getenv("COHERE_API_TOKEN")
    
    NEO4J_URI: str = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    NEO4J_USERNAME: str = os.getenv("NEO4J_USERNAME", "neo4j")
    NEO4J_PASSWORD: str = os.getenv("NEO4J_PASSWORD", "password")
    
    AWS_ACCESS_KEY_ID: str = os.getenv("AWS_ACCESS_KEY_ID")
    AWS_SECRET_KEY: str = os.getenv("AWS_SECRET_ACCESS_KEY")
    AWS_REGION: str = os.getenv("AWS_REGION")
    AWS_S3_BUCKET_NAME: str = os.getenv("AWS_S3_BUCKET_NAME")
    AWS_S3_BUCKET_URL: str = os.getenv("AWS_S3_BUCKET_URL")

    PAGE: int = 1
    PAGE_SIZE: int = 20
    ORDERING: str = "-id"


    class Config:
        case_sensitive = True


class TestConfigs(Configs):
    ENV: str = "test"


configs = Configs()

if ENV == "prod":
    pass
elif ENV == "stage":
    pass
elif ENV == "test":
    setting = TestConfigs()
