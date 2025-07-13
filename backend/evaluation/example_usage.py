"""
Example usage of the Hybrid RAG Evaluation Framework
This script demonstrates how to evaluate your RAG system
"""

import asyncio
import os
from pathlib import Path

# Assuming you're running from the project root
from evaluation.dataset_generator import DatasetGenerator
from evaluation.evaluator import HybridRAGEvaluator
from evaluation.ablation_configs import AblationConfigManager, ComponentType
from evaluation.rag_adapter import HybridRAGSystem, ChatEngineAdapter
from app.core.containers.application_container import ApplicationContainer


async def example_basic_evaluation():
    """Basic evaluation example"""
    print("="*60)
    print("BASIC EVALUATION EXAMPLE")
    print("="*60)
    
    # 1. Initialize your application container
    container = ApplicationContainer()
    
    # 2. Get your components
    chat_engine = container.chatbot().chat_engine()
    job_retriever = container.chatbot().job_retriever()
    course_retriever = container.chatbot().course_retriever()
    
    # 3. Create RAG system wrapper
    rag_system = HybridRAGSystem(
        chat_engine=chat_engine,
        job_retriever=job_retriever,
        course_retriever=course_retriever
    )
    
    # 4. Create a small test dataset
    test_queries = [
        {
            "query_id": "test_1",
            "query": "Find Python developer jobs in San Francisco",
            "query_type": "job_search",
            "ground_truth_answer": "Here are Python developer positions in San Francisco...",
            "context_documents": ["Python Developer at TechCorp..."],
            "metadata": {}
        },
        {
            "query_id": "test_2", 
            "query": "What courses should I take to learn machine learning?",
            "query_type": "course_recommendation",
            "ground_truth_answer": "To learn machine learning, consider these courses...",
            "context_documents": ["Machine Learning Fundamentals..."],
            "metadata": {}
        }
    ]
    
    import pandas as pd
    test_dataset = pd.DataFrame(test_queries)
    
    # 5. Initialize evaluator
    evaluator = HybridRAGEvaluator(output_dir="evaluation_results")
    
    # 6. Run evaluation
    results = await evaluator.evaluate_system(
        rag_system,
        test_dataset,
        configurations=None  # No ablation studies, just baseline
    )
    
    # 7. Print results
    print("\nEvaluation Results:")
    print("-"*40)
    baseline_metrics = results["results"]["baseline"].aggregate_metrics
    for metric, value in baseline_metrics.items():
        if "mean" in metric:
            print(f"{metric}: {value:.3f}")


async def example_dataset_generation():
    """Example of generating evaluation dataset"""
    print("\n" + "="*60)
    print("DATASET GENERATION EXAMPLE")
    print("="*60)
    
    # Initialize generator with your API key
    generator = DatasetGenerator(
        api_key=os.getenv("GEMINI_API_KEY"),  # Set your API key
        output_dir="evaluation_datasets"
    )
    
    # Generate small dataset
    print("Generating evaluation dataset...")
    dataset = await generator.generate_dataset(
        num_samples_per_type=5,  # Small number for demo
        include_hard_negatives=True,
        include_multi_hop=True
    )
    
    print(f"\nGenerated {len(dataset)} samples")
    print("\nSample queries:")
    for i, row in dataset.head(3).iterrows():
        print(f"\n{i+1}. Type: {row['query_type']}")
        print(f"   Query: {row['query']}")
        print(f"   Difficulty: {row['difficulty']}")


async def example_ablation_study():
    """Example of running ablation studies"""
    print("\n" + "="*60)
    print("ABLATION STUDY EXAMPLE")
    print("="*60)
    
    # Get configurations for weight ablation
    config_manager = AblationConfigManager()
    weight_configs = config_manager.get_configs([ComponentType.HYBRID_WEIGHTS])
    
    print("Available weight configurations:")
    for config in weight_configs:
        print(f"- {config.name}: {config.description}")
    
    # You would run evaluation with these configs:
    # results = await evaluator.evaluate_system(
    #     rag_system,
    #     dataset,
    #     configurations=[{"name": c.name, "modifications": c.modifications} 
    #                    for c in weight_configs]
    # )


async def example_custom_metric():
    """Example of adding custom metrics"""
    print("\n" + "="*60)
    print("CUSTOM METRIC EXAMPLE")
    print("="*60)
    
    # Define custom metric
    async def job_location_accuracy(sample, response_data):
        """Check if job location is mentioned correctly"""
        query = sample.get("query", "").lower()
        answer = response_data.get("answer", "").lower()
        
        # Extract location from query
        locations = ["san francisco", "new york", "london", "remote"]
        query_location = None
        for loc in locations:
            if loc in query:
                query_location = loc
                break
        
        # Check if location is in answer
        if query_location and query_location in answer:
            return 1.0
        elif "location" not in query:  # No location specified
            return 1.0
        else:
            return 0.0
    
    # Add to evaluator
    evaluator = HybridRAGEvaluator()
    evaluator.domain_metrics["job_location_accuracy"] = job_location_accuracy
    
    print("Added custom metric: job_location_accuracy")


async def main():
    """Run all examples"""
    try:
        # Run basic evaluation
        await example_basic_evaluation()
        
        # Show dataset generation
        await example_dataset_generation()
        
        # Show ablation study setup
        await example_ablation_study()
        
        # Show custom metric
        await example_custom_metric()
        
        print("\n" + "="*60)
        print("EXAMPLES COMPLETED")
        print("="*60)
        print("\nFor full evaluation, run:")
        print("python -m evaluation.run_evaluation --help")
        
    except Exception as e:
        print(f"\nError in examples: {e}")
        print("\nMake sure you have:")
        print("1. Set up your environment variables")
        print("2. Initialized your databases")
        print("3. Installed all dependencies")


if __name__ == "__main__":
    asyncio.run(main()) 