import os
import json
import re
import nest_asyncio
from typing import Optional

from dotenv import load_dotenv
from qdrant_client import QdrantClient, AsyncQdrantClient
from llama_index.vector_stores.qdrant import QdrantVectorStore


from llama_index.llms.huggingface import HuggingFaceInferenceAPI
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core import VectorStoreIndex, StorageContext, Settings
from llama_index.core.memory import ChatMemoryBuffer
from llama_index.core.storage.chat_store import SimpleChatStore
from llama_index.core.chat_engine import CondensePlusContextChatEngine, SimpleChatEngine
from llama_index.core.llms import ChatMessage
from llama_index.postprocessor.cohere_rerank import CohereRerank

from small_talk_check import AdvancedRuleBasedSmallTalkChecker

nest_asyncio.apply()


class MultiPipelineChatbot:
    """
    Chatbot with two pipelines:
    1) RAG pipeline using Qdrant + CondensePlusContextChatEngine
    2) Simple chat engine for small talk

    Memory persists to JSON via SimpleChatStore.
    """

    def __init__(
        self,
        env_path: str,
        session_id: str = 'default',
        memory_path: str = 'chat_memory.json',
        token_limit: int = 8000,
        collection_name: str = 'job_collection',
        top_k: int = 15,
        temperature: float = 0.6,
        max_tokens: int = 3500,

    ):
        # Load environment variables
        load_dotenv(env_path)

        # Initialize LLM and embeddings
        self.llm = HuggingFaceInferenceAPI(
            model_name='models/gemini-2.0-flash',
            api_key=os.environ.get('GEMINI_TOKEN'),
            max_tokens=self.max_tokens,
            temperature=self.temperature,
        )
        embedding_model = HuggingFaceEmbedding(
            model_name='BAAI/bge-large-en-v1.5'
        )
        Settings.llm = self.llm
        Settings.embed_model = embedding_model

        # Initialize Qdrant vector store
        q_client = QdrantClient(
            url=os.environ['QDRANT_URL'],
            api_key=os.environ['QDRANT_API_TOKEN'],
        )
        aq_client = AsyncQdrantClient(
            url=os.environ['QDRANT_URL'],
            api_key=os.environ['QDRANT_API_TOKEN'],
        )

        vector_store = QdrantVectorStore(
            client=q_client,
            aclient=aq_client,
            collection_name=self.collection_name,
            dense_vector_name='text-dense',
            sparse_vector_name='text-sparse',
            enable_hybrid=True,
        )
        storage_ctx = StorageContext.from_defaults(vector_store=vector_store)
        index = VectorStoreIndex.from_vector_store(
            vector_store, use_async=True)
        retriever = index.as_retriever(
            similarity_top_k=int(self.top_k),
            vector_store_query_mode='hybrid'
        )

        cohere_reranker = CohereRerank(
            model="rerank-v3.5", api_key=os.environ["COHERE_API_TOKEN"], top_n=self.top_k)

        self.rag_prompt = """
            You are an intelligent assistant specialized in job matching, job discovery, resume analysis, and career guidance. Your primary objective is to help users find relevant job opportunities and assess their fit based on job descriptions and their professional background.
            You have access to:
            - A vector database of job descriptions (retrieved based on contextual relevance)
            - The user's resume or summarized professional experience

            When handling user queries:
            1. **Understand the user's intent** within the context of the conversation.
            2. Use relevant job descriptions and resume content as contextual input to **rephrase or clarify the user’s query** into a standalone, specific question.
            3. If the user asks to find jobs:
            - Return results in **bullet points**
            - Include the **job title**, **brief job summary**, and a **direct job URL**
            4. Respond in **natural, conversational language** suitable for a helpful assistant.

            ### Example Job Response Format:
            - **Job Title**: [Job Title Here] 
            **Company Name**: [Company name here]
            **Summary**: [Short job description here]  
            **URL**: https://vn.indeed.com/viewjob?jk=d077359f1ac32d4a
        """
        self.smalltalk_prompt = os.getenv(
            'SMALLTALK_SYSTEM_PROMPT') or 'You are a helpful assistant.'

        # Setup persistent chat memory
        self.memory_path = memory_path
        self.chat_store = SimpleChatStore()
        # load if exists
        if os.path.exists(memory_path):
            try:
                self.chat_store = SimpleChatStore.from_persist_path(
                    memory_path)
            except Exception:
                pass
        self.chat_memory = ChatMemoryBuffer.from_defaults(
            token_limit=token_limit,
            chat_store=self.chat_store,
            chat_store_key=session_id,
        )

        # Engines
        self.rag_engine = CondensePlusContextChatEngine(
            retriever=retriever,
            llm=self.llm,
            system_prompt=self.rag_prompt,
            node_postprocessors=[cohere_reranker],
            memory=self.chat_memory,
        )
        prefix_messages = [ChatMessage(
            role='system', content=self.smalltalk_prompt)]
        self.smalltalk_engine = SimpleChatEngine(
            llm=self.llm,
            memory=self.chat_memory,
            prefix_messages=prefix_messages,
        )

        # Small talk checker
        self.checker = AdvancedRuleBasedSmallTalkChecker()

    def chat(self, user_input: str) -> str:
        """
        Routes input to small-talk or RAG engine, persists memory.
        """
        if self.checker.is_small_talk(user_input):
            resp = self.smalltalk_engine.chat(user_input)
        else:
            resp = self.rag_engine.chat(user_input)

        self.chat_store.persist(self.memory_path)
        return resp

    def clear_memory(self):
        """Clears both in-memory and persisted chat history."""
        self.chat_memory.reset()
        try:
            os.remove(self.memory_path)
        except OSError:
            pass
