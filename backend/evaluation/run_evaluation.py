"""
Main Evaluation Script for Hybrid RAG System
Run comprehensive evaluation with ablation studies
"""

import asyncio
import argparse
import logging
import os
from pathlib import Path
from datetime import datetime
import json
import sys
from typing import Optional

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from evaluation.dataset_generator import DatasetGenerator
from evaluation.evaluator import HybridRAGEvaluator
from evaluation.ablation_configs import AblationConfigManager, ComponentType
from evaluation.rag_adapter import HybridRAGSystem
from app.core.containers.application_container import ApplicationContainer
from app.core.config import Configs

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class EvaluationPipeline:
    """Complete evaluation pipeline"""
    
    def __init__(self, config_path: Optional[str] = None):
        # Load configuration
        self.settings = Configs()
        if config_path:
            self.settings.load_from_file(config_path)
        
        # Initialize containers
        self.container = ApplicationContainer()
        # self.container.config.from_dict(self.settings.model_dump())
        
        # Initialize components
        self.dataset_generator = None
        self.evaluator = None
        self.rag_system = None
        
    async def initialize(self):
        """Initialize all components"""
        logger.info("Initializing evaluation pipeline...")
        
        # Initialize dataset generator
        self.dataset_generator = DatasetGenerator(
            api_key=self.settings.GEMINI_TOKEN,
            output_dir="evaluation_datasets"
        )
        
        # Initialize evaluator
        self.evaluator = HybridRAGEvaluator(
            output_dir="evaluation_results",
            enable_wandb=False  # Set to True if you want to use Weights & Biases
        )
        
        # Initialize RAG system
        await self._initialize_rag_system()
        
        logger.info("Evaluation pipeline initialized successfully")
    
    async def _initialize_rag_system(self):
        """Initialize the RAG system from containers"""
        # Get components from containers
        chat_engine = self.container.chatbot().chat_engine()
        job_retriever = self.container.chatbot().job_retriever()
        course_retriever = self.container.chatbot().course_retriever()
        
        # Create RAG system wrapper
        self.rag_system = HybridRAGSystem(
            chat_engine=chat_engine,
            job_retriever=job_retriever,
            course_retriever=course_retriever
        )
        
        logger.info("RAG system initialized with configuration:")
        logger.info(json.dumps(self.rag_system.get_config_dict(), indent=2))
    
    async def generate_dataset(
        self,
        num_samples_per_type: int = 20,
        use_existing: Optional[str] = None
    ):
        """Generate or load evaluation dataset"""
        if use_existing:
            logger.info(f"Loading existing dataset from {use_existing}")
            import pandas as pd
            return pd.read_csv(use_existing)
        
        logger.info("Generating new evaluation dataset...")
        dataset = await self.dataset_generator.generate_dataset(
            num_samples_per_type=num_samples_per_type,
            include_hard_negatives=True,
            include_multi_hop=True
        )
        
        logger.info(f"Generated dataset with {len(dataset)} samples")
        return dataset
    
    async def run_evaluation(
        self,
        dataset,
        ablation_configs: Optional[list] = None,
        quick_test: bool = False
    ):
        """Run complete evaluation"""
        logger.info("Starting evaluation...")
        
        # Use subset for quick testing
        if quick_test:
            dataset = dataset.head(10)
            logger.info("Running quick test with 10 samples")
        
        # Prepare configurations for ablation
        if ablation_configs is None:
            # Use default ablation configurations
            config_manager = AblationConfigManager()
            ablation_configs = config_manager.get_configs()
        
        # Convert configs to format expected by evaluator
        configurations = []
        for config in ablation_configs:
            configurations.append({
                "name": config.name,
                "modifications": config.modifications
            })
        
        # Run evaluation
        results = await self.evaluator.evaluate_system(
            self.rag_system,
            dataset,
            configurations
        )
        
        logger.info("Evaluation completed successfully")
        return results
    
    async def run_specific_ablation(
        self,
        dataset,
        component_types: list[ComponentType]
    ):
        """Run ablation study for specific component types"""
        config_manager = AblationConfigManager()
        configs = config_manager.get_configs(component_types)
        
        return await self.run_evaluation(dataset, configs)


async def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Run Hybrid RAG Evaluation")
    
    parser.add_argument(
        "--config",
        type=str,
        help="Path to configuration file"
    )
    
    parser.add_argument(
        "--dataset",
        type=str,
        help="Path to existing dataset CSV file"
    )
    
    parser.add_argument(
        "--num-samples",
        type=int,
        default=20,
        help="Number of samples per query type (default: 20)"
    )
    
    parser.add_argument(
        "--quick-test",
        action="store_true",
        help="Run quick test with limited samples"
    )
    
    parser.add_argument(
        "--ablation-study",
        choices=["all", "retriever", "weights", "topk", "reranker"],
        default="all",
        help="Type of ablation study to run"
    )
    
    parser.add_argument(
        "--output-dir",
        type=str,
        default="evaluation_results",
        help="Directory to save results"
    )
    
    args = parser.parse_args()
    
    # Create pipeline
    pipeline = EvaluationPipeline(config_path=args.config)
    
    try:
        # Initialize
        await pipeline.initialize()
        
        # Generate or load dataset
        dataset = await pipeline.generate_dataset(
            num_samples_per_type=args.num_samples,
            use_existing=args.dataset
        )
        
        # Determine which ablations to run
        if args.ablation_study == "all":
            ablation_configs = None  # Use all default configs
        else:
            component_map = {
                "retriever": [ComponentType.EMBEDDING_RETRIEVER, ComponentType.GRAPH_RETRIEVER],
                "weights": [ComponentType.HYBRID_WEIGHTS],
                "topk": [ComponentType.TOP_K],
                "reranker": [ComponentType.RERANKER]
            }
            
            component_types = component_map.get(args.ablation_study, [])
            results = await pipeline.run_specific_ablation(dataset, component_types)
        
        # Run evaluation
        if args.ablation_study == "all":
            results = await pipeline.run_evaluation(
                dataset,
                ablation_configs=None,
                quick_test=args.quick_test
            )
        
        # Print summary
        print("\n" + "="*60)
        print("EVALUATION SUMMARY")
        print("="*60)
        
        for config_name, ablation_result in results["results"].items():
            print(f"\nConfiguration: {config_name}")
            print("-"*40)
            
            # Print key metrics
            metrics = ablation_result.aggregate_metrics
            print(f"Answer Correctness: {metrics.get('answer_correctness_mean', 0):.3f} "
                  f"(±{metrics.get('answer_correctness_std', 0):.3f})")
            print(f"Context Precision: {metrics.get('context_precision_mean', 0):.3f}")
            print(f"Faithfulness: {metrics.get('faithfulness_mean', 0):.3f}")
            print(f"Answer Relevancy: {metrics.get('answer_relevancy_mean', 0):.3f}")
            print(f"Latency: {metrics.get('latency_mean_ms', 0):.1f}ms "
                  f"(p95: {metrics.get('latency_p95_ms', 0):.1f}ms)")
        
        # Print statistical comparisons
        if "baseline_comparisons" in results["analysis"]:
            print("\n" + "="*60)
            print("STATISTICAL COMPARISONS VS BASELINE")
            print("="*60)
            
            for config, comparison in results["analysis"]["baseline_comparisons"].items():
                print(f"\n{config}:")
                print(f"  Mean difference: {comparison['mean_difference']:.3f}")
                print(f"  P-value: {comparison['p_value']:.4f}")
                print(f"  Significant: {'Yes' if comparison['significant'] else 'No'}")
        
        print("\n" + "="*60)
        print(f"Results saved to: {pipeline.evaluator.output_dir}")
        print("="*60)
        
    except Exception as e:
        logger.error(f"Evaluation failed: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    asyncio.run(main()) 