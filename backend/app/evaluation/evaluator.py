import asyncio
import time
from typing import List, Dict, Any, Optional
from pathlib import Path
import pandas as pd
import json
from datetime import datetime
from llama_index.core.schema import QueryBundle

from app.evaluation.metrics import HybridRAGMetrics
from app.evaluation.dataset import EvaluationDataset, TestCase
from app.chatbot.hybrid_retriever import HybridRetriever
from app.chatbot.chat_engine import ChatEngine


class HybridRAGEvaluator:
    """Main evaluator for the Hybrid RAG system"""
    
    def __init__(self, 
                 job_retriever: HybridRetriever,
                 course_retriever: HybridRetriever,
                 chat_engine: ChatEngine,
                 output_dir: str = "evaluation_results"):
        self.job_retriever = job_retriever
        self.course_retriever = course_retriever
        self.chat_engine = chat_engine
        self.metrics = HybridRAGMetrics()
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        self.results = []
        self.experiment_metadata = {
            'start_time': None,
            'end_time': None,
            'configuration': {}
        }
    
    async def evaluate_dataset(self, 
                             dataset: EvaluationDataset,
                             resume_text: str = "Experienced software developer",
                             memory: List[Dict] = None,
                             session_id: str = "eval_session",
                             experiment_name: str = "default") -> Dict[str, Any]:
        """Run evaluation on entire dataset"""
        self.experiment_metadata['start_time'] = datetime.now().isoformat()
        self.experiment_metadata['experiment_name'] = experiment_name
        
        # Initialize chat engine
        self.chat_engine.compose(resume_text, memory or [], session_id)
        
        # Process each query
        for query in dataset.queries:
            gt = dataset.ground_truth.get(query['id'], {})
            test_case = TestCase(query['id'], query['question'], gt)
            
            # Run evaluation
            await self._evaluate_single_query(test_case, query['domain'])
            self.results.append(test_case.to_dict())
        
        self.experiment_metadata['end_time'] = datetime.now().isoformat()
        
        # Aggregate results
        aggregated_results = self._aggregate_results()
        
        # Save results
        self._save_results(experiment_name, aggregated_results)
        
        return aggregated_results
    
    async def _evaluate_single_query(self, test_case: TestCase, domain: str):
        """Evaluate a single query"""
        # Select appropriate retriever
        retriever = self._select_retriever(domain)
        
        # Retrieval phase
        start_time = time.time()
        query_bundle = QueryBundle(query_str=test_case.question)
        retrieved_nodes = await retriever._aretrieve(query_bundle)
        retrieval_time = time.time() - start_time
        
        # Convert nodes to documents
        retrieved_docs = []
        for node_with_score in retrieved_nodes:
            doc = {
                'id': node_with_score.node.metadata.get('id', str(hash(node_with_score.node.text[:50]))),
                'text': node_with_score.node.text,
                'score': node_with_score.score,
                'metadata': node_with_score.node.metadata
            }
            retrieved_docs.append(doc)
        
        test_case.add_retrieval_results(retrieved_docs)
        
        # Generation phase
        start_time = time.time()
        generated_answer = await self._generate_answer(test_case.question)
        generation_time = time.time() - start_time
        
        test_case.add_generation_results(generated_answer, generation_time)
        
        # Evaluate metrics
        eval_results = self.metrics.evaluate_end_to_end(
            test_case.question,
            retrieved_docs,
            generated_answer,
            test_case.ground_truth
        )
        
        # Add timing information
        eval_results['timing'] = {
            'retrieval_time': retrieval_time,
            'generation_time': generation_time,
            'total_time': retrieval_time + generation_time
        }
        
        test_case.results['evaluation'] = eval_results
    
    def _select_retriever(self, domain: str) -> HybridRetriever:
        """Select appropriate retriever based on domain"""
        if domain in ['job', 'career', 'skill']:
            return self.job_retriever
        elif domain in ['course', 'learning']:
            return self.course_retriever
        else:
            # Default to job retriever for complex queries
            return self.job_retriever
    
    async def _generate_answer(self, question: str) -> str:
        """Generate answer using chat engine"""
        full_response = ""
        
        try:
            # Use the streaming interface
            async for chunk in self.chat_engine.stream_chat(question):
                if chunk and not chunk.startswith("ERROR:"):
                    full_response += chunk
        except Exception as e:
            print(f"Error generating answer: {e}")
            full_response = f"Error: {str(e)}"
        
        return full_response
    
    def _aggregate_results(self) -> Dict[str, Any]:
        """Aggregate evaluation results across all queries"""
        if not self.results:
            return {}
        
        # Initialize aggregators
        retrieval_metrics = {}
        generation_metrics = {}
        timing_metrics = {}
        
        # Collect all metrics
        for result in self.results:
            eval_data = result['results'].get('evaluation', {})
            
            # Aggregate retrieval metrics
            for metric, value in eval_data.get('retrieval_metrics', {}).items():
                if metric not in retrieval_metrics:
                    retrieval_metrics[metric] = []
                retrieval_metrics[metric].append(value)
            
            # Aggregate generation metrics
            for metric, value in eval_data.get('generation_metrics', {}).items():
                if metric not in generation_metrics:
                    generation_metrics[metric] = []
                generation_metrics[metric].append(value)
            
            # Aggregate timing
            timing = eval_data.get('timing', {})
            for metric, value in timing.items():
                if metric not in timing_metrics:
                    timing_metrics[metric] = []
                timing_metrics[metric].append(value)
        
        # Calculate statistics
        aggregated = {
            'num_queries': len(self.results),
            'retrieval_metrics': self._calculate_statistics(retrieval_metrics),
            'generation_metrics': self._calculate_statistics(generation_metrics),
            'timing_metrics': self._calculate_statistics(timing_metrics),
            'metadata': self.experiment_metadata
        }
        
        return aggregated
    
    def _calculate_statistics(self, metrics: Dict[str, List[float]]) -> Dict[str, Dict[str, float]]:
        """Calculate mean, std, min, max for each metric"""
        stats = {}
        
        for metric, values in metrics.items():
            if values:
                stats[metric] = {
                    'mean': pd.Series(values).mean(),
                    'std': pd.Series(values).std(),
                    'min': pd.Series(values).min(),
                    'max': pd.Series(values).max(),
                    'median': pd.Series(values).median()
                }
        
        return stats
    
    def _save_results(self, experiment_name: str, aggregated_results: Dict[str, Any]):
        """Save evaluation results"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save detailed results
        detailed_path = self.output_dir / f"{experiment_name}_detailed_{timestamp}.json"
        with open(detailed_path, 'w') as f:
            json.dump({
                'experiment': experiment_name,
                'timestamp': timestamp,
                'detailed_results': self.results,
                'aggregated_results': aggregated_results
            }, f, indent=2)
        
        # Save aggregated results as CSV
        metrics_data = []
        
        # Retrieval metrics
        for metric, stats in aggregated_results.get('retrieval_metrics', {}).items():
            for stat_name, value in stats.items():
                metrics_data.append({
                    'metric_type': 'retrieval',
                    'metric_name': metric,
                    'statistic': stat_name,
                    'value': value
                })
        
        # Generation metrics
        for metric, stats in aggregated_results.get('generation_metrics', {}).items():
            for stat_name, value in stats.items():
                metrics_data.append({
                    'metric_type': 'generation',
                    'metric_name': metric,
                    'statistic': stat_name,
                    'value': value
                })
        
        # Timing metrics
        for metric, stats in aggregated_results.get('timing_metrics', {}).items():
            for stat_name, value in stats.items():
                metrics_data.append({
                    'metric_type': 'timing',
                    'metric_name': metric,
                    'statistic': stat_name,
                    'value': value
                })
        
        if metrics_data:
            df = pd.DataFrame(metrics_data)
            csv_path = self.output_dir / f"{experiment_name}_metrics_{timestamp}.csv"
            df.to_csv(csv_path, index=False)
    
    async def ablation_study(self, dataset: EvaluationDataset, resume_text: str = "Experienced software developer") -> Dict[str, Any]:
        """Run ablation study to evaluate contribution of each component"""
        ablation_results = {}
        
        # Test 1: Embedding-only retrieval
        print("Running ablation: Embedding-only retrieval...")
        self.job_retriever.graph_weight = 0.0
        self.job_retriever.embedding_weight = 1.0
        self.course_retriever.graph_weight = 0.0
        self.course_retriever.embedding_weight = 1.0
        
        results_embedding_only = await self.evaluate_dataset(
            dataset, resume_text, experiment_name="ablation_embedding_only"
        )
        ablation_results['embedding_only'] = results_embedding_only
        
        # Test 2: Graph-only retrieval
        print("Running ablation: Graph-only retrieval...")
        self.job_retriever.graph_weight = 1.0
        self.job_retriever.embedding_weight = 0.0
        self.course_retriever.graph_weight = 1.0
        self.course_retriever.embedding_weight = 0.0
        
        self.results = []  # Reset results
        results_graph_only = await self.evaluate_dataset(
            dataset, resume_text, experiment_name="ablation_graph_only"
        )
        ablation_results['graph_only'] = results_graph_only
        
        # Test 3: Hybrid (default weights)
        print("Running ablation: Hybrid retrieval...")
        self.job_retriever.graph_weight = 0.4
        self.job_retriever.embedding_weight = 0.6
        self.course_retriever.graph_weight = 0.4
        self.course_retriever.embedding_weight = 0.6
        
        self.results = []  # Reset results
        results_hybrid = await self.evaluate_dataset(
            dataset, resume_text, experiment_name="ablation_hybrid"
        )
        ablation_results['hybrid'] = results_hybrid
        
        # Test 4: Without reranker
        print("Running ablation: Without reranker...")
        original_reranker_job = self.job_retriever.reranker
        original_reranker_course = self.course_retriever.reranker
        self.job_retriever.reranker = None
        self.course_retriever.reranker = None
        
        self.results = []  # Reset results
        results_no_reranker = await self.evaluate_dataset(
            dataset, resume_text, experiment_name="ablation_no_reranker"
        )
        ablation_results['no_reranker'] = results_no_reranker
        
        # Restore reranker
        self.job_retriever.reranker = original_reranker_job
        self.course_retriever.reranker = original_reranker_course
        
        # Save ablation study summary
        self._save_ablation_summary(ablation_results)
        
        return ablation_results
    
    def _save_ablation_summary(self, ablation_results: Dict[str, Any]):
        """Save ablation study summary"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Create comparison DataFrame
        comparison_data = []
        
        for config, results in ablation_results.items():
            row = {'configuration': config}
            
            # Add retrieval metrics
            for metric, stats in results.get('retrieval_metrics', {}).items():
                if 'mean' in stats:
                    row[f'retrieval_{metric}_mean'] = stats['mean']
            
            # Add generation metrics
            for metric, stats in results.get('generation_metrics', {}).items():
                if 'mean' in stats:
                    row[f'generation_{metric}_mean'] = stats['mean']
            
            # Add timing metrics
            for metric, stats in results.get('timing_metrics', {}).items():
                if 'mean' in stats:
                    row[f'timing_{metric}_mean'] = stats['mean']
            
            comparison_data.append(row)
        
        df = pd.DataFrame(comparison_data)
        csv_path = self.output_dir / f"ablation_study_summary_{timestamp}.csv"
        df.to_csv(csv_path, index=False)
        
        # Save detailed JSON
        json_path = self.output_dir / f"ablation_study_detailed_{timestamp}.json"
        with open(json_path, 'w') as f:
            json.dump(ablation_results, f, indent=2) 