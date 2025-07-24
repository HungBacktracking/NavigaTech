"""
Run RAG Evaluation for Research Paper
=====================================
Simple script to execute the comprehensive evaluation
"""

import asyncio
import argparse
from datetime import datetime
import os
import sys

# Add the app directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rag_evaluation_framework import ComprehensiveRAGEvaluator, RAGApproach
from evaluation_configs import EVALUATION_PRESETS


async def run_quick_evaluation():
    """Run a quick evaluation with fewer questions for testing"""
    print("🚀 Running Quick Evaluation (5 questions)")
    
    evaluator = ComprehensiveRAGEvaluator()
    
    # Use only 5 test questions
    quick_test_cases = [
        {
            "question": "What skills are required for a Data Engineer?",
            "type": "job",
            "difficulty": "easy"
        },
        {
            "question": "What Python courses are best for beginners?",
            "type": "course", 
            "difficulty": "easy"
        },
        {
            "question": "What does a Machine Learning Engineer do?",
            "type": "job",
            "difficulty": "medium"
        },
        {
            "question": "How can I learn cloud computing?",
            "type": "course",
            "difficulty": "medium"
        },
        {
            "question": "What is the career path for a Software Engineer?",
            "type": "job",
            "difficulty": "hard"
        }
    ]
    
    # Generate ground truth
    print("\n📝 Generating ground truth...")
    test_cases_with_truth = await evaluator.generate_ground_truth(quick_test_cases)
    
    # Run evaluation
    print("\n🔬 Running evaluation...")
    results_df = await evaluator.run_comprehensive_evaluation(test_cases_with_truth)
    results_df = await evaluator.add_ragas_metrics(results_df)
    
    # Generate report
    print("\n📊 Generating analysis...")
    analysis_report = evaluator.generate_analysis_report(results_df)
    
    # Create output directory with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = f"evaluation_results_quick_{timestamp}"
    
    # Save results
    evaluator.create_visualizations(results_df, output_dir)
    evaluator.export_for_paper(results_df, analysis_report, output_dir)
    
    print(f"\n✅ Quick evaluation complete! Results saved to {output_dir}/")
    
    return results_df, analysis_report


async def run_full_evaluation():
    """Run full evaluation with all test cases"""
    print("🚀 Running Full Evaluation")
    
    evaluator = ComprehensiveRAGEvaluator()
    
    # Create full test dataset
    test_cases = evaluator.create_test_dataset()
    print(f"\n📋 Created {len(test_cases)} test cases")
    
    # Generate ground truth
    print("\n📝 Generating ground truth...")
    test_cases_with_truth = await evaluator.generate_ground_truth(test_cases)
    
    # Run evaluation
    print("\n🔬 Running comprehensive evaluation...")
    results_df = await evaluator.run_comprehensive_evaluation(test_cases_with_truth)
    
    # Generate report
    print("\n📊 Generating analysis report...")
    analysis_report = evaluator.generate_analysis_report(results_df)
    
    # Create output directory with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = f"evaluation_results_full_{timestamp}"
    
    # Create visualizations and export
    evaluator.create_visualizations(results_df, output_dir)
    evaluator.export_for_paper(results_df, analysis_report, output_dir)
    
    print(f"\n✅ Full evaluation complete! Results saved to {output_dir}/")
    
    return results_df, analysis_report


async def run_custom_evaluation(approaches: list, num_questions: int = 10):
    """Run evaluation with custom selection of approaches"""
    print(f"🚀 Running Custom Evaluation with {len(approaches)} approaches")
    
    evaluator = ComprehensiveRAGEvaluator()
    
    # Create test dataset
    all_test_cases = evaluator.create_test_dataset()
    test_cases = all_test_cases[:num_questions]
    
    print(f"\n📋 Using {len(test_cases)} test cases")
    
    # Generate ground truth
    print("\n📝 Generating ground truth...")
    test_cases_with_truth = await evaluator.generate_ground_truth(test_cases)
    
    # Filter experiments to only requested approaches
    from rag_evaluation_framework import ExperimentConfig
    
    experiments = []
    for approach_name in approaches:
        try:
            approach = RAGApproach(approach_name)
            config = EVALUATION_PRESETS.get(approach_name)
            if config:
                experiments.append(ExperimentConfig(
                    approach=approach,
                    top_k=config.retriever_config.dense_top_k or config.retriever_config.graph_top_k,
                    rerank=config.retriever_config.use_reranker,
                    embedding_weight=config.retriever_config.embedding_weight,
                    graph_weight=config.retriever_config.graph_weight,
                    temperature=config.generation_config.temperature,
                    max_tokens=config.generation_config.max_tokens
                ))
        except ValueError:
            print(f"⚠️  Unknown approach: {approach_name}")
    
    # Run evaluation with custom experiments
    print(f"\n🔬 Running evaluation with {len(experiments)} approaches...")
    
    all_results = []
    for config in experiments:
        print(f"\n📊 Evaluating {config.approach.value}...")
        
        for test_case in test_cases_with_truth:
            result = await evaluator.evaluate_single_question(
                question=test_case['question'],
                ground_truth=test_case['ground_truth'],
                approach=config.approach,
                config=config
            )
            
            # Add metadata
            result_dict = result.__dict__.copy()
            result_dict.update({
                'question_type': test_case['type'],
                'difficulty': test_case['difficulty']
            })
            all_results.append(result_dict)
    
    # Convert to DataFrame and add RAGAS metrics
    import pandas as pd
    results_df = pd.DataFrame(all_results)
    results_df['approach'] = results_df['approach'].map(lambda a: a.value if isinstance(a, RAGApproach) else a)
    results_df = await evaluator.add_ragas_metrics(results_df)
    
    # Generate report
    print("\n📊 Generating analysis report...")
    analysis_report = evaluator.generate_analysis_report(results_df)
    
    # Create output directory
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    approaches_str = "_".join(approaches[:3])  # First 3 approaches in filename
    output_dir = f"evaluation_results_custom_{approaches_str}_{timestamp}"
    
    # Save results
    evaluator.create_visualizations(results_df, output_dir)
    evaluator.export_for_paper(results_df, analysis_report, output_dir)
    
    print(f"\n✅ Custom evaluation complete! Results saved to {output_dir}/")
    
    return results_df, analysis_report


def main():
    parser = argparse.ArgumentParser(description="Run RAG evaluation for research")
    parser.add_argument(
        "--mode", 
        choices=["quick", "full", "custom"],
        default="quick",
        help="Evaluation mode: quick (5 questions), full (all questions), or custom"
    )
    parser.add_argument(
        "--approaches",
        nargs="+",
        choices=list(EVALUATION_PRESETS.keys()),
        help="For custom mode: which approaches to evaluate"
    )
    parser.add_argument(
        "--num-questions",
        type=int,
        default=10,
        help="For custom mode: number of questions to use"
    )
    
    args = parser.parse_args()
    
    # Print header
    print("=" * 60)
    print("RAG EVALUATION FOR ACADEMIC RESEARCH")
    print("=" * 60)
    print(f"Mode: {args.mode}")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # Run appropriate evaluation
    if args.mode == "quick":
        asyncio.run(run_quick_evaluation())
    elif args.mode == "full":
        asyncio.run(run_full_evaluation())
    elif args.mode == "custom":
        if not args.approaches:
            print("❌ Error: --approaches required for custom mode")
            print("Available approaches:", list(EVALUATION_PRESETS.keys()))
            sys.exit(1)
        asyncio.run(run_custom_evaluation(args.approaches, args.num_questions))


if __name__ == "__main__":
    main() 