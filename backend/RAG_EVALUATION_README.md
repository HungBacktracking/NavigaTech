# RAG Evaluation Framework for Academic Research

A comprehensive framework for evaluating different Retrieval-Augmented Generation (RAG) approaches, designed specifically for academic research papers.

## Overview

This framework allows you to systematically evaluate and compare:

1. **Baseline (No RAG)** - Pure LLM without retrieval
2. **Dense Embedding RAG** - Traditional dense vector search
3. **Hybrid Search RAG** - Combined dense + sparse embeddings  
4. **Graph RAG** - Knowledge graph-based retrieval
5. **Hybrid RAG** - Combination of embedding and graph retrieval
6. **Reranked variants** - With neural reranking

## Features

- **Comprehensive Metrics**: RAGAS metrics (answer relevancy, faithfulness, context recall/precision) + custom metrics
- **Statistical Analysis**: Significance testing with Friedman and Wilcoxon tests
- **Visualization**: Publication-ready plots and charts
- **LaTeX Export**: Tables formatted for academic papers
- **Configurable**: Easy to add new approaches or modify existing ones

## Installation

1. Install the required packages:
```bash
pip install -r requirements_evaluation.txt
```

2. Ensure you have the necessary API keys in your `.env` file:
```env
GEMINI_TOKEN=your_gemini_token
COHERE_API_TOKEN=your_cohere_token
OPENAI_API_KEY=your_openai_key  # For RAGAS evaluation
```

## Usage

### Quick Evaluation (5 questions)
```bash
python run_evaluation.py --mode quick
```

### Full Evaluation (all test questions)
```bash
python run_evaluation.py --mode full
```

### Custom Evaluation (specific approaches)
```bash
python run_evaluation.py --mode custom --approaches baseline dense_embedding hybrid_rag --num-questions 10
```

### Available Approaches
- `baseline` - No retrieval
- `dense_embedding` - Dense embeddings only
- `hybrid_search` - Dense + sparse embeddings
- `graph_only` - Graph retrieval only
- `hybrid_rag` - Embedding + graph
- `reranked_dense` - Dense with reranking
- `reranked_hybrid` - Hybrid with reranking
- `graph_heavy_hybrid` - Hybrid with more weight on graph
- `high_recall` - Optimized for high recall

## Output Structure

After running evaluation, you'll get a timestamped results directory containing:

```
evaluation_results_[timestamp]/
├── full_results.csv          # Raw evaluation data
├── summary_statistics.csv    # Aggregated metrics
├── analysis_report.json      # Detailed analysis
├── latex_tables.tex         # Tables for papers
├── overall_performance.png   # Performance comparison plot
├── latency_analysis.png     # Latency breakdown
├── performance_by_type.png   # Results by question type
└── metrics_heatmap.png      # Comprehensive metrics heatmap
```

## Analysis Notebook

Use the `analyze_rag_results.ipynb` notebook for:
- Interactive data exploration
- Custom visualizations
- Statistical significance testing
- Generating additional plots for your paper

## Customization

### Adding New Test Questions

Edit the `create_test_dataset()` method in `rag_evaluation_framework.py`:

```python
def create_test_dataset(self) -> List[Dict[str, str]]:
    test_cases = [
        {
            "question": "Your new question here",
            "type": "job",  # or "course"
            "difficulty": "easy"  # or "medium", "hard"
        },
        # Add more questions...
    ]
```

### Modifying Evaluation Configurations

Edit `evaluation_configs.py` to adjust retriever settings:

```python
"your_custom_config": EvaluationConfig(
    retriever_config=RetrieverConfig(
        dense_top_k=20,
        embedding_weight=0.7,
        graph_weight=0.3,
        use_reranker=True
    ),
    generation_config=GenerationConfig(
        temperature=0.2,
        max_tokens=600
    ),
    experiment_name="Your Custom Config",
    description="Description of your approach"
)
```

### Adding New Metrics

To add custom metrics, modify the `evaluate_single_question()` method:

```python
# Add your custom metric calculation
custom_metric = calculate_your_metric(answer, ground_truth, contexts)

# Include it in the result
return EvaluationResult(
    # ... existing fields ...
    custom_metric=custom_metric
)
```

## Key Components

### 1. `rag_evaluation_framework.py`
Main evaluation framework with:
- `ComprehensiveRAGEvaluator` - Core evaluation class
- `EvaluationResult` - Data structure for results
- Metric calculation and aggregation

### 2. `evaluation_configs.py`
Predefined configurations for each RAG approach with standardized settings.

### 3. `run_evaluation.py`
Simple CLI interface for running evaluations with different modes.

### 4. `analyze_rag_results.ipynb`
Jupyter notebook for interactive analysis and visualization.

## Tips for Paper Writing

1. **Statistical Significance**: Always report p-values and use appropriate corrections (Bonferroni)
2. **Error Bars**: Include standard deviations in your plots
3. **Trade-offs**: Discuss quality vs. latency trade-offs
4. **Reproducibility**: Share your evaluation configurations

## Example Results Interpretation

```
🏆 Best Quality: hybrid_rag (score: 0.892)
⚡ Fastest: baseline (latency: 145.3ms)
⚖️ Best Trade-off: reranked_dense (combined score: 0.754)

📈 Hybrid RAG shows 23.4% improvement over baseline
```

## Troubleshooting

### Common Issues

1. **Neo4j Connection Error**: Ensure Neo4j is running and credentials are correct
2. **RAGAS Evaluation Fails**: Check OpenAI API key and rate limits
3. **Memory Issues**: Reduce batch size or number of questions

### Performance Tips

- Use `--mode quick` for initial testing
- Run full evaluation overnight for comprehensive results
- Consider using GPU for embedding models

## Citation

If you use this framework in your research, please cite:

```bibtex
@software{rag_evaluation_framework,
  title = {Comprehensive RAG Evaluation Framework},
  author = {Your Name},
  year = {2024},
  url = {https://github.com/yourusername/rag-evaluation}
}
```

## Contributing

Feel free to submit issues or pull requests for improvements! 