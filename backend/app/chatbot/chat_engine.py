from llama_index.llms.huggingface_api import HuggingFaceInferenceAPI
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core import VectorStoreIndex, StorageContext, Settings
from llama_index.core.memory import ChatMemoryBuffer
from llama_index.core.llms import ChatMessage
from llama_index.postprocessor.cohere_rerank import CohereRerank


from llama_index.core.chat_engine import CondensePlusContextChatEngine, SimpleChatEngine

from app.chatbot.prompt import RAGPrompt
from llama_index.core.storage.chat_store import SimpleChatStore

from app.chatbot.small_talk_checker import SmallTalkChecker


class ChatEngine:
    """
    Chatbot with two pipelines:
    1) RAG pipeline using Qdrant + CondensePlusContextChatEngine
    2) Simple chat engine for small talk

    Memory persists to JSON via SimpleChatStore.
    """

    def __init__(
        self,
        llm: HuggingFaceInferenceAPI,
        retriever: VectorStoreIndex.as_retriever,
        embed_model: HuggingFaceEmbedding,
        reranker: CohereRerank,
        chat_store: SimpleChatStore,
        small_talk_checker: SmallTalkChecker,
        rag_prompt: RAGPrompt,
        token_limit: int = 8000,
        top_k: int = 15,
        temperature: float = 0.6,
        max_tokens: int = 3500,
    ):
        self.llm = llm
        self.retriever = retriever
        self.embed_model = embed_model
        self.reranker = reranker
        self.chat_store = chat_store
        self.small_talk_checker = small_talk_checker
        self.rag_prompt = rag_prompt

        Settings.llm = self.llm
        Settings.embed_model = self.embed_model

        self.chat_memory = ChatMemoryBuffer.from_defaults()
        self.rag_engine = CondensePlusContextChatEngine(
            retriever=self.retriever,
            llm=self.llm,
            system_prompt=self.rag_prompt.prompt,
            node_postprocessors=[self.reranker],
            memory=self.chat_memory,
        )

        prefix_messages = [ChatMessage(
            role='system', content=self.rag_prompt.small_talk_prompt)]
        self.smalltalk_engine = SimpleChatEngine(
            llm=self.llm,
            memory=self.chat_memory,
            prefix_messages=prefix_messages,
        )

    def chat(self, user_input: str) -> str:
        """
        Routes input to small-talk or RAG engine, persists memory.
        """
        if self.small_talk_checker.is_small_talk(user_input):
            resp = self.smalltalk_engine.chat(user_input)
        else:
            resp = self.rag_engine.chat(user_input)

        # self.chat_store.persist(self.memory_path)
        return resp

    def clear_memory(self):
        """Clears both in-memory and persisted chat history."""
        self.chat_memory.reset()
        # try:
        #     os.remove(self.memory_path)
        # except OSError:
        #     pass



