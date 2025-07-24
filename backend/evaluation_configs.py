"""
Evaluation Configuration Presets
================================
Standardized configurations for each RAG approach to ensure fair comparison
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any


@dataclass
class RetrieverConfig:
    """Configuration for retriever components"""
    # Embedding retriever settings
    embedding_model: str = "BAAI/bge-large-en-v1.5"
    dense_top_k: int = 20
    hybrid_mode: bool = False  # Enable dense+sparse
    sparse_weight: float = 0.3  # Weight for sparse vectors in hybrid mode
    
    # Graph retriever settings
    graph_top_k: int = 20
    graph_search_depth: int = 2
    include_skills: bool = True
    include_relationships: bool = True
    
    # Hybrid fusion settings
    embedding_weight: float = 0.6
    graph_weight: float = 0.4
    fusion_k: int = 60  # RRF parameter
    
    # Reranking settings
    use_reranker: bool = False
    rerank_top_k: int = 10
    reranker_model: str = "cohere"


@dataclass 
class GenerationConfig:
    """Configuration for generation settings"""
    temperature: float = 0.3
    max_tokens: int = 500
    top_p: float = 0.9
    system_prompt: Optional[str] = None
    

@dataclass
class EvaluationConfig:
    """Complete configuration for an evaluation run"""
    retriever_config: RetrieverConfig
    generation_config: GenerationConfig
    experiment_name: str
    description: str
    
    
# Preset configurations for each approach
EVALUATION_PRESETS = {
    "baseline": EvaluationConfig(
        retriever_config=RetrieverConfig(
            dense_top_k=0,  # No retrieval
        ),
        generation_config=GenerationConfig(
            temperature=0.3,
            system_prompt="You are a helpful career and education advisor. Answer based on your general knowledge."
        ),
        experiment_name="Baseline (No RAG)",
        description="Pure LLM without any retrieval augmentation"
    ),
    
    "dense_embedding": EvaluationConfig(
        retriever_config=RetrieverConfig(
            dense_top_k=10,
            hybrid_mode=False,
            use_reranker=False
        ),
        generation_config=GenerationConfig(
            temperature=0.3,
        ),
        experiment_name="Dense Embedding RAG",
        description="Traditional RAG with dense embeddings only"
    ),
    
    "hybrid_search": EvaluationConfig(
        retriever_config=RetrieverConfig(
            dense_top_k=10,
            hybrid_mode=True,
            sparse_weight=0.3,
            use_reranker=False
        ),
        generation_config=GenerationConfig(
            temperature=0.3,
        ),
        experiment_name="Hybrid Search RAG",
        description="RAG with both dense and sparse embeddings"
    ),
    
    "graph_only": EvaluationConfig(
        retriever_config=RetrieverConfig(
            graph_top_k=10,
            graph_search_depth=2,
            include_skills=True,
            include_relationships=True,
            use_reranker=False
        ),
        generation_config=GenerationConfig(
            temperature=0.3,
        ),
        experiment_name="Graph RAG",
        description="Knowledge graph-based retrieval only"
    ),
    
    "hybrid_rag": EvaluationConfig(
        retriever_config=RetrieverConfig(
            dense_top_k=15,
            graph_top_k=15,
            embedding_weight=0.6,
            graph_weight=0.4,
            fusion_k=60,
            use_reranker=False
        ),
        generation_config=GenerationConfig(
            temperature=0.3,
        ),
        experiment_name="Hybrid RAG",
        description="Combination of embedding and graph retrieval"
    ),
    
    "reranked_dense": EvaluationConfig(
        retriever_config=RetrieverConfig(
            dense_top_k=20,
            hybrid_mode=False,
            use_reranker=True,
            rerank_top_k=10,
            reranker_model="cohere"
        ),
        generation_config=GenerationConfig(
            temperature=0.3,
        ),
        experiment_name="Reranked Dense RAG",
        description="Dense embeddings with neural reranking"
    ),
    
    "reranked_hybrid": EvaluationConfig(
        retriever_config=RetrieverConfig(
            dense_top_k=20,
            graph_top_k=20,
            embedding_weight=0.6,
            graph_weight=0.4,
            fusion_k=60,
            use_reranker=True,
            rerank_top_k=10
        ),
        generation_config=GenerationConfig(
            temperature=0.3,
        ),
        experiment_name="Reranked Hybrid RAG",
        description="Hybrid retrieval with neural reranking"
    ),
    
    # Additional experimental configurations
    "graph_heavy_hybrid": EvaluationConfig(
        retriever_config=RetrieverConfig(
            dense_top_k=15,
            graph_top_k=15,
            embedding_weight=0.3,
            graph_weight=0.7,  # More weight on graph
            fusion_k=60,
            use_reranker=False
        ),
        generation_config=GenerationConfig(
            temperature=0.3,
        ),
        experiment_name="Graph-Heavy Hybrid RAG",
        description="Hybrid with emphasis on graph retrieval"
    ),
    
    "high_recall": EvaluationConfig(
        retriever_config=RetrieverConfig(
            dense_top_k=30,  # Retrieve more documents
            graph_top_k=30,
            embedding_weight=0.5,
            graph_weight=0.5,
            fusion_k=60,
            use_reranker=True,
            rerank_top_k=15  # Keep more after reranking
        ),
        generation_config=GenerationConfig(
            temperature=0.3,
            max_tokens=700  # Allow longer answers
        ),
        experiment_name="High Recall RAG",
        description="Optimized for high recall with more retrieved documents"
    )
}


def get_custom_config(base_config: str, **overrides) -> EvaluationConfig:
    """Get a configuration with custom overrides"""
    if base_config not in EVALUATION_PRESETS:
        raise ValueError(f"Unknown base config: {base_config}")
    
    import copy
    config = copy.deepcopy(EVALUATION_PRESETS[base_config])
    
    # Apply overrides
    for key, value in overrides.items():
        if hasattr(config.retriever_config, key):
            setattr(config.retriever_config, key, value)
        elif hasattr(config.generation_config, key):
            setattr(config.generation_config, key, value)
        else:
            raise ValueError(f"Unknown configuration parameter: {key}")
    
    return config 