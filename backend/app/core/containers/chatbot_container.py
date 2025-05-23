from dependency_injector import containers, providers

from app.chatbot.chat_engine import ChatEngine
from app.chatbot.small_talk_checker import SmallTalkChecker
from llama_index.core import VectorStoreIndex, load_index_from_storage, StorageContext
from llama_index.vector_stores.qdrant import QdrantVectorStore
from llama_index.core.storage.chat_store import SimpleChatStore



class ChatbotContainer(containers.DeclarativeContainer):
    config = providers.Configuration()
    database = providers.DependenciesContainer()
    AI = providers.DependenciesContainer()

    qdrant_client = database.qdrant_client
    async_qdrant_client = database.async_qdrant_client
    llm = AI.llm_gemini
    embed_model = AI.embed_model

    course_storage = providers.Singleton(
        StorageContext.from_defaults,
        persist_dir=config.COURSE_DB
    )
    course_index = providers.Singleton(
        load_index_from_storage,
        storage_context=course_storage,
        embed_model=embed_model,
    )
    
    # Fix: Use a Factory provider to ensure as_retriever() is called
    course_retriever = providers.Factory(
        lambda idx, top_k: idx.as_retriever(top_k=top_k),
        idx=course_index,
        top_k=15,
    )

    # Vector store components
    vector_store = providers.Singleton(
        QdrantVectorStore,
        client=qdrant_client,
        aclient=async_qdrant_client,
        collection_name=config.QDRANT_COLLECTION_NAME,
        dense_vector_name="text-dense",
        sparse_vector_name="text-sparse",
        enable_hybrid=True,
    )

    # Index components
    index = providers.Singleton(
        VectorStoreIndex.from_vector_store,
        vector_store=vector_store,
        use_async=True,
    )

    # Retriever
    # Fix: Use a Factory provider to ensure as_retriever() is called
    job_retriever = providers.Factory(
        lambda idx, top_k, mode: idx.as_retriever(similarity_top_k=top_k, vector_store_query_mode=mode),
        idx=index,
        top_k=15,
        mode="hybrid",
    )

    # Helper components
    small_talk_checker = providers.Singleton(SmallTalkChecker)
    chat_store = providers.Singleton(SimpleChatStore)

    # Main chat engine
    chat_engine = providers.Factory(
        ChatEngine,
        llm=llm,
        job_retriever=job_retriever,
        course_retriever=course_retriever,
        embedding_model=embed_model,
        chat_store=chat_store,
        checker=small_talk_checker
    )