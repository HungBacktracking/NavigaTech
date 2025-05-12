from dependency_injector import containers, providers
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.postprocessor.cohere_rerank import CohereRerank
import google.generativeai as genai
from llama_index.llms.huggingface_api import HuggingFaceInferenceAPI




def create_llm_model(api_key: str, model_name: str = "gemini-2.0-flash"):
    genai.configure(api_key=api_key)

    return genai.GenerativeModel(model_name)


class AIContainer(containers.DeclarativeContainer):
    config = providers.Configuration()

    llm_model = providers.Singleton(
        create_llm_model,
        api_key=config.GEMINI_TOKEN,
        model_name=config.GEMINI_MODEL_NAME,
    )

    llm_huggingface = providers.Singleton(
        HuggingFaceInferenceAPI,
        model_name=config.GEMINI_MODEL_NAME,
        api_key=config.GEMINI_TOKEN,
        max_tokens=config.MAX_TOKENS,
        temperature=config.TEMPERATURE,
    )

    embed_model = providers.Singleton(
        HuggingFaceEmbedding,
        model_name=config.EMBEDDING_MODEL_NAME
    )

    cohere_reranker = providers.Singleton(
        CohereRerank,
        model="rerank-v3.5",
        api_key=config.COHERE_API_TOKEN,
        top_n=config.TOP_K,
    )