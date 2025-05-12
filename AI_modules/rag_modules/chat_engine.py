import os
import nest_asyncio
from typing import Optional

from dotenv import load_dotenv
from qdrant_client import QdrantClient, AsyncQdrantClient
from llama_index.vector_stores.qdrant import QdrantVectorStore
from llama_index.core import VectorStoreIndex, Settings, load_index_from_storage, StorageContext
from llama_index.core.memory import ChatMemoryBuffer
from llama_index.core.storage.chat_store import SimpleChatStore
from llama_index.core.chat_engine import (
    CondensePlusContextChatEngine,
    SimpleChatEngine,
)
from llama_index.core.tools import RetrieverTool
from llama_index.core.retrievers import RouterRetriever
from llama_index.core.selectors import LLMSingleSelector
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.postprocessor.cohere_rerank import CohereRerank
from llama_index.core.llms import ChatMessage

from llama_index.llms.gemini import Gemini
from small_talk_check import AdvancedRuleBasedSmallTalkChecker
nest_asyncio.apply()


class MultiPipelineChatbot:
    """
    Chatbot with two RAG pipelines (job & course) plus small talk.
    Preserves chat history across all dialogues via memory buffer.
    Routes queries via RouterQueryEngine.
    """

    def __init__(
        self,
        env_path: str,
        session_id: str = 'default',
        token_limit: int = 20000,
        job_collection: str = 'job_collection',
        course_db_path: str = r'C:\Users\leduc\OneDrive\Desktop\NLP\grab-capstone-project\NavigaTech\AI_modules\rag_modules\courses_db',
        top_k: int = 15,
        temperature: float = 0.6,
        max_tokens: int = 5000,
        memory: Optional[object] = None,
        resume: str = "default"
    ):
        # Load environment variables
        load_dotenv(env_path)
        self.resume = resume
        self.top_k = top_k
        self.course_db_path = course_db_path
        # Initialize LLM & embeddings
        self.llm = Gemini(
            model_name='models/gemini-2.0-flash',
            api_key=os.environ["GEMINI_TOKEN"],
            max_tokens=max_tokens,
            temperature=temperature,
        )
        embedding_model = HuggingFaceEmbedding(
            model_name='BAAI/bge-large-en-v1.5'
        )
        Settings.llm = self.llm
        Settings.embed_model = embedding_model

        # Setup persistent memory
        self.memory = memory
        self.chat_store = SimpleChatStore()
        # load if exists
        if memory:
            try:
                self.chat_store = SimpleChatStore.from_json(
                    memory
                )
            except Exception:
                pass
        self.chat_memory = ChatMemoryBuffer.from_defaults(
            token_limit=token_limit,
            chat_store=self.chat_store,
            chat_store_key=session_id,
        )

        qdrant_url = os.environ["QDRANT_URL"]
        qdrant_api = os.environ["QDRANT_API_TOKEN"]
        # Qdrant clients
        client = QdrantClient(
            url=qdrant_url,
            api_key=qdrant_api,
        )
        aclient = AsyncQdrantClient(
            url=qdrant_url,
            api_key=qdrant_api,
        )

        # Helper to build RAG index and engine
        def build_retriever(collection_name: str):
            store = QdrantVectorStore(
                client=client,
                aclient=aclient,
                collection_name=collection_name,
                dense_vector_name='text-dense',
                sparse_vector_name='text-sparse',
                enable_hybrid=True,
            )
            index = VectorStoreIndex.from_vector_store(store, use_async=True)
            retriever = index.as_retriever(
                similarity_top_k=top_k,
                vector_store_query_mode='hybrid',
            )
            return retriever

        self.job_retriever = build_retriever(job_collection)
        course_storage = StorageContext.from_defaults(
            persist_dir=self.course_db_path)
        course_index = load_index_from_storage(course_storage)
        self.course_retriever = course_index.as_retriever(top_k=self.top_k)

        def build_tool(retriever, tool_name, description):
            tool = RetrieverTool.from_defaults(
                retriever=retriever,
                name=tool_name,
                description=description
            )
            return tool

        job_tool = build_tool(self.job_retriever, tool_name="job retriever tool",
                              description="Useful for retrieving job-related context")
        course_tool = build_tool(self.course_retriever, tool_name="course retriever tool",
                                 description="Useful for retrieving Handles course and learning path queries. context")

        # Build small talk engine
        smalltalk_prompt = os.getenv(
            'SMALLTALK_SYSTEM_PROMPT') or 'You are a helpful assistant.'
        prefix = [ChatMessage(role='system', content=smalltalk_prompt)]
        self.smalltalk_engine = SimpleChatEngine(
            llm=self.llm,
            memory=self.chat_memory,
            prefix_messages=prefix,
        )

        main_retriever = RouterRetriever(
            selector=LLMSingleSelector.from_defaults(llm=self.llm),
            retriever_tools=[
                job_tool,
                course_tool
            ],
        )

        cohere_reranker = CohereRerank(
            model="rerank-v3.5", api_key=os.environ["COHERE_API_TOKEN"], top_n=self.top_k)

        self.rag_prompt = """
            You are an intelligent assistant specializing in job matching, job discovery, resume analysis, and career guidance. Your objective is to help users find relevant job opportunities and assess their fit based on job descriptions and their professional background.

            You have access to:  
            - A vector database of job descriptions and online courses (retrieved based on contextual relevance)  
            - The user's resume or summarized professional experience  

            ### Guidelines for Handling User Queries:

            1. **Understanding Intent:**  
            - Analyze the user's query to determine whether they are seeking job recommendations, course suggestions, or roadmap guidance.

            2. **Contextual Query Rephrasing:**  
            - Use relevant job descriptions and resume content to rephrase or clarify the user’s query as a specific, standalone question.

            3. **Job Recommendations:**  
            - If the query involves job recommendations, respond in **bullet points** with the following format:

            ## Data Engineer

            **Company Name:** Digital Intellect 
            **Summary:** Role Overview: As a Data Engineer, you will collaborate closely with the client’s Data Lead to design, develop, and maintain data architectures that enhance their data platforms....
            **URL:** https://www.vietnamworks.com/data-engineer--1906728-jv?source=searchResults&searchType=2&placement=1906728&sortBy=date

            4. **Course Recommendations or Roadmaps:**  
            - If the query involves courses or roadmaps, respond in **bullet points** with the following format:

            ## {Course Title}

            **Skills:** {Skills Learned}  
            **What You Will Learn:** {What the user will learn here}  
            **Description:** {Course Description}  
            **URL:** {Course URL}

            5. **Response Formatting:**  
            - Ensure all responses are structured in **Markdown format** with appropriate headings for clarity and organization.
            - Job and course Title MUST be heading like this: ## Job Title
        """

        self.context_prompt = f"""
        USER RESUME:
        {self.resume}
        """

        self.rag_engine = CondensePlusContextChatEngine(
            retriever=main_retriever,
            llm=self.llm,
            system_prompt=self.rag_prompt,
            context_prompt=self.context_prompt,
            node_postprocessors=[cohere_reranker],
            memory=self.chat_memory,
        )

        self.checker = AdvancedRuleBasedSmallTalkChecker()

    def chat(self, user_input: str) -> str:
        """
        Routes input to small-talk or RAG engine, persists memory.
        """
        if self.checker.is_small_talk(user_input):
            resp = self.smalltalk_engine.chat(user_input)
        else:
            resp = self.rag_engine.chat(user_input)

        # self.chat_store.persist(self.memory_path)
        return resp.response.replace("\n", "\n\n")

    def persist_memory(self):
        """
        Returning chat memory in JSON format
        """
        return self.chat_store.json()

    def clear_memory(self):
        self.chat_memory.reset()
        try:
            os.remove(self.memory_path)
        except:
            pass
