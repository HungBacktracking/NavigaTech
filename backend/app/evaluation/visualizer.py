import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Any
import json


class EvaluationVisualizer:
    """Generate visualizations and reports for evaluation results"""
    
    def __init__(self, output_dir: str = "evaluation_results/visualizations"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Set style
        plt.style.use('seaborn-v0_8-darkgrid')
        sns.set_palette("husl")
    
    def plot_retrieval_metrics_by_k(self, results_path: str, experiment_name: str = "default"):
        """Plot precision, recall, F1 at different k values"""
        # Load results
        with open(results_path, 'r') as f:
            data = json.load(f)
        
        # Extract retrieval metrics
        retrieval_metrics = data['aggregated_results']['retrieval_metrics']
        
        # Prepare data for plotting
        k_values = []
        precision_values = []
        recall_values = []
        f1_values = []
        
        for metric, stats in retrieval_metrics.items():
            if '@' in metric:
                metric_type, k = metric.split('@')
                k = int(k)
                
                if metric_type == 'precision':
                    k_values.append(k)
                    precision_values.append(stats['mean'])
                elif metric_type == 'recall':
                    k_values.append(k)
                    recall_values.append(stats['mean'])
                elif metric_type == 'f1':
                    k_values.append(k)
                    f1_values.append(stats['mean'])
        
        # Sort by k values
        k_values = sorted(list(set(k_values)))
        
        # Create plot
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # Plot lines
        ax.plot(k_values, [precision_values[i] for i in range(len(k_values))], 
                marker='o', label='Precision@K', linewidth=2)
        ax.plot(k_values, [recall_values[i] for i in range(len(k_values))], 
                marker='s', label='Recall@K', linewidth=2)
        ax.plot(k_values, [f1_values[i] for i in range(len(k_values))], 
                marker='^', label='F1@K', linewidth=2)
        
        ax.set_xlabel('K', fontsize=12)
        ax.set_ylabel('Score', fontsize=12)
        ax.set_title(f'Retrieval Metrics by K - {experiment_name}', fontsize=14)
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        # Save plot
        plot_path = self.output_dir / f'retrieval_metrics_by_k_{experiment_name}.png'
        plt.tight_layout()
        plt.savefig(plot_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        return plot_path
    
    def plot_generation_metrics(self, results_path: str, experiment_name: str = "default"):
        """Plot generation quality metrics"""
        # Load results
        with open(results_path, 'r') as f:
            data = json.load(f)
        
        generation_metrics = data['aggregated_results']['generation_metrics']
        
        # Prepare data
        metrics_data = []
        for metric, stats in generation_metrics.items():
            if 'mean' in stats:
                metrics_data.append({
                    'metric': metric,
                    'mean': stats['mean'],
                    'std': stats.get('std', 0)
                })
        
        df = pd.DataFrame(metrics_data)
        
        # Create plot
        fig, ax = plt.subplots(figsize=(12, 6))
        
        x = np.arange(len(df))
        bars = ax.bar(x, df['mean'], yerr=df['std'], capsize=5, alpha=0.8)
        
        # Color bars by metric type
        colors = []
        for metric in df['metric']:
            if 'bleu' in metric:
                colors.append('skyblue')
            elif 'rouge' in metric:
                colors.append('lightcoral')
            elif 'similarity' in metric:
                colors.append('lightgreen')
            else:
                colors.append('plum')
        
        for bar, color in zip(bars, colors):
            bar.set_color(color)
        
        ax.set_xticks(x)
        ax.set_xticklabels(df['metric'], rotation=45, ha='right')
        ax.set_ylabel('Score', fontsize=12)
        ax.set_title(f'Generation Quality Metrics - {experiment_name}', fontsize=14)
        ax.set_ylim(0, 1.1)
        
        # Add value labels on bars
        for i, (bar, mean) in enumerate(zip(bars, df['mean'])):
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01,
                   f'{mean:.3f}', ha='center', va='bottom', fontsize=9)
        
        plt.tight_layout()
        plot_path = self.output_dir / f'generation_metrics_{experiment_name}.png'
        plt.savefig(plot_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        return plot_path
    
    def plot_ablation_comparison(self, ablation_results_path: str):
        """Create comparison plots for ablation study"""
        # Load ablation results
        with open(ablation_results_path, 'r') as f:
            ablation_data = json.load(f)
        
        # Prepare data for comparison
        configs = []
        retrieval_f1_5 = []
        generation_similarity = []
        total_time = []
        
        for config, results in ablation_data.items():
            configs.append(config)
            
            # Get F1@5
            f1_5 = results.get('retrieval_metrics', {}).get('f1@5', {}).get('mean', 0)
            retrieval_f1_5.append(f1_5)
            
            # Get semantic similarity
            sem_sim = results.get('generation_metrics', {}).get('semantic_similarity', {}).get('mean', 0)
            generation_similarity.append(sem_sim)
            
            # Get total time
            time = results.get('timing_metrics', {}).get('total_time', {}).get('mean', 0)
            total_time.append(time)
        
        # Create subplots
        fig, axes = plt.subplots(1, 3, figsize=(15, 5))
        
        # Plot 1: Retrieval F1@5
        axes[0].bar(configs, retrieval_f1_5, color='steelblue', alpha=0.8)
        axes[0].set_title('Retrieval Performance (F1@5)', fontsize=12)
        axes[0].set_ylabel('F1 Score', fontsize=10)
        axes[0].set_xticklabels(configs, rotation=45, ha='right')
        
        # Plot 2: Generation Semantic Similarity
        axes[1].bar(configs, generation_similarity, color='seagreen', alpha=0.8)
        axes[1].set_title('Generation Quality (Semantic Similarity)', fontsize=12)
        axes[1].set_ylabel('Similarity Score', fontsize=10)
        axes[1].set_xticklabels(configs, rotation=45, ha='right')
        
        # Plot 3: Total Time
        axes[2].bar(configs, total_time, color='coral', alpha=0.8)
        axes[2].set_title('Average Total Time', fontsize=12)
        axes[2].set_ylabel('Time (seconds)', fontsize=10)
        axes[2].set_xticklabels(configs, rotation=45, ha='right')
        
        plt.suptitle('Ablation Study Comparison', fontsize=14)
        plt.tight_layout()
        
        plot_path = self.output_dir / 'ablation_comparison.png'
        plt.savefig(plot_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        return plot_path
    
    def plot_metric_distributions(self, results_path: str, experiment_name: str = "default"):
        """Plot distribution of metrics across queries"""
        # Load detailed results
        with open(results_path, 'r') as f:
            data = json.load(f)
        
        detailed_results = data['detailed_results']
        
        # Extract metrics for each query
        precision_5_values = []
        recall_5_values = []
        semantic_sim_values = []
        faithfulness_values = []
        
        for result in detailed_results:
            eval_data = result['results'].get('evaluation', {})
            
            # Retrieval metrics
            prec_5 = eval_data.get('retrieval_metrics', {}).get('precision@5', 0)
            recall_5 = eval_data.get('retrieval_metrics', {}).get('recall@5', 0)
            precision_5_values.append(prec_5)
            recall_5_values.append(recall_5)
            
            # Generation metrics
            sem_sim = eval_data.get('generation_metrics', {}).get('semantic_similarity', 0)
            faith = eval_data.get('generation_metrics', {}).get('faithfulness', 0)
            semantic_sim_values.append(sem_sim)
            faithfulness_values.append(faith)
        
        # Create figure with subplots
        fig, axes = plt.subplots(2, 2, figsize=(12, 10))
        
        # Precision@5 distribution
        axes[0, 0].hist(precision_5_values, bins=20, edgecolor='black', alpha=0.7, color='skyblue')
        axes[0, 0].set_title('Distribution of Precision@5', fontsize=12)
        axes[0, 0].set_xlabel('Precision@5')
        axes[0, 0].set_ylabel('Frequency')
        axes[0, 0].axvline(np.mean(precision_5_values), color='red', linestyle='--', 
                          label=f'Mean: {np.mean(precision_5_values):.3f}')
        axes[0, 0].legend()
        
        # Recall@5 distribution
        axes[0, 1].hist(recall_5_values, bins=20, edgecolor='black', alpha=0.7, color='lightgreen')
        axes[0, 1].set_title('Distribution of Recall@5', fontsize=12)
        axes[0, 1].set_xlabel('Recall@5')
        axes[0, 1].set_ylabel('Frequency')
        axes[0, 1].axvline(np.mean(recall_5_values), color='red', linestyle='--',
                          label=f'Mean: {np.mean(recall_5_values):.3f}')
        axes[0, 1].legend()
        
        # Semantic similarity distribution
        axes[1, 0].hist(semantic_sim_values, bins=20, edgecolor='black', alpha=0.7, color='lightcoral')
        axes[1, 0].set_title('Distribution of Semantic Similarity', fontsize=12)
        axes[1, 0].set_xlabel('Semantic Similarity')
        axes[1, 0].set_ylabel('Frequency')
        axes[1, 0].axvline(np.mean(semantic_sim_values), color='red', linestyle='--',
                          label=f'Mean: {np.mean(semantic_sim_values):.3f}')
        axes[1, 0].legend()
        
        # Faithfulness distribution
        axes[1, 1].hist(faithfulness_values, bins=20, edgecolor='black', alpha=0.7, color='plum')
        axes[1, 1].set_title('Distribution of Faithfulness', fontsize=12)
        axes[1, 1].set_xlabel('Faithfulness Score')
        axes[1, 1].set_ylabel('Frequency')
        axes[1, 1].axvline(np.mean(faithfulness_values), color='red', linestyle='--',
                          label=f'Mean: {np.mean(faithfulness_values):.3f}')
        axes[1, 1].legend()
        
        plt.suptitle(f'Metric Distributions - {experiment_name}', fontsize=14)
        plt.tight_layout()
        
        plot_path = self.output_dir / f'metric_distributions_{experiment_name}.png'
        plt.savefig(plot_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        return plot_path
    
    def generate_markdown_report(self, results_path: str, experiment_name: str = "default") -> str:
        """Generate a comprehensive markdown report"""
        # Load results
        with open(results_path, 'r') as f:
            data = json.load(f)
        
        aggregated = data['aggregated_results']
        
        # Start building report
        report = f"# Evaluation Report: {experiment_name}\n\n"
        report += f"**Generated at:** {data['timestamp']}\n\n"
        report += f"**Number of queries evaluated:** {aggregated['num_queries']}\n\n"
        
        # Retrieval metrics section
        report += "## Retrieval Metrics\n\n"
        report += "| Metric | Mean | Std | Min | Max | Median |\n"
        report += "|--------|------|-----|-----|-----|--------|\n"
        
        for metric, stats in aggregated['retrieval_metrics'].items():
            report += f"| {metric} | {stats['mean']:.4f} | {stats['std']:.4f} | "
            report += f"{stats['min']:.4f} | {stats['max']:.4f} | {stats['median']:.4f} |\n"
        
        # Generation metrics section
        report += "\n## Generation Metrics\n\n"
        report += "| Metric | Mean | Std | Min | Max | Median |\n"
        report += "|--------|------|-----|-----|-----|--------|\n"
        
        for metric, stats in aggregated['generation_metrics'].items():
            report += f"| {metric} | {stats['mean']:.4f} | {stats['std']:.4f} | "
            report += f"{stats['min']:.4f} | {stats['max']:.4f} | {stats['median']:.4f} |\n"
        
        # Timing metrics section
        report += "\n## Performance Metrics\n\n"
        report += "| Metric | Mean (s) | Std | Min | Max | Median |\n"
        report += "|--------|----------|-----|-----|-----|--------|\n"
        
        for metric, stats in aggregated['timing_metrics'].items():
            report += f"| {metric} | {stats['mean']:.3f} | {stats['std']:.3f} | "
            report += f"{stats['min']:.3f} | {stats['max']:.3f} | {stats['median']:.3f} |\n"
        
        # Key findings
        report += "\n## Key Findings\n\n"
        
        # Find best performing metrics
        best_retrieval = max(aggregated['retrieval_metrics'].items(), 
                           key=lambda x: x[1]['mean'] if 'precision' in x[0] else 0)
        report += f"- **Best retrieval metric:** {best_retrieval[0]} with mean {best_retrieval[1]['mean']:.4f}\n"
        
        best_generation = max(aggregated['generation_metrics'].items(),
                            key=lambda x: x[1]['mean'])
        report += f"- **Best generation metric:** {best_generation[0]} with mean {best_generation[1]['mean']:.4f}\n"
        
        avg_total_time = aggregated['timing_metrics'].get('total_time', {}).get('mean', 0)
        report += f"- **Average total response time:** {avg_total_time:.3f} seconds\n"
        
        # Save report
        report_path = self.output_dir / f'evaluation_report_{experiment_name}.md'
        with open(report_path, 'w') as f:
            f.write(report)
        
        return report_path 