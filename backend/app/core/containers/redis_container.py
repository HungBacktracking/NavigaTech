from dependency_injector import containers, providers
from app.core.redis_client import RedisClient


class RedisContainer(containers.DeclarativeContainer):
    config = providers.Configuration()
    
    redis_client = providers.Singleton(
        RedisClient,
        host=config.REDIS_HOST,
        port=config.REDIS_PORT,
        password=config.REDIS_PASSWORD if config.REDIS_PASSWORD else None,
        db=config.REDIS_DB,
        default_timeout=config.REDIS_DEFAULT_TIMEOUT,
    ) 