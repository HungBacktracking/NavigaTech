from dependency_injector import containers, providers
from app.recommendation.job_recommendation import JobRecommendation


class RecommendationContainer(containers.DeclarativeContainer):
    AI = providers.DependenciesContainer()
    database = providers.DependenciesContainer()

    qdrant_client = database.qdrant_client
    reranker = AI.cohere_reranker

    job_recommendation = providers.Singleton(
        JobRecommendation,
        collection_name="job_description_2",
        qdrant_client=qdrant_client,
        reranker=reranker,
    ) 