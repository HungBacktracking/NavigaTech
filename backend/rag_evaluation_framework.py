"""
Comprehensive RAG Evaluation Framework for Academic Research
===========================================================
This framework evaluates multiple RAG approaches systematically:
1. Baseline (LLM only, no retrieval)
2. Dense Embedding RAG
3. Hybrid Search RAG (Dense + Sparse embeddings)
4. Graph RAG
5. Hybrid RAG (Embedding + Graph)
"""

import traceback
import asyncio
from logging import raiseExceptions
from typing import List, Dict, Any, Optional, Tuple
import pandas as pd
import numpy as np
from datetime import datetime
import time
import json
from dataclasses import dataclass, asdict
from enum import Enum
import matplotlib.pyplot as plt
import seaborn as sns

# RAGAS imports
from ragas import evaluate
from ragas.metrics import (
    answer_relevancy,
    faithfulness,
    context_recall,
    context_precision,
    answer_correctness
)
from datasets import Dataset

# LlamaIndex imports
from llama_index.core import QueryBundle
from llama_index.core.retrievers import BaseRetriever
from llama_index.core.schema import NodeWithScore

# Your app imports
from app.core.containers.application_container import ApplicationContainer
from app.chatbot.hybrid_retriever import HybridRetriever
from app.chatbot.graph_retriever import Neo4jGraphRetriever


class RAGApproach(Enum):
    """Enumeration of different RAG approaches to evaluate"""
    BASELINE = "baseline"  # No retrieval, just LLM
    DENSE_EMBEDDING = "dense_embedding"  # Traditional dense embedding RAG
    HYBRID_SEARCH = "hybrid_search"  # Dense + Sparse embedding
    GRAPH_ONLY = "graph_only"  # Graph-based retrieval only
    HYBRID_RAG = "hybrid_rag"  # Embedding + Graph hybrid
    RERANKED_DENSE = "reranked_dense"  # Dense embedding with reranking
    RERANKED_HYBRID = "reranked_hybrid"  # Hybrid with reranking


@dataclass
class EvaluationResult:
    """Store evaluation results for each approach"""
    approach: RAGApproach
    question: str
    answer: str
    contexts: List[str]
    ground_truth: str
    latency_ms: float
    retrieval_time_ms: float
    generation_time_ms: float
    num_contexts: int
    # RAGAS metrics will be added after batch evaluation
    ragas_metrics: Optional[Dict[str, float]] = None


@dataclass
class ExperimentConfig:
    """Configuration for each experiment"""
    approach: RAGApproach
    top_k: int = 10
    rerank: bool = False
    embedding_weight: float = 0.5
    graph_weight: float = 0.5
    temperature: float = 0.3
    max_tokens: int = 500


class ComprehensiveRAGEvaluator:
    """
    Comprehensive evaluator for comparing different RAG approaches
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize the evaluator with all necessary components"""
        # Initialize containers
        self.app_container = ApplicationContainer()
        
        # Get core components
        self.llm = self.app_container.AI.llm_gemini()
        self.embeddings = self.app_container.AI.embed_model()
        
        # Get retrievers
        self.job_embedding_retriever = self.app_container.chatbot.job_embedding_retriever()
        self.course_embedding_retriever = self.app_container.chatbot.course_embedding_retriever()
        self.job_graph_retriever = self.app_container.chatbot.job_graph_retriever()
        self.course_graph_retriever = self.app_container.chatbot.course_graph_retriever()
        self.reranker = self.app_container.chatbot.reranker()
        
        # Storage for results
        self.all_results: List[EvaluationResult] = []
        
    def create_retriever_for_approach(
        self, 
        approach: RAGApproach, 
        config: ExperimentConfig,
        retriever_type: str = "job"
    ) -> Optional[BaseRetriever]:
        """Create the appropriate retriever based on the approach"""
        
        if approach == RAGApproach.BASELINE:
            # No retriever for baseline
            return None
            
        elif approach == RAGApproach.DENSE_EMBEDDING:
            # Dense embedding only
            if retriever_type == "job":
                return self.job_embedding_retriever
            else:
                return self.course_embedding_retriever
                
        elif approach == RAGApproach.HYBRID_SEARCH:
            # This uses the Qdrant hybrid search (dense + sparse)
            # Already configured in job_embedding_retriever with mode="hybrid"
            if retriever_type == "job":
                return self.job_embedding_retriever
            else:
                return self.course_embedding_retriever
                
        elif approach == RAGApproach.GRAPH_ONLY:
            # Graph retrieval only
            if retriever_type == "job":
                return self.job_graph_retriever
            else:
                return self.course_graph_retriever
                
        elif approach in [RAGApproach.HYBRID_RAG, RAGApproach.RERANKED_HYBRID]:
            # Hybrid retriever combining embedding and graph
            embedding_retriever = self.job_embedding_retriever if retriever_type == "job" else self.course_embedding_retriever
            graph_retriever = self.job_graph_retriever if retriever_type == "job" else self.course_graph_retriever
            
            return HybridRetriever(
                embedding_retriever=embedding_retriever,
                graph_retriever=graph_retriever,
                reranker=self.reranker if config.rerank else None,
                embedding_weight=config.embedding_weight,
                graph_weight=config.graph_weight,
                top_k=config.top_k
            )
            
        elif approach == RAGApproach.RERANKED_DENSE:
            # Dense embedding with reranking
            # We'll need to wrap the retriever with reranking logic
            base_retriever = self.job_embedding_retriever if retriever_type == "job" else self.course_embedding_retriever
            # For now, return the base retriever and handle reranking separately
            return base_retriever
            
        else:
            raise ValueError(f"Unknown approach: {approach}")
    
    async def evaluate_single_question(
        self,
        question: str,
        ground_truth: str,
        approach: RAGApproach,
        config: ExperimentConfig
    ) -> EvaluationResult:
        """Evaluate a single question with a specific approach"""
        
        start_time = time.time()
        retrieval_time = 0
        contexts = []
        
        # Determine retriever type based on question
        retriever_type = "course" if any(word in question.lower() for word in ['course', 'learn', 'study']) else "job"
        
        # Create retriever for this approach
        retriever = self.create_retriever_for_approach(approach, config, retriever_type)
        
        # Retrieve contexts if not baseline
        if retriever is not None:
            retrieval_start = time.time()
            nodes = await retriever.aretrieve(QueryBundle(query_str=question))
            retrieval_time = (time.time() - retrieval_start) * 1000  # Convert to ms
            
            # Apply reranking if needed
            if config.rerank and approach == RAGApproach.RERANKED_DENSE:
                nodes = self.reranker.postprocess_nodes(nodes, QueryBundle(query_str=question))
            
            contexts = [node.node.text for node in nodes[:config.top_k]]
        
        # Generate answer
        generation_start = time.time()
        
        if approach == RAGApproach.BASELINE:
            # Baseline: No context, just question
            prompt = f"Question: {question}\n\nProvide a comprehensive answer:"
        else:
            # With retrieval: Include contexts
            context_str = "\n\n".join([f"Context {i+1}: {ctx}" for i, ctx in enumerate(contexts)])
            prompt = f"""Based on the following contexts, answer the question.

Contexts:
{context_str}

Question: {question}

Answer:"""

        request_options = {
            "temperature": config.temperature,
            "maxOutputTokens": config.max_tokens,
        }

        response = await self.llm.acomplete(prompt, request_options)
        answer = response.text.strip()
        
        generation_time = (time.time() - generation_start) * 1000  # Convert to ms
        total_latency = (time.time() - start_time) * 1000  # Convert to ms
        
        return EvaluationResult(
            approach=approach,
            question=question,
            answer=answer,
            contexts=contexts,
            ground_truth=ground_truth,
            latency_ms=total_latency,
            retrieval_time_ms=retrieval_time,
            generation_time_ms=generation_time,
            num_contexts=len(contexts)
        )
    
    def create_test_dataset(self) -> List[Dict[str, str]]:
        """Create a comprehensive test dataset for evaluation"""
        test_cases = [
            # Job-related questions
            {
                "question": "What skills are required for a Data Engineer position?",
                "type": "job",
                "difficulty": "easy"
            },
            {
                "question": "What are the main responsibilities of a Machine Learning Engineer?",
                "type": "job",
                "difficulty": "medium"
            },
            {
                "question": "How does a DevOps Engineer differ from a System Administrator?",
                "type": "job",
                "difficulty": "hard"
            },
            {
                "question": "What is the typical career progression for a Software Engineer?",
                "type": "job",
                "difficulty": "medium"
            },
            {
                "question": "What technical stack should a Full Stack Developer master?",
                "type": "job",
                "difficulty": "medium"
            },
            
            # Course-related questions
            {
                "question": "What are the best Python courses for beginners?",
                "type": "course",
                "difficulty": "easy"
            },
            {
                "question": "How can I learn cloud computing from scratch?",
                "type": "course",
                "difficulty": "medium"
            },
            {
                "question": "What courses should I take to transition into data science?",
                "type": "course",
                "difficulty": "hard"
            },
            {
                "question": "Which online platforms offer the best machine learning courses?",
                "type": "course",
                "difficulty": "medium"
            },
            {
                "question": "What is the recommended learning path for becoming a React developer?",
                "type": "course",
                "difficulty": "medium"
            }
        ]
        
        return test_cases
    
    async def generate_ground_truth(self, test_cases: List[Dict]) -> List[Dict]:
        """Generate ground truth using the best available approach (hybrid RAG)"""
        print("🎯 Generating ground truth using Hybrid RAG...")
        
        config = ExperimentConfig(
            approach=RAGApproach.HYBRID_RAG,
            top_k=15,
            rerank=True,
            temperature=0.1  # Low temperature for consistency
        )
        
        ground_truth_data = []
        
        for i, test_case in enumerate(test_cases):
            print(f"  Processing {i+1}/{len(test_cases)}: {test_case['question'][:50]}...")
            
            # Get high-quality answer using hybrid approach
            result = await self.evaluate_single_question(
                question=test_case['question'],
                ground_truth="",  # Temporary
                approach=RAGApproach.HYBRID_RAG,
                config=config
            )
            
            ground_truth_data.append({
                "question": test_case['question'],
                "ground_truth": result.answer,
                "type": test_case['type'],
                "difficulty": test_case['difficulty'],
                "source_contexts": result.contexts
            })
        
        return ground_truth_data
    
    async def run_comprehensive_evaluation(self, test_cases: List[Dict]) -> pd.DataFrame:
        """Run evaluation across all approaches"""
        
        # Define experiment configurations
        experiments = [
            ExperimentConfig(approach=RAGApproach.BASELINE, top_k=0),
            ExperimentConfig(approach=RAGApproach.DENSE_EMBEDDING, top_k=10),
            ExperimentConfig(approach=RAGApproach.HYBRID_SEARCH, top_k=10),
            ExperimentConfig(approach=RAGApproach.GRAPH_ONLY, top_k=10),
            ExperimentConfig(approach=RAGApproach.HYBRID_RAG, top_k=10),
            ExperimentConfig(approach=RAGApproach.RERANKED_DENSE, top_k=10, rerank=True),
            ExperimentConfig(approach=RAGApproach.RERANKED_HYBRID, top_k=10, rerank=True),
        ]
        
        all_results = []
        
        # Run experiments
        for config in experiments:
            print(f"\n📊 Evaluating {config.approach.value}...")
            
            for test_case in test_cases:
                result = await self.evaluate_single_question(
                    question=test_case['question'],
                    ground_truth=test_case['ground_truth'],
                    approach=config.approach,
                    config=config
                )
                
                # Add metadata
                result_dict = asdict(result)
                result_dict.update({
                    'question_type': test_case['type'],
                    'difficulty': test_case['difficulty']
                })
                all_results.append(result_dict)
            
            print(f"  ✓ Completed {len(test_cases)} questions")
        
        # Convert to DataFrame
        results_df = pd.DataFrame(all_results)

        # Run RAGAS evaluation for each approach
        print("\n🔍 Running RAGAS evaluation...")
        results_df = await self.add_ragas_metrics(results_df)
        
        return results_df
    
    async def add_ragas_metrics(self, results_df: pd.DataFrame) -> pd.DataFrame:
        """Add RAGAS metrics to results"""
        results_df['approach'] = results_df['approach'].map(lambda a: a.value if isinstance(a, RAGApproach) else a)

        # Group by approach for batch evaluation
        for approach in RAGApproach:
            approach_data = results_df[results_df['approach'] == approach.value]
            
            if len(approach_data) == 0:
                continue
            
            # Prepare data for RAGAS
            dataset_dict = {
                "question": approach_data['question'].tolist(),
                "answer": approach_data['answer'].tolist(),
                "contexts": approach_data['contexts'].tolist(),
                "ground_truth": approach_data['ground_truth'].tolist()
            }
            
            dataset = Dataset.from_dict(dataset_dict)
            
            # Evaluate with RAGAS
            try:
                ragas_results = evaluate(
                    dataset,
                    metrics=[
                        answer_relevancy,
                        faithfulness,
                        context_recall,
                        context_precision,
                        answer_correctness
                    ],
                    raise_exceptions = True
                )

                scores_df = ragas_results.to_pandas()
                # Add metrics to dataframe
                for idx, row_idx in enumerate(approach_data.index):
                    results_df.at[row_idx, 'answer_relevancy'] = scores_df.loc[idx, 'answer_relevancy']
                    results_df.at[row_idx, 'faithfulness'] = scores_df.loc[idx, 'faithfulness']
                    results_df.at[row_idx, 'context_recall'] = scores_df.loc[idx, 'context_recall'] if 'context_recall' in scores_df else None
                    results_df.at[row_idx, 'context_precision'] = scores_df.loc[idx, 'context_precision'] if 'context_precision' in scores_df else None
                    results_df.at[row_idx, 'answer_correctness'] = scores_df.loc[idx, 'answer_correctness'] if 'answer_correctness' in scores_df else None
                    
            except Exception as e:
                print(f"  ⚠️  Error evaluating {approach.value}: {e!r}")
                # 2) In cả traceback để biết dòng nào nó vấp
                traceback.print_exc()
                # Add None values for this approach
                for idx in approach_data.index:
                    results_df.at[idx, 'answer_relevancy'] = None
                    results_df.at[idx, 'faithfulness'] = None
                    results_df.at[idx, 'context_recall'] = None
                    results_df.at[idx, 'context_precision'] = None
                    results_df.at[idx, 'answer_correctness'] = None
        
        return results_df
    
    def generate_analysis_report(self, results_df: pd.DataFrame) -> Dict[str, Any]:
        """Generate comprehensive analysis report"""
        
        report = {
            "summary_statistics": {},
            "approach_comparison": {},
            "latency_analysis": {}
        }
        
        # Summary statistics by approach
        metrics = ['answer_relevancy', 'faithfulness', 'context_recall', 
                   'context_precision', 'answer_correctness', 'latency_ms']
        
        for approach in RAGApproach:
            approach_data = results_df[results_df['approach'] == approach.value]
            if len(approach_data) > 0:
                stats = {}
                for metric in metrics:
                    if metric in approach_data.columns:
                        stats[metric] = {
                            'mean': approach_data[metric].mean(),
                            'std': approach_data[metric].std(),
                            'min': approach_data[metric].min(),
                            'max': approach_data[metric].max()
                        }
                report["summary_statistics"][approach.value] = stats
        
        # Performance comparison
        comparison_df = results_df.groupby('approach')[metrics].mean()
        report["approach_comparison"] = comparison_df.to_dict()
        
        # Latency breakdown
        latency_df = results_df.groupby('approach')[
            ['latency_ms', 'retrieval_time_ms', 'generation_time_ms']
        ].mean()
        report["latency_analysis"] = latency_df.to_dict()
        
        return report
    
    def create_visualizations(self, results_df: pd.DataFrame, output_dir: str = "evaluation_results"):
        """Create visualizations for the paper"""
        import os
        os.makedirs(output_dir, exist_ok=True)
        
        # Set style
        plt.style.use('seaborn-v0_8-darkgrid')
        
        # 1. Overall Performance Comparison
        fig, ax = plt.subplots(figsize=(10, 6))
        metrics_to_plot = ['answer_relevancy', 'faithfulness', 'answer_correctness']
        
        approach_means = results_df.groupby('approach')[metrics_to_plot].mean()
        approach_means.plot(kind='bar', ax=ax)
        
        ax.set_title('RAG Approach Performance Comparison', fontsize=14)
        ax.set_xlabel('Approach', fontsize=12)
        ax.set_ylabel('Score', fontsize=12)
        ax.legend(title='Metrics')
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        plt.savefig(f"{output_dir}/overall_performance.png", dpi=300)
        plt.close()
        
        # 2. Latency Analysis
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
        
        # Total latency
        latency_data = results_df.groupby('approach')['latency_ms'].mean().sort_values()
        latency_data.plot(kind='barh', ax=ax1, color='skyblue')
        ax1.set_title('Average Total Latency by Approach', fontsize=12)
        ax1.set_xlabel('Latency (ms)', fontsize=10)
        
        # Latency breakdown
        latency_breakdown = results_df.groupby('approach')[
            ['retrieval_time_ms', 'generation_time_ms']
        ].mean()
        latency_breakdown.plot(kind='bar', stacked=True, ax=ax2)
        ax2.set_title('Latency Breakdown by Approach', fontsize=12)
        ax2.set_ylabel('Time (ms)', fontsize=10)
        ax2.legend(title='Component')
        plt.xticks(rotation=45, ha='right')
        
        plt.tight_layout()
        plt.savefig(f"{output_dir}/latency_analysis.png", dpi=300)
        plt.close()
        
        # 3. Performance by Question Type
        fig, ax = plt.subplots(figsize=(10, 6))
        
        type_perf = results_df.pivot_table(
            values='answer_correctness',
            index='approach',
            columns='question_type',
            aggfunc='mean'
        )
        
        type_perf.plot(kind='bar', ax=ax)
        ax.set_title('Performance by Question Type', fontsize=14)
        ax.set_xlabel('Approach', fontsize=12)
        ax.set_ylabel('Answer Correctness Score', fontsize=12)
        ax.legend(title='Question Type')
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        plt.savefig(f"{output_dir}/performance_by_type.png", dpi=300)
        plt.close()
        
        # 4. Heatmap of all metrics
        fig, ax = plt.subplots(figsize=(10, 8))
        
        metrics_matrix = results_df.groupby('approach')[
            ['answer_relevancy', 'faithfulness', 'context_recall',
             'context_precision', 'answer_correctness']
        ].mean()
        
        sns.heatmap(metrics_matrix.T, annot=True, fmt='.3f', cmap='YlOrRd', ax=ax)
        ax.set_title('Comprehensive Metrics Heatmap', fontsize=14)
        plt.tight_layout()
        plt.savefig(f"{output_dir}/metrics_heatmap.png", dpi=300)
        plt.close()
        
        print(f"✅ Visualizations saved to {output_dir}/")
    
    def export_for_paper(self, results_df: pd.DataFrame, analysis_report: Dict, output_dir: str = "evaluation_results"):
        """Export results in formats suitable for academic paper"""
        import os
        os.makedirs(output_dir, exist_ok=True)
        
        # 1. LaTeX tables
        latex_tables = {}
        
        # Summary statistics table
        summary_stats = results_df.groupby('approach')[
            ['answer_relevancy', 'faithfulness', 'answer_correctness', 'latency_ms']
        ].agg(['mean', 'std'])
        
        latex_tables['summary_stats'] = summary_stats.to_latex(float_format="%.3f")
        
        # Save LaTeX tables
        with open(f"{output_dir}/latex_tables.tex", 'w') as f:
            for name, table in latex_tables.items():
                f.write(f"% {name}\n")
                f.write(table)
                f.write("\n\n")
        
        # 2. CSV files for reproducibility
        results_df.to_csv(f"{output_dir}/full_results.csv", index=False)
        
        # 3. JSON report
        with open(f"{output_dir}/analysis_report.json", 'w') as f:
            json.dump(analysis_report, f, indent=2)
        
        # 4. Summary statistics CSV
        summary_df = results_df.groupby('approach').agg({
            'answer_relevancy': ['mean', 'std'],
            'faithfulness': ['mean', 'std'],
            'context_recall': ['mean', 'std'],
            'context_precision': ['mean', 'std'],
            'answer_correctness': ['mean', 'std'],
            'latency_ms': ['mean', 'std'],
            'retrieval_time_ms': ['mean', 'std'],
            'generation_time_ms': ['mean', 'std']
        }).round(3)
        
        summary_df.to_csv(f"{output_dir}/summary_statistics.csv")
        
        print(f"📄 Results exported to {output_dir}/")


async def main():
    """Main evaluation pipeline"""
    print("🚀 Starting Comprehensive RAG Evaluation for Research Paper")
    print("=" * 60)
    
    # Initialize evaluator
    evaluator = ComprehensiveRAGEvaluator()
    
    # Create test dataset
    print("\n📋 Creating test dataset...")
    test_cases = evaluator.create_test_dataset()
    print(f"Created {len(test_cases)} test cases")
    
    # Generate ground truth
    print("\n🎯 Generating ground truth...")
    test_cases_with_truth = await evaluator.generate_ground_truth(test_cases)
    
    # Save ground truth for reference
    pd.DataFrame(test_cases_with_truth).to_csv("ground_truth_data.csv", index=False)
    print("Ground truth saved to ground_truth_data.csv")
    
    # Run comprehensive evaluation
    print("\n🔬 Running comprehensive evaluation across all approaches...")
    results_df = await evaluator.run_comprehensive_evaluation(test_cases_with_truth)
    
    # Generate analysis report
    print("\n📊 Generating analysis report...")
    analysis_report = evaluator.generate_analysis_report(results_df)
    
    # Create visualizations
    print("\n📈 Creating visualizations...")
    evaluator.create_visualizations(results_df)
    
    # Export results for paper
    print("\n📄 Exporting results for academic paper...")
    evaluator.export_for_paper(results_df, analysis_report)
    
    # Print summary
    print("\n" + "=" * 60)
    print("EVALUATION COMPLETE")
    print("=" * 60)
    
    # Print key findings
    print("\n🏆 Top Performing Approaches:")
    top_approaches = results_df.groupby('approach')['answer_correctness'].mean().sort_values(ascending=False)
    for i, (approach, score) in enumerate(top_approaches.head(3).items()):
        print(f"  {i+1}. {approach}: {score:.3f}")
    
    print("\n⚡ Fastest Approaches:")
    fastest = results_df.groupby('approach')['latency_ms'].mean().sort_values()
    for i, (approach, latency) in enumerate(fastest.head(3).items()):
        print(f"  {i+1}. {approach}: {latency:.1f}ms")
    
    print("\n✅ All results saved to evaluation_results/")
    print("Use these results for your research paper!")


if __name__ == "__main__":
    asyncio.run(main()) 