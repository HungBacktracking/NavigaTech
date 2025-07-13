"""
Comprehensive Evaluation Framework for Hybrid RAG System
Implements RAGAS metrics, domain-specific evaluations, and ablation studies
"""

import asyncio
import json
import time
from typing import Dict, List, Any, Optional, Tuple, Callable
from datetime import datetime

from llama_index.llms.gemini import Gemini
from pathlib import Path
import pandas as pd
import numpy as np
from dataclasses import dataclass, asdict
import logging

from ragas.embeddings import LangchainEmbeddingsWrapper
from ragas.llms import LangchainLLMWrapper
from tqdm.asyncio import tqdm as async_tqdm
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats

from llama_index.embeddings.huggingface import HuggingFaceEmbedding

from dotenv import load_dotenv
import os
load_dotenv()

# RAGAS imports
from ragas import evaluate
from ragas.metrics import (
    answer_relevancy,
    faithfulness,
    context_recall,
    context_precision,
    answer_correctness,
    answer_similarity
)
from datasets import Dataset

# LlamaIndex imports
from llama_index.core import QueryBundle
from llama_index.core.schema import NodeWithScore
from llama_index.core.evaluation import (
    SemanticSimilarityEvaluator,
    ResponseEvaluator,
    RelevancyEvaluator
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class EvaluationResult:
    """Complete evaluation result"""
    query_id: str
    query: str
    query_type: str
    predicted_answer: str
    ground_truth_answer: str
    retrieved_contexts: List[str]
    expected_contexts: List[str]
    metrics: Dict[str, float]
    latency_ms: float
    metadata: Dict[str, Any]


@dataclass
class AblationResult:
    """Results from ablation study"""
    configuration: str
    results: List[EvaluationResult]
    aggregate_metrics: Dict[str, float]
    statistical_tests: Dict[str, Any]


class HybridRAGEvaluator:
    """Comprehensive evaluator for Hybrid RAG system"""
    
    def __init__(
        self,
        output_dir: str = "evaluation_results",
        enable_wandb: bool = False,
        wandb_project: Optional[str] = None,
        embedding_model_name: str = "BAAI/bge-large-en-v1.5"
    ):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Initialize tracking
        self.enable_wandb = enable_wandb
        if enable_wandb:
            import wandb
            self.wandb = wandb
            self.wandb.init(project=wandb_project or "hybrid-rag-evaluation")

        self.embedding_model_name = embedding_model_name
        self.embedding_model = HuggingFaceEmbedding(model_name=self.embedding_model_name)

        self.llm = Gemini(
            model_name='models/gemini-2.0-flash',
            api_key=os.getenv("GEMINI_TOKEN"),
            max_tokens=int(os.getenv("MAX_TOKENS")),
            temperature=float(os.getenv("TEMPERATURE")),
        )

        # Initialize evaluators
        self._init_evaluators()
        
    def _init_evaluators(self):
        """Initialize various evaluators"""
        self.semantic_evaluator = SemanticSimilarityEvaluator(self.embedding_model)
        self.relevancy_evaluator = RelevancyEvaluator(llm=self.llm)
        
        # Domain-specific metrics
        self.domain_metrics = {
            "skill_coverage": self._evaluate_skill_coverage,
            "entity_precision": self._evaluate_entity_precision,
            "requirement_matching": self._evaluate_requirement_matching,
            "career_path_coherence": self._evaluate_career_path_coherence
        }
    
    async def evaluate_system(
        self,
        rag_system,
        eval_dataset: pd.DataFrame,
        configurations: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Main evaluation function
        
        Args:
            rag_system: Your RAG system instance
            eval_dataset: Evaluation dataset
            configurations: List of configurations for ablation studies
        """
        logger.info("Starting comprehensive evaluation...")
        
        # Default evaluation
        base_results = await self._evaluate_configuration(
            rag_system, 
            eval_dataset, 
            "baseline"
        )
        
        all_results = {"baseline": base_results}
        
        # Ablation studies if configurations provided
        if configurations:
            logger.info("Running ablation studies...")
            for config in configurations:
                config_name = config.get("name", "unnamed")
                logger.info(f"Evaluating configuration: {config_name}")
                
                # Apply configuration
                modified_system = self._apply_configuration(rag_system, config)
                
                # Evaluate
                results = await self._evaluate_configuration(
                    modified_system,
                    eval_dataset,
                    config_name
                )
                
                all_results[config_name] = results
        
        # Statistical analysis
        analysis = self._perform_statistical_analysis(all_results)
        
        # Generate report
        report = self._generate_comprehensive_report(all_results, analysis)
        
        # Save results
        self._save_results(all_results, analysis, report)
        
        return {
            "results": all_results,
            "analysis": analysis,
            "report": report
        }
    
    async def _evaluate_configuration(
        self,
        rag_system,
        eval_dataset: pd.DataFrame,
        config_name: str
    ) -> AblationResult:
        """Evaluate a single configuration"""
        results = []
        
        # Convert dataframe to list of samples
        samples = eval_dataset.to_dict('records')
        
        for sample in async_tqdm(samples, desc=f"Evaluating {config_name}"):
            try:
                # Time the query
                start_time = time.time()
                
                # Get RAG response
                response_data = await self._get_rag_response(rag_system, sample['query'])
                
                latency_ms = (time.time() - start_time) * 1000
                
                # Evaluate response
                eval_result = await self._evaluate_single_sample(
                    sample,
                    response_data,
                    latency_ms
                )
                
                results.append(eval_result)
                
            except Exception as e:
                logger.error(f"Error evaluating sample {sample.get('query_id')}: {e}")
                continue
        
        # Aggregate metrics
        aggregate_metrics = self._aggregate_metrics(results)
        
        # Statistical tests
        statistical_tests = self._run_statistical_tests(results)
        
        return AblationResult(
            configuration=config_name,
            results=results,
            aggregate_metrics=aggregate_metrics,
            statistical_tests=statistical_tests
        )
    
    async def _get_rag_response(self, rag_system, query: str) -> Dict[str, Any]:
        """Get response from RAG system"""
        # This needs to be adapted to your system's interface
        try:
            # Assuming your system has a similar interface
            response = await rag_system.aquery(query)
            
            return {
                "answer": response.response,
                "contexts": [node.node.text for node in response.source_nodes],
                "metadata": response.metadata if hasattr(response, 'metadata') else {}
            }
        except Exception as e:
            logger.error(f"Error getting RAG response: {e}")
            return {
                "answer": "",
                "contexts": [],
                "metadata": {"error": str(e)}
            }
    
    async def _evaluate_single_sample(
        self,
        sample: Dict[str, Any],
        response_data: Dict[str, Any],
        latency_ms: float
    ) -> EvaluationResult:
        """Evaluate a single sample with all metrics"""
        
        # Prepare data for RAGAS
        ragas_data = {
            "question": sample['query'],
            "answer": response_data['answer'],
            "contexts": response_data['contexts'],
            "ground_truths": [sample['ground_truth_answer']]
        }
        
        # RAGAS metrics
        ragas_metrics = await self._compute_ragas_metrics(ragas_data)
        
        # Domain-specific metrics
        domain_metrics = await self._compute_domain_metrics(sample, response_data)
        
        # Combine all metrics
        all_metrics = {**ragas_metrics, **domain_metrics}
        
        return EvaluationResult(
            query_id=sample['query_id'],
            query=sample['query'],
            query_type=sample.get('query_type', 'unknown'),
            predicted_answer=response_data['answer'],
            ground_truth_answer=sample['ground_truth_answer'],
            retrieved_contexts=response_data['contexts'],
            expected_contexts=sample.get('context_documents', []),
            metrics=all_metrics,
            latency_ms=latency_ms,
            metadata={
                **sample.get('metadata', {}),
                **response_data.get('metadata', {})
            }
        )
    
    async def _compute_ragas_metrics(self, data: Dict[str, Any]) -> Dict[str, float]:
        """Compute RAGAS metrics"""
        try:
            # Create dataset for RAGAS
            eval_dataset = Dataset.from_dict({
                "question": [data["question"]],
                "answer": [data["answer"]],
                "contexts": [data["contexts"]],
                "ground_truths": [data["ground_truths"]]
            })
            
            # Evaluate with RAGAS
            result = evaluate(
                eval_dataset,
                metrics=[
                    context_precision,
                    faithfulness,
                    answer_relevancy,
                    context_recall,
                    answer_correctness,
                    answer_similarity
                ],
                llm=LangchainLLMWrapper(self.llm),
                embeddings=LangchainEmbeddingsWrapper(self.embedding_model)
            )
            
            # Extract scores
            return {metric: result[metric] for metric in result}
            
        except Exception as e:
            logger.error(f"Error computing RAGAS metrics: {e}")
            return {
                "context_precision": 0.0,
                "faithfulness": 0.0,
                "answer_relevancy": 0.0,
                "context_recall": 0.0,
                "answer_correctness": 0.0,
                "answer_similarity": 0.0
            }
    
    async def _compute_domain_metrics(
        self,
        sample: Dict[str, Any],
        response_data: Dict[str, Any]
    ) -> Dict[str, float]:
        """Compute domain-specific metrics"""
        metrics = {}
        
        for metric_name, metric_func in self.domain_metrics.items():
            try:
                score = await metric_func(sample, response_data)
                metrics[metric_name] = score
            except Exception as e:
                logger.error(f"Error computing {metric_name}: {e}")
                metrics[metric_name] = 0.0
        
        return metrics
    
    async def _evaluate_skill_coverage(
        self,
        sample: Dict[str, Any],
        response_data: Dict[str, Any]
    ) -> float:
        """Evaluate if mentioned skills are covered correctly"""
        # Extract skills from metadata
        expected_skills = set(sample.get('metadata', {}).get('key_entities', []))
        
        if not expected_skills:
            return 1.0
        
        # Simple keyword matching (can be improved with NER)
        answer_lower = response_data['answer'].lower()
        found_skills = sum(1 for skill in expected_skills if skill.lower() in answer_lower)
        
        return found_skills / len(expected_skills)
    
    async def _evaluate_entity_precision(
        self,
        sample: Dict[str, Any],
        response_data: Dict[str, Any]
    ) -> float:
        """Evaluate precision of entity extraction"""
        # This would use NER in production
        # Simplified version for demonstration
        entities = ['job', 'course', 'skill', 'company', 'certification']
        
        answer = response_data['answer'].lower()
        relevant_entities = sum(1 for entity in entities if entity in answer)
        
        return min(relevant_entities / len(entities), 1.0)
    
    async def _evaluate_requirement_matching(
        self,
        sample: Dict[str, Any],
        response_data: Dict[str, Any]
    ) -> float:
        """Evaluate if job requirements are matched correctly"""
        query_type = sample.get('query_type', '')
        
        if 'job' not in query_type.lower():
            return 1.0  # Not applicable
        
        # Check for requirement keywords
        requirement_keywords = ['require', 'must have', 'qualification', 'experience', 'skill']
        answer = response_data['answer'].lower()
        
        found_requirements = sum(1 for keyword in requirement_keywords if keyword in answer)
        
        return min(found_requirements / len(requirement_keywords), 1.0)
    
    async def _evaluate_career_path_coherence(
        self,
        sample: Dict[str, Any],
        response_data: Dict[str, Any]
    ) -> float:
        """Evaluate coherence of career path recommendations"""
        query_type = sample.get('query_type', '')
        
        if 'career' not in query_type.lower() and 'path' not in query_type.lower():
            return 1.0  # Not applicable
        
        # Check for progression indicators
        progression_keywords = ['junior', 'mid', 'senior', 'lead', 'principal', 'progression', 'advance', 'grow']
        answer = response_data['answer'].lower()
        
        found_progression = sum(1 for keyword in progression_keywords if keyword in answer)
        
        return min(found_progression / 3, 1.0)  # Expect at least 3 progression indicators
    
    def _aggregate_metrics(self, results: List[EvaluationResult]) -> Dict[str, float]:
        """Aggregate metrics across all samples"""
        if not results:
            return {}
        
        # Collect all metrics
        all_metrics = {}
        for result in results:
            for metric, value in result.metrics.items():
                if metric not in all_metrics:
                    all_metrics[metric] = []
                all_metrics[metric].append(value)
        
        # Calculate statistics
        aggregated = {}
        for metric, values in all_metrics.items():
            aggregated[f"{metric}_mean"] = np.mean(values)
            aggregated[f"{metric}_std"] = np.std(values)
            aggregated[f"{metric}_min"] = np.min(values)
            aggregated[f"{metric}_max"] = np.max(values)
            aggregated[f"{metric}_median"] = np.median(values)
        
        # Add latency statistics
        latencies = [r.latency_ms for r in results]
        aggregated["latency_mean_ms"] = np.mean(latencies)
        aggregated["latency_p95_ms"] = np.percentile(latencies, 95)
        aggregated["latency_p99_ms"] = np.percentile(latencies, 99)
        
        return aggregated
    
    def _run_statistical_tests(self, results: List[EvaluationResult]) -> Dict[str, Any]:
        """Run statistical tests on results"""
        tests = {}
        
        # Group by query type
        by_type = {}
        for result in results:
            qtype = result.query_type
            if qtype not in by_type:
                by_type[qtype] = []
            by_type[qtype].append(result)
        
        # ANOVA for answer correctness across query types
        if len(by_type) > 1:
            groups = []
            for qtype, type_results in by_type.items():
                scores = [r.metrics.get('answer_correctness', 0) for r in type_results]
                groups.append(scores)
            
            f_stat, p_value = stats.f_oneway(*groups)
            tests['anova_query_types'] = {
                'f_statistic': f_stat,
                'p_value': p_value,
                'significant': p_value < 0.05
            }
        
        # Test for normality
        all_scores = [r.metrics.get('answer_correctness', 0) for r in results]
        if len(all_scores) > 8:
            stat, p_value = stats.normaltest(all_scores)
            tests['normality_test'] = {
                'statistic': stat,
                'p_value': p_value,
                'is_normal': p_value > 0.05
            }
        
        return tests
    
    def _perform_statistical_analysis(
        self,
        all_results: Dict[str, AblationResult]
    ) -> Dict[str, Any]:
        """Perform statistical analysis across configurations"""
        analysis = {}
        
        # Compare baseline to other configurations
        if 'baseline' in all_results and len(all_results) > 1:
            baseline_scores = [
                r.metrics.get('answer_correctness', 0) 
                for r in all_results['baseline'].results
            ]
            
            comparisons = {}
            for config_name, ablation_result in all_results.items():
                if config_name == 'baseline':
                    continue
                    
                config_scores = [
                    r.metrics.get('answer_correctness', 0) 
                    for r in ablation_result.results
                ]
                
                # Paired t-test
                if len(baseline_scores) == len(config_scores):
                    t_stat, p_value = stats.ttest_rel(baseline_scores, config_scores)
                    comparisons[config_name] = {
                        't_statistic': t_stat,
                        'p_value': p_value,
                        'significant': p_value < 0.05,
                        'mean_difference': np.mean(config_scores) - np.mean(baseline_scores)
                    }
            
            analysis['baseline_comparisons'] = comparisons
        
        # Overall statistics
        all_scores = []
        for result in all_results.values():
            scores = [r.metrics.get('answer_correctness', 0) for r in result.results]
            all_scores.extend(scores)
        
        analysis['overall_statistics'] = {
            'total_samples': len(all_scores),
            'mean_score': np.mean(all_scores),
            'std_score': np.std(all_scores),
            'min_score': np.min(all_scores),
            'max_score': np.max(all_scores)
        }
        
        return analysis
    
    def _generate_comprehensive_report(
        self,
        all_results: Dict[str, AblationResult],
        analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate comprehensive evaluation report"""
        report = {
            "summary": {
                "evaluation_date": datetime.now().isoformat(),
                "configurations_tested": list(all_results.keys()),
                "total_samples": sum(len(r.results) for r in all_results.values())
            },
            "configuration_results": {},
            "statistical_analysis": analysis,
            "recommendations": []
        }
        
        # Configuration summaries
        for config_name, ablation_result in all_results.items():
            report["configuration_results"][config_name] = {
                "aggregate_metrics": ablation_result.aggregate_metrics,
                "statistical_tests": ablation_result.statistical_tests,
                "sample_count": len(ablation_result.results)
            }
        
        # Generate recommendations
        if 'baseline' in all_results:
            baseline_correctness = all_results['baseline'].aggregate_metrics.get('answer_correctness_mean', 0)
            
            for config_name, result in all_results.items():
                if config_name == 'baseline':
                    continue
                    
                config_correctness = result.aggregate_metrics.get('answer_correctness_mean', 0)
                
                if config_correctness > baseline_correctness * 1.05:
                    report["recommendations"].append(
                        f"Consider using {config_name} configuration - "
                        f"{(config_correctness - baseline_correctness) * 100:.1f}% improvement"
                    )
        
        return report
    
    def _save_results(
        self,
        all_results: Dict[str, AblationResult],
        analysis: Dict[str, Any],
        report: Dict[str, Any]
    ):
        """Save all evaluation results"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save detailed results
        for config_name, ablation_result in all_results.items():
            # Convert results to dataframe
            results_data = []
            for result in ablation_result.results:
                row = {
                    'query_id': result.query_id,
                    'query': result.query,
                    'query_type': result.query_type,
                    'predicted_answer': result.predicted_answer,
                    'ground_truth_answer': result.ground_truth_answer,
                    'latency_ms': result.latency_ms,
                    **result.metrics
                }
                results_data.append(row)
            
            df = pd.DataFrame(results_data)
            df.to_csv(
                self.output_dir / f"results_{config_name}_{timestamp}.csv",
                index=False
            )
        
        # Save analysis
        with open(self.output_dir / f"analysis_{timestamp}.json", 'w') as f:
            json.dump(analysis, f, indent=2, default=str)
        
        # Save report
        with open(self.output_dir / f"report_{timestamp}.json", 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        # Generate visualizations
        self._generate_visualizations(all_results, timestamp)
        
        # Log to wandb if enabled
        if self.enable_wandb:
            self.wandb.log(report)
    
    def _generate_visualizations(
        self,
        all_results: Dict[str, AblationResult],
        timestamp: str
    ):
        """Generate evaluation visualizations"""
        # Metric comparison across configurations
        plt.figure(figsize=(12, 8))
        
        metrics_to_plot = [
            'answer_correctness_mean',
            'context_precision_mean',
            'faithfulness_mean',
            'answer_relevancy_mean'
        ]
        
        config_names = list(all_results.keys())
        metric_values = {metric: [] for metric in metrics_to_plot}
        
        for config in config_names:
            for metric in metrics_to_plot:
                value = all_results[config].aggregate_metrics.get(metric, 0)
                metric_values[metric].append(value)
        
        x = np.arange(len(config_names))
        width = 0.2
        
        fig, ax = plt.subplots(figsize=(12, 8))
        
        for i, (metric, values) in enumerate(metric_values.items()):
            ax.bar(x + i * width, values, width, label=metric.replace('_mean', ''))
        
        ax.set_xlabel('Configuration')
        ax.set_ylabel('Score')
        ax.set_title('Metric Comparison Across Configurations')
        ax.set_xticks(x + width * 1.5)
        ax.set_xticklabels(config_names)
        ax.legend()
        
        plt.tight_layout()
        plt.savefig(self.output_dir / f"metric_comparison_{timestamp}.png")
        plt.close()
        
        # Latency distribution
        plt.figure(figsize=(10, 6))
        
        for config_name, result in all_results.items():
            latencies = [r.latency_ms for r in result.results]
            plt.hist(latencies, bins=30, alpha=0.5, label=config_name)
        
        plt.xlabel('Latency (ms)')
        plt.ylabel('Count')
        plt.title('Latency Distribution Across Configurations')
        plt.legend()
        
        plt.tight_layout()
        plt.savefig(self.output_dir / f"latency_distribution_{timestamp}.png")
        plt.close()
    
    def _apply_configuration(self, rag_system, config: Dict[str, Any]):
        """Apply configuration changes to RAG system"""
        # This needs to be implemented based on your system's architecture
        # Example configurations might include:
        # - Disabling graph retriever
        # - Disabling embedding retriever
        # - Changing reranker settings
        # - Modifying top_k values
        
        # For now, return the original system
        # You'll need to implement this based on your system 