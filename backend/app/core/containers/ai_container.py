import cohere
from dependency_injector import containers, providers
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
import google.generativeai as genai
from llama_index.llms.huggingface_api import HuggingFaceInferenceAPI
from llama_index.llms.gemini import Gemini
from sentence_transformers import SentenceTransformer


def create_llm_model(api_key: str, model_name: str = "gemini-2.0-flash"):
    genai.configure(api_key=api_key)

    return genai.GenerativeModel(model_name)


class AIContainer(containers.DeclarativeContainer):
    config = providers.Configuration()

    scoring_model = providers.Singleton(
        SentenceTransformer,
        config.SCORING_MODEL_NAME
    )

    llm_model = providers.Singleton(
        create_llm_model,
        api_key=config.GEMINI_TOKEN,
        model_name=config.GEMINI_MODEL_NAME,
    )

    llm_gemini = providers.Singleton(
        Gemini,
        model_name='models/gemini-2.0-flash',
        api_key=config.GEMINI_TOKEN,
        max_tokens=config.MAX_TOKENS,
        temperature=config.TEMPERATURE
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
        cohere.Client,
        api_key=config.COHERE_API_TOKEN
    )