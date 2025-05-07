from dependency_injector import containers, providers

from app.chatbot.chat_engine import ChatEngine
from app.chatbot.prompt import RAGPrompt
from app.chatbot.small_talk_checker import SmallTalkChecker
from app.core.config import configs

from llama_index.llms.huggingface_api import HuggingFaceInferenceAPI
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core import VectorStoreIndex
from llama_index.postprocessor.cohere_rerank import CohereRerank
from qdrant_client import QdrantClient, AsyncQdrantClient
from llama_index.vector_stores.qdrant import QdrantVectorStore
from llama_index.core.storage.chat_store import SimpleChatStore

from app.services.chatbot_service import ChatbotService


class ChatbotContainer(containers.DeclarativeContainer):

    # LLM + Embedding
    llm = providers.Singleton(
        HuggingFaceInferenceAPI,
        model_name=configs.GEMINI_MODEL_NAME,
        api_key=configs.GEMINI_TOKEN,
        max_tokens=configs.MAX_TOKENS,
        temperature=configs.TEMPERATURE,
    )
    embed_model = providers.Singleton(HuggingFaceEmbedding, model_name=configs.EMBEDDING_MODEL_NAME)

    # Qdrant clients
    qdrant_client = providers.Singleton(
        QdrantClient,
        url=configs.QDRANT_URL,
        api_key=configs.QDRANT_API_TOKEN,
    )
    async_qdrant_client = providers.Singleton(
        AsyncQdrantClient,
        url=configs.QDRANT_URL,
        api_key=configs.QDRANT_API_TOKEN,
    )

    # Vector store + index + retriever
    vector_store = providers.Singleton(
        QdrantVectorStore,
        client=qdrant_client,
        aclient=async_qdrant_client,
        collection_name=configs.QDRANT_COLLECTION_NAME,
        dense_vector_name="text-dense",
        sparse_vector_name="text-sparse",
        enable_hybrid=True,
    )
    index = providers.Singleton(
        VectorStoreIndex.from_vector_store,
        vector_store=vector_store,
        use_async=True,
    )
    retriever = providers.Singleton(
        index.provided.as_retriever,
        similarity_top_k=configs.TOP_K,
        vector_store_query_mode="hybrid",
    )

    chat_store = SimpleChatStore()

    # Reranker
    cohere_reranker = providers.Singleton(
        CohereRerank,
        model="rerank-v3.5",
        api_key=configs.COHERE_API_TOKEN,
        top_n=configs.TOP_K,
    )

    small_talk_checker = providers.Singleton(SmallTalkChecker)
    rag_prompt = RAGPrompt()

    chat_engine = providers.Singleton(
        ChatEngine,
        llm=llm,
        retriever=retriever,
        embed_model=embed_model,
        reranker=cohere_reranker,
        chat_store=chat_store,
        small_talk_checker=small_talk_checker,
        rag_prompt=rag_prompt,
        token_limit=configs.TOKEN_LIMIT,
        top_k=configs.TOP_K,
        temperature=configs.TEMPERATURE,
        max_tokens=configs.MAX_TOKENS
    )


    chatbot_service = providers.Factory(ChatbotService,)
