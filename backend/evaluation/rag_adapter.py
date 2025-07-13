"""
RAG System Adapter for Evaluation
Connects the evaluation framework to your ChatEngine
"""

import asyncio
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
import logging

from llama_index.core.schema import NodeWithScore, TextNode
from app.chatbot.chat_engine import ChatEngine
from app.chatbot.hybrid_retriever import HybridRetriever

logger = logging.getLogger(__name__)


@dataclass
class RAGResponse:
    """Standardized RAG response for evaluation"""
    response: str
    source_nodes: List[NodeWithScore]
    metadata: Dict[str, Any]


class ChatEngineAdapter:
    """
    Adapter to make ChatEngine compatible with evaluation framework
    """
    
    def __init__(self, chat_engine: ChatEngine):
        self.chat_engine = chat_engine
        self._resume_text = "Default resume for evaluation"  # You can customize this
        self._session_id = "eval_session"
        
    def set_resume_text(self, resume_text: str):
        """Set resume text for evaluation"""
        self._resume_text = resume_text
        
    async def aquery(self, query: str) -> RAGResponse:
        """
        Async query method that returns standardized response
        """
        try:
            # Initialize chat engine for this query
            self.chat_engine.compose(
                resume=self._resume_text,
                memory=[],  # Empty memory for evaluation
                session_id=self._session_id
            )
            
            # Get response and collect full text
            full_response = ""
            source_nodes = []
            
            # Use the stream_chat method and collect response
            async for chunk in self.chat_engine.stream_chat(query):
                if chunk and not chunk.startswith("ERROR:"):
                    full_response += chunk
            
            # Extract source nodes from retrievers
            # This is a workaround since stream_chat doesn't return sources
            source_nodes = await self._get_source_nodes(query)
            
            return RAGResponse(
                response=full_response,
                source_nodes=source_nodes,
                metadata={
                    "session_id": self._session_id,
                    "is_small_talk": self.chat_engine.checker.is_small_talk(query)
                }
            )
            
        except Exception as e:
            logger.error(f"Error in aquery: {e}")
            return RAGResponse(
                response=f"Error: {str(e)}",
                source_nodes=[],
                metadata={"error": str(e)}
            )
    
    async def _get_source_nodes(self, query: str) -> List[NodeWithScore]:
        """
        Extract source nodes by directly querying retrievers
        """
        source_nodes = []
        
        try:
            # Determine which retriever to use based on query
            if any(word in query.lower() for word in ['job', 'position', 'vacancy', 'career']):
                retriever = self.chat_engine.retrievers.get("job")
            elif any(word in query.lower() for word in ['course', 'learn', 'study', 'training']):
                retriever = self.chat_engine.retrievers.get("course")
            else:
                # Default to job retriever
                retriever = self.chat_engine.retrievers.get("job")
            
            if retriever:
                from llama_index.core import QueryBundle
                query_bundle = QueryBundle(query_str=query)
                
                # Get nodes from retriever
                nodes = await retriever._aretrieve(query_bundle)
                source_nodes.extend(nodes)
                
        except Exception as e:
            logger.error(f"Error getting source nodes: {e}")
        
        return source_nodes


class HybridRAGSystem:
    """
    Wrapper for the complete Hybrid RAG system
    Makes it easier to modify for ablation studies
    """
    
    def __init__(
        self,
        chat_engine: ChatEngine,
        job_retriever: HybridRetriever,
        course_retriever: HybridRetriever
    ):
        self.chat_engine = chat_engine
        self.job_retriever = job_retriever
        self.course_retriever = course_retriever
        self.adapter = ChatEngineAdapter(chat_engine)
        
    async def aquery(self, query: str) -> RAGResponse:
        """Query the system"""
        return await self.adapter.aquery(query)
    
    def get_config_dict(self) -> Dict[str, Any]:
        """Get current configuration as dictionary"""
        return {
            "job_retriever": {
                "embedding_weight": self.job_retriever.embedding_weight,
                "graph_weight": self.job_retriever.graph_weight,
                "top_k": self.job_retriever.top_k,
                "has_reranker": self.job_retriever.reranker is not None
            },
            "course_retriever": {
                "embedding_weight": self.course_retriever.embedding_weight,
                "graph_weight": self.course_retriever.graph_weight,
                "top_k": self.course_retriever.top_k,
                "has_reranker": self.course_retriever.reranker is not None
            }
        }
    
    def apply_modifications(self, modifications: Dict[str, Any]):
        """Apply modifications for ablation studies"""
        # Handle retriever modifications
        if modifications.get("disable_graph_retriever"):
            self.job_retriever.graph_weight = 0.0
            self.job_retriever.embedding_weight = 1.0
            self.course_retriever.graph_weight = 0.0
            self.course_retriever.embedding_weight = 1.0
            
        if modifications.get("disable_embedding_retriever"):
            self.job_retriever.graph_weight = 1.0
            self.job_retriever.embedding_weight = 0.0
            self.course_retriever.graph_weight = 1.0
            self.course_retriever.embedding_weight = 0.0
        
        # Handle reranker
        if modifications.get("disable_reranker"):
            self.job_retriever.reranker = None
            self.course_retriever.reranker = None
        
        # Handle weights
        if "embedding_weight" in modifications:
            self.job_retriever.embedding_weight = modifications["embedding_weight"]
            self.course_retriever.embedding_weight = modifications["embedding_weight"]
            
        if "graph_weight" in modifications:
            self.job_retriever.graph_weight = modifications["graph_weight"]
            self.course_retriever.graph_weight = modifications["graph_weight"]
        
        # Handle top_k
        if "top_k" in modifications:
            self.job_retriever.top_k = modifications["top_k"]
            self.course_retriever.top_k = modifications["top_k"]
            
        # Update retrievers in chat engine
        self.chat_engine.retrievers["job"] = self.job_retriever
        self.chat_engine.retrievers["course"] = self.course_retriever 