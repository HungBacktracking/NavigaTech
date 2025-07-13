# Hybrid RAG Evaluation Framework

A comprehensive evaluation framework for Hybrid RAG systems that combines embedding-based and knowledge graph retrieval. This framework implements industry best practices for evaluating RAG systems in the IT domain (job search and course recommendations).

## Features

### 1. **Comprehensive Metrics**
- **RAGAS Metrics**: Answer correctness, faithfulness, context precision/recall, answer relevancy
- **Domain-Specific Metrics**: Skill coverage, entity precision, requirement matching, career path coherence
- **Performance Metrics**: Latency (mean, p95, p99), throughput

### 2. **Ablation Studies**
- Test individual components (embedding vs graph retrieval)
- Evaluate different weight combinations
- Assess impact of reranker
- Compare different top-k values

### 3. **Statistical Analysis**
- Paired t-tests for configuration comparisons
- ANOVA across query types
- Normality tests
- Confidence intervals

### 4. **Advanced Dataset Generation**
- Multiple query types (job search, course recommendation, skill matching, career paths)
- Difficulty levels (easy, medium, hard)
- Hard negative generation
- Multi-hop queries

## Installation

```bash
# Install evaluation dependencies
pip install -r evaluation/requirements.txt

# For RAGAS metrics
pip install ragas

# Optional: for experiment tracking
pip install wandb
```

## Quick Start

### 1. Basic Evaluation

```bash
# Run evaluation with default settings
python -m evaluation.run_evaluation --quick-test

# Generate larger dataset and run full evaluation
python -m evaluation.run_evaluation --num-samples 50
```

### 2. Using Existing Dataset

```bash
# Use a pre-generated dataset
python -m evaluation.run_evaluation --dataset evaluation_datasets/eval_dataset_20240101_120000.csv
```

### 3. Specific Ablation Studies

```bash
# Test only retriever components
python -m evaluation.run_evaluation --ablation-study retriever

# Test weight combinations
python -m evaluation.run_evaluation --ablation-study weights

# Test top-k values
python -m evaluation.run_evaluation --ablation-study topk
```

## Detailed Usage

### Dataset Generation

```python
from evaluation.dataset_generator import DatasetGenerator

# Initialize generator
generator = DatasetGenerator(api_key="your-gemini-api-key")

# Generate comprehensive dataset
dataset = await generator.generate_dataset(
    num_samples_per_type=50,  # 50 samples per query type
    include_hard_negatives=True,
    include_multi_hop=True
)

# Augment with your real data
augmented_dataset = await generator.augment_with_your_data(
    job_data_path="path/to/jobs.json",
    course_data_path="path/to/courses.json"
)
```

### Running Evaluation

```python
from evaluation.evaluator import HybridRAGEvaluator
from evaluation.rag_adapter import HybridRAGSystem

# Initialize evaluator
evaluator = HybridRAGEvaluator(
    output_dir="evaluation_results",
    enable_wandb=True  # Enable Weights & Biases tracking
)

# Create RAG system wrapper
rag_system = HybridRAGSystem(
    chat_engine=your_chat_engine,
    job_retriever=your_job_retriever,
    course_retriever=your_course_retriever
)

# Run evaluation
results = await evaluator.evaluate_system(
    rag_system,
    eval_dataset,
    configurations=[...]  # Optional: specific configurations
)
```

### Custom Ablation Configurations

```python
from evaluation.ablation_configs import AblationConfig, ComponentType

# Create custom configuration
custom_config = AblationConfig(
    name="ultra_light",
    description="Minimal retrieval with top-3 only",
    modifications={
        "top_k": 3,
        "disable_reranker": True,
        "embedding_weight": 0.9,
        "graph_weight": 0.1
    },
    component_type=ComponentType.TOP_K
)

# Add to evaluation
config_manager.add_custom_config(custom_config)
```

## Output Structure

```
evaluation_results/
├── results_baseline_20240101_120000.csv      # Detailed results per sample
├── results_embedding_only_20240101_120000.csv
├── results_graph_only_20240101_120000.csv
├── analysis_20240101_120000.json             # Statistical analysis
├── report_20240101_120000.json               # Summary report
├── metric_comparison_20240101_120000.png     # Visualization
└── latency_distribution_20240101_120000.png
```

## Metrics Explained

### RAGAS Metrics
- **Answer Correctness**: How accurate is the generated answer compared to ground truth
- **Faithfulness**: Whether the answer is grounded in the retrieved context
- **Context Precision**: Relevance of retrieved documents
- **Context Recall**: Coverage of required information in retrieved documents
- **Answer Relevancy**: How relevant the answer is to the question

### Domain-Specific Metrics
- **Skill Coverage**: Percentage of mentioned skills correctly identified
- **Entity Precision**: Accuracy of entity extraction (jobs, companies, skills)
- **Requirement Matching**: How well job requirements are captured
- **Career Path Coherence**: Logical progression in career recommendations

## Best Practices

1. **Dataset Quality**
   - Generate diverse queries covering all use cases
   - Include edge cases and difficult queries
   - Balance query types in your dataset

2. **Statistical Significance**
   - Run evaluation on at least 100 samples per configuration
   - Use statistical tests to validate improvements
   - Report confidence intervals

3. **Ablation Studies**
   - Test one component at a time
   - Keep other variables constant
   - Document all configuration changes

4. **Performance Considerations**
   - Monitor both quality metrics and latency
   - Consider trade-offs between accuracy and speed
   - Test under realistic load conditions

## Interpreting Results

### Example Output
```
Configuration: baseline
----------------------------------------
Answer Correctness: 0.842 (±0.123)
Context Precision: 0.756
Faithfulness: 0.891
Answer Relevancy: 0.923
Latency: 245.3ms (p95: 412.1ms)

Configuration: embedding_only
----------------------------------------
Answer Correctness: 0.798 (±0.145)
Context Precision: 0.812
Faithfulness: 0.867
Answer Relevancy: 0.901
Latency: 189.2ms (p95: 298.5ms)
```

### Making Decisions
- **Baseline > 0.8**: Good performance
- **Significant p-value < 0.05**: Real difference between configurations
- **Latency p95 < 500ms**: Acceptable for real-time applications

## Troubleshooting

### Common Issues

1. **Import Errors**
   ```bash
   # Ensure you're in the project root
   cd /path/to/backend
   python -m evaluation.run_evaluation
   ```

2. **Memory Issues**
   ```bash
   # Reduce batch size
   python -m app.evaluation.run_evaluation --num-samples 10
   ```

3. **API Rate Limits**
   - Add delays in dataset generation
   - Use cached datasets when possible

## Advanced Features

### Custom Metrics

```python
async def custom_metric(sample, response_data):
    """Implement your custom metric"""
    # Your logic here
    return score

# Add to evaluator
evaluator.domain_metrics["custom_metric"] = custom_metric
```

### Integration with MLflow/Weights & Biases

```python
# Enable W&B tracking
evaluator = HybridRAGEvaluator(
    enable_wandb=True,
    wandb_project="hybrid-rag-evaluation"
)
```

## Contributing

When adding new features:
1. Add corresponding metrics
2. Update ablation configurations
3. Document changes in this README
4. Add unit tests

## Citation

If you use this evaluation framework in your research, please cite:
```
@software{hybrid_rag_eval,
  title = {Hybrid RAG Evaluation Framework},
  year = {2024},
  author = {Your Organization}
}
``` 