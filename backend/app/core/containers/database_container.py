from dependency_injector import containers, providers
from app.core.config import configs
from qdrant_client import QdrantClient, AsyncQdrantClient
from app.core.database import Database
from app.core.database_mongo import MongoDB
from app.core.s3_client import S3Client



class DatabaseContainer(containers.DeclarativeContainer):
    config = providers.Configuration()

    # Database
    db = providers.Singleton(
        Database, 
        db_url=config.DATABASE_URI,
        replica_db_url=config.REPLICA_DATABASE_URI
    )
    mongo_db = providers.Singleton(MongoDB, mongo_url=config.MONGO_DB_URI, db_name=config.MONGO_DB_NAME)

    # S3 Client
    s3_client = providers.Singleton(
        S3Client,
        region_name=config.AWS_REGION,
        access_key_id=config.AWS_ACCESS_KEY_ID,
        secret_key=config.AWS_SECRET_KEY
    )

    # Qdrant clients
    qdrant_client = providers.Singleton(
        QdrantClient,
        url=config.QDRANT_URL,
        api_key=config.QDRANT_API_TOKEN,
    )
    async_qdrant_client = providers.Singleton(
        AsyncQdrantClient,
        url=config.QDRANT_URL,
        api_key=config.QDRANT_API_TOKEN,
    )