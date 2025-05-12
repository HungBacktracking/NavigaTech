from dependency_injector import containers, providers
from app.recommendation.job_recommendation import JobRecommendation


class RecommendationContainer(containers.DeclarativeContainer):
    job_recommendation = providers.Singleton(
        JobRecommendation,
        collection_name="job_description"
    ) 