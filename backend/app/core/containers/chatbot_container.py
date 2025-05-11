from dependency_injector import containers, providers

from app.chatbot.chat_engine import ChatEngine
from app.chatbot.prompt import RAGPrompt
from app.chatbot.small_talk_checker import SmallTalkChecker
from app.core.config import configs
from llama_index.core import VectorStoreIndex
from llama_index.vector_stores.qdrant import QdrantVectorStore
from llama_index.core.storage.chat_store import SimpleChatStore


class ChatbotContainer(containers.DeclarativeContainer):
    config = providers.Configuration()
    database = providers.DependenciesContainer()
    AI = providers.DependenciesContainer()

    mongo_db = database.mongo_db
    qdrant_client = database.qdrant_client
    async_qdrant_client = database.async_qdrant_client

    llm = AI.llm_model
    embed_model = AI.embed_model

    vector_store = providers.Singleton(
        QdrantVectorStore,
        client=qdrant_client,
        aclient=async_qdrant_client,
        collection_name=config.QDRANT_COLLECTION_NAME,
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
        similarity_top_k=10,
        vector_store_query_mode="hybrid",
    )

    # Reranker, prompt, chat store…
    cohere_reranker = AI.cohere_reranker
    small_talk_checker = providers.Singleton(SmallTalkChecker)
    rag_prompt = providers.Singleton(RAGPrompt)
    chat_store = providers.Singleton(SimpleChatStore)

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