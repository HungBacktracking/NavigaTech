from typing import List, Optional
from llama_index.core.schema import NodeWithScore, QueryBundle
from llama_index.core.retrievers import BaseRetriever
from llama_index.core.callbacks import CallbackManager
from llama_index.postprocessor.cohere_rerank import CohereRerank
import asyncio


class HybridRetriever(BaseRetriever):
    """
    Hybrid retriever combining embedding-based and graph-based retrieval.
    Implements reciprocal rank fusion for result merging.
    """
    
    def __init__(
        self,
        embedding_retriever: BaseRetriever,
        graph_retriever: BaseRetriever,
        reranker: Optional[CohereRerank] = None,
        embedding_weight: float = 0.5,
        graph_weight: float = 0.5,
        top_k: int = 10,
        fusion_k: int = 60,  # RRF parameter
        callback_manager: Optional[CallbackManager] = None
    ):
        self.embedding_retriever = embedding_retriever
        self.graph_retriever = graph_retriever
        self.reranker = reranker
        # Normalize weights to ensure they sum to 1
        total_weight = embedding_weight + graph_weight
        if total_weight == 0:
            self.embedding_weight = 0.5
            self.graph_weight = 0.5
        else:
            self.embedding_weight = embedding_weight / total_weight
            self.graph_weight = graph_weight / total_weight
        self.top_k = top_k
        self.fusion_k = max(1, fusion_k)  # Ensure fusion_k is at least 1
        super().__init__(callback_manager=callback_manager)
    
    def _retrieve(self, query_bundle: QueryBundle) -> List[NodeWithScore]:
        """Sync retrieve"""
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # If there's already a running loop, use ThreadPoolExecutor
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(asyncio.run, self._aretrieve(query_bundle))
                    return future.result()
            else:
                return loop.run_until_complete(self._aretrieve(query_bundle))
        except Exception as e:
            print(f"Error in hybrid sync retrieve: {e}")
            return []
    
    async def _aretrieve(self, query_bundle: QueryBundle) -> List[NodeWithScore]:
        """Async hybrid retrieve"""
        # Parallel retrieval from both sources
        embedding_task = asyncio.create_task(
            self._safe_aretrieve(self.embedding_retriever, query_bundle)
        )
        graph_task = asyncio.create_task(
            self._safe_aretrieve(self.graph_retriever, query_bundle)
        )
        
        embedding_results, graph_results = await asyncio.gather(
            embedding_task, graph_task
        )
        
        # Combine results using reciprocal rank fusion
        fused_results = self._reciprocal_rank_fusion(
            embedding_results, 
            graph_results
        )
        
        # Apply reranking if available
        if self.reranker and fused_results:
            fused_results = self.reranker.postprocess_nodes(
                fused_results, 
                query_bundle
            )
        
        return fused_results[:self.top_k]
    
    async def _safe_aretrieve(
        self, 
        retriever: BaseRetriever, 
        query_bundle: QueryBundle
    ) -> List[NodeWithScore]:
        """Safely retrieve with error handling"""
        try:
            if hasattr(retriever, '_aretrieve'):
                return await retriever._aretrieve(query_bundle)
            else:
                # Fallback to sync retrieve in thread
                loop = asyncio.get_event_loop()
                return await loop.run_in_executor(
                    None, 
                    retriever._retrieve, 
                    query_bundle
                )
        except Exception as e:
            print(f"Error in retriever {type(retriever).__name__}: {e}")
            return []
    
    def _reciprocal_rank_fusion(
        self,
        embedding_results: List[NodeWithScore],
        graph_results: List[NodeWithScore]
    ) -> List[NodeWithScore]:
        """
        Implements Reciprocal Rank Fusion (RRF) to combine results.
        RRF score = sum(1 / (k + rank_i)) for each ranking
        """
        # Handle empty results
        if not embedding_results and not graph_results:
            return []
            
        # Create node to score mapping
        node_scores = {}
        node_map = {}
        
        # Process embedding results
        for rank, node_with_score in enumerate(embedding_results):
            try:
                node_id = self._get_node_id(node_with_score.node)
                rrf_score = self.embedding_weight / (self.fusion_k + rank + 1)
                
                if node_id not in node_scores:
                    node_scores[node_id] = 0
                    node_map[node_id] = node_with_score.node
                
                node_scores[node_id] += rrf_score
            except Exception as e:
                print(f"Error processing embedding result at rank {rank}: {e}")
                continue
        
        # Process graph results
        for rank, node_with_score in enumerate(graph_results):
            try:
                node_id = self._get_node_id(node_with_score.node)
                rrf_score = self.graph_weight / (self.fusion_k + rank + 1)
                
                if node_id not in node_scores:
                    node_scores[node_id] = 0
                    node_map[node_id] = node_with_score.node
                
                node_scores[node_id] += rrf_score
            except Exception as e:
                print(f"Error processing graph result at rank {rank}: {e}")
                continue
        
        # Sort by RRF score and create final results
        sorted_nodes = sorted(
            node_scores.items(), 
            key=lambda x: x[1], 
            reverse=True
        )
        
        results = []
        for node_id, score in sorted_nodes:
            try:
                results.append(
                    NodeWithScore(
                        node=node_map[node_id],
                        score=score
                    )
                )
            except Exception as e:
                print(f"Error creating result for node {node_id}: {e}")
                continue
        
        return results
    
    def _get_node_id(self, node) -> str:
        """Generate unique ID for a node"""
        # Try to get ID from metadata first
        if hasattr(node, 'metadata'):
            if 'id' in node.metadata:
                return str(node.metadata['id'])
            elif 'title' in node.metadata:
                return str(node.metadata['title'])
        
        # Fallback to text hash
        if hasattr(node, 'text'):
            return str(hash(node.text[:100]))
        
        return str(id(node)) 