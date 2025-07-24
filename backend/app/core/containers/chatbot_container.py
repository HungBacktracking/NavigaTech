from dependency_injector import containers, providers
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

from app.chatbot.chat_engine import ChatEngine
from app.chatbot.small_talk_checker import SmallTalkChecker
from app.chatbot.graph_retriever import Neo4jGraphRetriever
from app.chatbot.hybrid_retriever import HybridRetriever
from llama_index.core import Settings, VectorStoreIndex, load_index_from_storage, StorageContext
from llama_index.vector_stores.qdrant import QdrantVectorStore
from llama_index.core.storage.chat_store import SimpleChatStore
from llama_index.postprocessor.cohere_rerank import CohereRerank


class ChatbotContainer(containers.DeclarativeContainer):
    config = providers.Configuration()
    database = providers.DependenciesContainer()
    AI = providers.DependenciesContainer()

    qdrant_client = database.qdrant_client
    async_qdrant_client = database.async_qdrant_client
    neo4j_driver = database.neo4j_driver
    llm = AI.llm_gemini
    embed_model = AI.embed_model
    cohere_client = AI.cohere_reranker

    course_storage = providers.Singleton(
        StorageContext.from_defaults,
        persist_dir=config.COURSE_DB
    )
    course_index = providers.Singleton(
        load_index_from_storage,
        storage_context=course_storage,
        embed_model=embed_model,
    )
    
    # Embedding-based course retriever
    course_embedding_retriever = providers.Factory(
        lambda idx, top_k: idx.as_retriever(top_k=top_k),
        idx=course_index,
        top_k=20,
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

    # settings = providers.Singleton(
    #     Settings,
    #     embed_model=AI.embed_model
    # )

    # Index components
    index = providers.Singleton(
        VectorStoreIndex.from_vector_store,
        vector_store=vector_store,
        # settings=settings,
        embed_model=AI.embed_model,
        use_async=True,
    )

    # Embedding-based job retriever
    job_embedding_retriever = providers.Factory(
        lambda idx, top_k, mode: idx.as_retriever(similarity_top_k=top_k, vector_store_query_mode=mode),
        idx=index,
        top_k=20,
        mode="hybrid",
    )

    # Graph retrievers
    job_graph_retriever = providers.Singleton(
        Neo4jGraphRetriever,
        neo4j_driver=neo4j_driver,
        top_k=20
    )
    
    course_graph_retriever = providers.Singleton(
        Neo4jGraphRetriever,
        neo4j_driver=neo4j_driver,
        top_k=20
    )

    # Reranker
    reranker = providers.Singleton(
        CohereRerank,
        api_key=config.COHERE_API_TOKEN,
        top_n=10
    )

    # Hybrid retrievers
    job_retriever = providers.Singleton(
        HybridRetriever,
        embedding_retriever=job_embedding_retriever,
        graph_retriever=job_graph_retriever,
        reranker=reranker,
        embedding_weight=0.6,
        graph_weight=0.4,
        top_k=15
    )
    
    course_retriever = providers.Singleton(
        HybridRetriever,
        embedding_retriever=course_embedding_retriever,
        graph_retriever=course_graph_retriever,
        reranker=reranker,
        embedding_weight=0.6,
        graph_weight=0.4,
        top_k=15
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