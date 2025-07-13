# Research Guide: Hybrid RAG Evaluation for Academic Papers

This guide explains how to use the evaluation framework for your research paper on Hybrid RAG systems in the IT domain.

## Framework Architecture

The evaluation framework consists of several key components designed specifically for academic research:

### 1. Dataset Generation (`dataset_generator.py`)
- **Purpose**: Creates diverse, challenging evaluation datasets
- **Research Value**: 
  - Generates 6 query types relevant to IT domain
  - Includes difficulty levels for stratified analysis
  - Creates hard negatives for robustness testing
  - Supports multi-hop queries for complex reasoning evaluation

### 2. Comprehensive Evaluator (`evaluator.py`)
- **Purpose**: Implements state-of-the-art metrics and statistical analysis
- **Research Value**:
  - RAGAS metrics for standardized comparison
  - Domain-specific metrics for IT QA evaluation
  - Statistical significance testing (t-tests, ANOVA)
  - Confidence intervals for all metrics

### 3. Ablation Study Framework (`ablation_configs.py`)
- **Purpose**: Systematic component analysis
- **Research Value**:
  - Isolates contribution of each component
  - Tests hybrid weight combinations
  - Evaluates reranker impact
  - Provides empirical evidence for design choices

### 4. Adapter Pattern (`rag_adapter.py`)
- **Purpose**: Clean interface between evaluation and system
- **Research Value**:
  - Ensures reproducibility
  - Enables fair comparison
  - Facilitates system modifications for ablations

## For Your Research Paper

### 1. Experimental Setup Section

```markdown
## Experimental Setup

### Dataset
We generated a comprehensive evaluation dataset consisting of:
- 300 queries across 6 categories (50 per category)
- Query types: job search, course recommendation, skill matching, 
  career path, comparative analysis, and multi-hop reasoning
- Difficulty levels: easy (40%), medium (40%), hard (20%)
- Ground truth generated using Gemini-Pro with human validation

### Metrics
We employ both standard and domain-specific metrics:

**Standard Metrics (RAGAS)**:
- Answer Correctness (AC)
- Faithfulness (F)
- Context Precision (CP)
- Context Recall (CR)
- Answer Relevancy (AR)

**Domain-Specific Metrics**:
- Skill Coverage (SC): Percentage of required skills mentioned
- Entity Precision (EP): Accuracy of job/course entity extraction
- Requirement Matching (RM): Completeness of job requirements
- Career Path Coherence (CPC): Logical progression in recommendations

### Statistical Analysis
- Paired t-tests for configuration comparisons (α = 0.05)
- ANOVA for query type performance analysis
- Bonferroni correction for multiple comparisons
```

### 2. Results Section

```python
# Generate publication-ready results
results = await evaluator.evaluate_system(
    rag_system,
    eval_dataset,
    configurations=ablation_configs
)

# Extract key metrics for paper
baseline = results["results"]["baseline"]
print(f"Baseline Performance:")
print(f"AC: {baseline.aggregate_metrics['answer_correctness_mean']:.3f} "
      f"(±{baseline.aggregate_metrics['answer_correctness_std']:.3f})")
```

### 3. Ablation Study Results

The framework provides structured ablation results perfect for research papers:

```markdown
## Ablation Study Results

| Configuration | AC ↑ | F ↑ | CP ↑ | Latency (ms) ↓ |
|--------------|------|-----|------|----------------|
| Baseline     | 0.842| 0.891| 0.756| 245.3         |
| Embed Only   | 0.798| 0.867| 0.812| 189.2         |
| Graph Only   | 0.723| 0.834| 0.698| 312.4         |
| No Reranker  | 0.801| 0.878| 0.723| 198.7         |

Statistical significance: * p < 0.05, ** p < 0.01, *** p < 0.001
```

### 4. Visualization for Papers

The framework generates publication-quality figures:

```python
# The evaluator automatically creates:
# 1. Metric comparison bar charts
# 2. Latency distribution histograms
# 3. Performance vs query type heatmaps
```

## Best Practices for Research

### 1. Reproducibility
- Set random seeds in dataset generation
- Document all hyperparameters
- Save generated datasets with papers
- Use version control for configurations

### 2. Statistical Rigor
- Run at least 3 seeds for each configuration
- Report confidence intervals, not just means
- Use appropriate statistical tests
- Correct for multiple comparisons

### 3. Comprehensive Analysis
```python
# Analyze by query type
by_type_analysis = analyze_by_query_type(results)

# Analyze by difficulty
by_difficulty = analyze_by_difficulty(results)

# Error analysis
error_cases = identify_failure_patterns(results)
```

### 4. Reporting Guidelines

Include in your paper:
1. **Dataset Statistics**: Size, distribution, generation method
2. **Implementation Details**: Model versions, hardware specs
3. **Hyperparameters**: All configuration values
4. **Statistical Tests**: Test types, significance levels
5. **Error Analysis**: Common failure patterns

## Example Paper Sections

### Abstract Results
"Our Hybrid RAG system achieves 84.2% answer correctness, outperforming embedding-only (79.8%) and graph-only (72.3%) baselines (p < 0.001). The hybrid approach shows particular strength in multi-hop queries (87.1% vs 71.2% baseline)."

### Methodology
"We evaluate using the RAGAS framework augmented with domain-specific metrics. Our ablation study systematically removes components to quantify their contribution..."

### Discussion
"The 5.9% improvement from graph integration validates our hypothesis that structural knowledge enhances retrieval quality. However, the 23% latency increase requires optimization..."

## Citation

When using this framework, cite:

```bibtex
@inproceedings{your-paper-2024,
  title={Hybrid RAG: Combining Embedding and Knowledge Graph Retrieval for IT Domain QA},
  author={Your Name et al.},
  booktitle={Conference Name},
  year={2024}
}
```

## Checklist for Paper Submission

- [ ] Generated dataset with at least 300 samples
- [ ] Ran evaluation with 3+ random seeds
- [ ] Completed full ablation study
- [ ] Performed statistical significance tests
- [ ] Generated all visualization figures
- [ ] Documented failure cases
- [ ] Compared against baselines
- [ ] Reported confidence intervals
- [ ] Saved all results and datasets
- [ ] Made code available for reproduction 