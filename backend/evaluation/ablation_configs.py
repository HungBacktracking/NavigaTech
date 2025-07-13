"""
Ablation Study Configurations for Hybrid RAG Evaluation
Tests different components and configurations
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum
import copy


class ComponentType(Enum):
    """Types of components that can be modified"""
    EMBEDDING_RETRIEVER = "embedding_retriever"
    GRAPH_RETRIEVER = "graph_retriever"
    RERANKER = "reranker"
    HYBRID_WEIGHTS = "hybrid_weights"
    TOP_K = "top_k"
    LLM = "llm"


@dataclass
class AblationConfig:
    """Configuration for ablation study"""
    name: str
    description: str
    modifications: Dict[str, Any]
    component_type: ComponentType


class AblationConfigManager:
    """Manages configurations for ablation studies"""
    
    def __init__(self):
        self.configs = self._create_default_configs()
    
    def _create_default_configs(self) -> List[AblationConfig]:
        """Create default ablation configurations"""
        configs = [
            # Test individual retrievers
            AblationConfig(
                name="embedding_only",
                description="Use only embedding-based retrieval",
                modifications={
                    "disable_graph_retriever": True,
                    "embedding_weight": 1.0,
                    "graph_weight": 0.0
                },
                component_type=ComponentType.GRAPH_RETRIEVER
            ),
            
            AblationConfig(
                name="graph_only",
                description="Use only graph-based retrieval",
                modifications={
                    "disable_embedding_retriever": True,
                    "embedding_weight": 0.0,
                    "graph_weight": 1.0
                },
                component_type=ComponentType.EMBEDDING_RETRIEVER
            ),
            
            # Test without reranker
            AblationConfig(
                name="no_reranker",
                description="Disable Cohere reranker",
                modifications={
                    "disable_reranker": True
                },
                component_type=ComponentType.RERANKER
            ),
            
            # Test different weight combinations
            AblationConfig(
                name="embedding_heavy",
                description="80% embedding, 20% graph",
                modifications={
                    "embedding_weight": 0.8,
                    "graph_weight": 0.2
                },
                component_type=ComponentType.HYBRID_WEIGHTS
            ),
            
            AblationConfig(
                name="graph_heavy",
                description="20% embedding, 80% graph",
                modifications={
                    "embedding_weight": 0.2,
                    "graph_weight": 0.8
                },
                component_type=ComponentType.HYBRID_WEIGHTS
            ),
            
            AblationConfig(
                name="balanced",
                description="50% embedding, 50% graph",
                modifications={
                    "embedding_weight": 0.5,
                    "graph_weight": 0.5
                },
                component_type=ComponentType.HYBRID_WEIGHTS
            ),
            
            # Test different top_k values
            AblationConfig(
                name="top_k_5",
                description="Retrieve only top 5 documents",
                modifications={
                    "top_k": 5
                },
                component_type=ComponentType.TOP_K
            ),
            
            AblationConfig(
                name="top_k_10",
                description="Retrieve top 10 documents",
                modifications={
                    "top_k": 10
                },
                component_type=ComponentType.TOP_K
            ),
            
            AblationConfig(
                name="top_k_30",
                description="Retrieve top 30 documents",
                modifications={
                    "top_k": 30
                },
                component_type=ComponentType.TOP_K
            ),
        ]
        
        return configs
    
    def get_configs(self, component_types: Optional[List[ComponentType]] = None) -> List[AblationConfig]:
        """Get configurations, optionally filtered by component type"""
        if component_types is None:
            return self.configs
        
        return [
            config for config in self.configs 
            if config.component_type in component_types
        ]
    
    def add_custom_config(self, config: AblationConfig):
        """Add a custom configuration"""
        self.configs.append(config)
    
    def apply_config_to_system(self, rag_system, config: AblationConfig):
        """
        Apply configuration to RAG system
        This creates a modified copy of the system
        """
        # Create a wrapper or modified instance based on config
        # This is a template - you'll need to implement based on your system
        
        modified_system = RAGSystemWrapper(rag_system, config.modifications)
        return modified_system


class RAGSystemWrapper:
    """
    Wrapper for RAG system that applies modifications
    This needs to be adapted to your specific system architecture
    """
    
    def __init__(self, base_system, modifications: Dict[str, Any]):
        self.base_system = base_system
        self.modifications = modifications
        
        # Apply modifications
        self._apply_modifications()
    
    def _apply_modifications(self):
        """Apply modifications to the system"""
        # Handle retriever modifications
        if self.modifications.get("disable_graph_retriever"):
            self._disable_graph_retriever()
        
        if self.modifications.get("disable_embedding_retriever"):
            self._disable_embedding_retriever()
        
        # Handle reranker
        if self.modifications.get("disable_reranker"):
            self._disable_reranker()
        
        # Handle weights
        if "embedding_weight" in self.modifications:
            self._update_weights()
        
        # Handle top_k
        if "top_k" in self.modifications:
            self._update_top_k()
    
    def _disable_graph_retriever(self):
        """Disable graph retriever component"""
        # Implementation depends on your system
        # This is a placeholder
        if hasattr(self.base_system, 'job_retriever'):
            # Modify the hybrid retriever to use only embedding
            self.base_system.job_retriever.graph_weight = 0.0
            self.base_system.job_retriever.embedding_weight = 1.0
            
        if hasattr(self.base_system, 'course_retriever'):
            self.base_system.course_retriever.graph_weight = 0.0
            self.base_system.course_retriever.embedding_weight = 1.0
    
    def _disable_embedding_retriever(self):
        """Disable embedding retriever component"""
        if hasattr(self.base_system, 'job_retriever'):
            self.base_system.job_retriever.graph_weight = 1.0
            self.base_system.job_retriever.embedding_weight = 0.0
            
        if hasattr(self.base_system, 'course_retriever'):
            self.base_system.course_retriever.graph_weight = 1.0
            self.base_system.course_retriever.embedding_weight = 0.0
    
    def _disable_reranker(self):
        """Disable reranker component"""
        if hasattr(self.base_system, 'job_retriever'):
            self.base_system.job_retriever.reranker = None
            
        if hasattr(self.base_system, 'course_retriever'):
            self.base_system.course_retriever.reranker = None
    
    def _update_weights(self):
        """Update retriever weights"""
        embedding_weight = self.modifications.get("embedding_weight", 0.5)
        graph_weight = self.modifications.get("graph_weight", 0.5)
        
        if hasattr(self.base_system, 'job_retriever'):
            self.base_system.job_retriever.embedding_weight = embedding_weight
            self.base_system.job_retriever.graph_weight = graph_weight
            
        if hasattr(self.base_system, 'course_retriever'):
            self.base_system.course_retriever.embedding_weight = embedding_weight
            self.base_system.course_retriever.graph_weight = graph_weight
    
    def _update_top_k(self):
        """Update top_k parameter"""
        top_k = self.modifications.get("top_k", 10)
        
        if hasattr(self.base_system, 'job_retriever'):
            self.base_system.job_retriever.top_k = top_k
            
        if hasattr(self.base_system, 'course_retriever'):
            self.base_system.course_retriever.top_k = top_k
    
    async def aquery(self, query: str):
        """Async query method - adapt to your system's interface"""
        # This needs to match your system's query interface
        return await self.base_system.aquery(query) 