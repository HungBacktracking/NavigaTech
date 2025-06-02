import asyncio
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.core.containers.ai_container import AIContainer
from app.core.containers.database_container import DatabaseContainer
from app.core.containers.chatbot_container import ChatbotContainer
from app.evaluation.evaluator import HybridRAGEvaluator
from app.evaluation.dataset import EvaluationDataset
from app.evaluation.visualizer import EvaluationVisualizer

# Load environment variables
load_dotenv()


async def main():
    # Initialize containers
    database_container = DatabaseContainer()
    database_container.config.from_env('POSTGRES_URL', 'QDRANT_URL', 'QDRANT_API_KEY', 
                                       'QDRANT_COLLECTION_NAME', 'NEO4J_URI', 
                                       'NEO4J_USERNAME', 'NEO4J_PASSWORD')
    
    ai_container = AIContainer()
    ai_container.config.from_env('GEMINI_TOKEN', 'GEMINI_MODEL_NAME', 'EMBEDDING_MODEL_NAME',
                                'SCORING_MODEL_NAME', 'MAX_TOKENS', 'TEMPERATURE', 
                                'COHERE_API_TOKEN')
    
    chatbot_container = ChatbotContainer()
    chatbot_container.config.from_env('COURSE_DB', 'QDRANT_COLLECTION_NAME', 'COHERE_API_TOKEN')
    chatbot_container.database.override(database_container)
    chatbot_container.AI.override(ai_container)
    
    # Create evaluation dataset
    print("Creating evaluation dataset...")
    dataset = EvaluationDataset()
    dataset.create_it_domain_dataset()
    
    # Save dataset for reproducibility
    dataset.save_dataset("evaluation_results/it_domain_dataset.json")
    
    # Get components
    job_retriever = chatbot_container.job_retriever()
    course_retriever = chatbot_container.course_retriever()
    chat_engine = chatbot_container.chat_engine()
    
    # Initialize evaluator
    evaluator = HybridRAGEvaluator(
        job_retriever=job_retriever,
        course_retriever=course_retriever,
        chat_engine=chat_engine,
        output_dir="evaluation_results"
    )
    
    # Run main evaluation
    print("\n=== Running Main Evaluation ===")
    results = await evaluator.evaluate_dataset(
        dataset,
        resume_text="Senior software engineer with 10 years of experience in Python, Java, and cloud technologies",
        experiment_name="main_evaluation"
    )
    
    # Run ablation study
    print("\n=== Running Ablation Study ===")
    ablation_results = await evaluator.ablation_study(
        dataset,
        resume_text="Senior software engineer with 10 years of experience in Python, Java, and cloud technologies"
    )
    
    # Generate visualizations
    print("\n=== Generating Visualizations ===")
    visualizer = EvaluationVisualizer()
    
    # Find the latest result files
    results_dir = Path("evaluation_results")
    main_results_file = max(results_dir.glob("main_evaluation_detailed_*.json"))
    ablation_results_file = max(results_dir.glob("ablation_study_detailed_*.json"))
    
    # Generate plots
    visualizer.plot_retrieval_metrics_by_k(str(main_results_file), "main_evaluation")
    visualizer.plot_generation_metrics(str(main_results_file), "main_evaluation")
    visualizer.plot_metric_distributions(str(main_results_file), "main_evaluation")
    visualizer.plot_ablation_comparison(str(ablation_results_file))
    
    # Generate markdown report
    report_path = visualizer.generate_markdown_report(str(main_results_file), "main_evaluation")
    
    print(f"\n=== Evaluation Complete ===")
    print(f"Results saved to: evaluation_results/")
    print(f"Visualizations saved to: evaluation_results/visualizations/")
    print(f"Report saved to: {report_path}")
    
    # Print summary
    print("\n=== Summary of Main Evaluation ===")
    print(f"Number of queries: {results['num_queries']}")
    
    if 'retrieval_metrics' in results:
        print("\nRetrieval Metrics (mean):")
        for metric, stats in results['retrieval_metrics'].items():
            if 'mean' in stats:
                print(f"  {metric}: {stats['mean']:.4f}")
    
    if 'generation_metrics' in results:
        print("\nGeneration Metrics (mean):")
        for metric, stats in results['generation_metrics'].items():
            if 'mean' in stats:
                print(f"  {metric}: {stats['mean']:.4f}")
    
    if 'timing_metrics' in results:
        print("\nTiming Metrics (mean):")
        for metric, stats in results['timing_metrics'].items():
            if 'mean' in stats:
                print(f"  {metric}: {stats['mean']:.3f} seconds")


if __name__ == "__main__":
    # Create output directories
    Path("evaluation_results").mkdir(exist_ok=True)
    Path("evaluation_results/visualizations").mkdir(exist_ok=True)
    
    # Run async main
    asyncio.run(main()) 