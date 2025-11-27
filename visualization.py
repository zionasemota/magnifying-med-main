"""
Visualization module for generating graphs and plots comparing LLM analysis to baselines
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
from typing import Dict, Any, List, Optional, Tuple
import os
from pathlib import Path


class BiasVisualizer:
    """Generate visualizations for bias analysis and baseline comparisons"""
    
    def __init__(self, output_dir: str = "outputs/visualizations"):
        """
        Initialize visualizer
        
        Args:
            output_dir: Directory to save visualization files
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Set style (try seaborn-v0_8-darkgrid, fallback to seaborn-darkgrid or default)
        try:
            plt.style.use('seaborn-v0_8-darkgrid')
        except OSError:
            try:
                plt.style.use('seaborn-darkgrid')
            except OSError:
                plt.style.use('default')
        self.colors = {
            'primary': '#2E86AB',
            'secondary': '#A23B72',
            'accent': '#F18F01',
            'success': '#C73E1D',
            'baseline': '#6C757D',
            'llm': '#2E86AB',
            'warning': '#FFC107'
        }
    
    def plot_score_comparison(self, llm_scores: Dict[str, float], 
                             baseline_scores: Optional[Dict[str, float]] = None,
                             scope: str = "Medical AI",
                             save_path: Optional[str] = None) -> str:
        """
        Generate bar chart comparing LLM bias scores to baseline
        
        Args:
            llm_scores: Dictionary of bias score components from LLM analysis
            baseline_scores: Optional baseline scores for comparison
            scope: Medical field/scope being analyzed
            save_path: Optional path to save the figure
            
        Returns:
            Path to saved figure
        """
        fig, ax = plt.subplots(figsize=(12, 7))
        
        categories = list(llm_scores.keys())
        llm_values = [llm_scores.get(cat, 0.0) for cat in categories]
        
        x = np.arange(len(categories))
        width = 0.35
        
        # Format category names for display
        display_names = [self._format_category_name(cat) for cat in categories]
        
        # Plot LLM scores
        bars1 = ax.bar(x - width/2 if baseline_scores else x, llm_values, 
                      width, label='MagnifyingMed LLM', color=self.colors['llm'], 
                      alpha=0.8, edgecolor='black', linewidth=1.2)
        
        # Plot baseline if provided
        if baseline_scores:
            baseline_values = [baseline_scores.get(cat, 0.0) for cat in categories]
            bars2 = ax.bar(x + width/2, baseline_values, width, 
                          label='Baseline', color=self.colors['baseline'], 
                          alpha=0.8, edgecolor='black', linewidth=1.2)
            
            # Add value labels on bars
            for bars in [bars1, bars2]:
                for bar in bars:
                    height = bar.get_height()
                    ax.text(bar.get_x() + bar.get_width()/2., height,
                           f'{height:.2f}',
                           ha='center', va='bottom', fontsize=9, fontweight='bold')
        else:
            # Add value labels for single set
            for bar in bars1:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height,
                       f'{height:.2f}',
                       ha='center', va='bottom', fontsize=9, fontweight='bold')
        
        # Customize plot
        ax.set_ylabel('Bias Score Component', fontsize=12, fontweight='bold')
        ax.set_xlabel('Bias Dimension', fontsize=12, fontweight='bold')
        ax.set_title(f'Bias Score Breakdown: {scope}\n(LLM vs Baseline Comparison)', 
                    fontsize=14, fontweight='bold', pad=20)
        ax.set_xticks(x)
        ax.set_xticklabels(display_names, rotation=45, ha='right', fontsize=10)
        ax.set_ylim(0, 1.1)
        ax.legend(loc='upper right', fontsize=11, framealpha=0.9)
        ax.grid(axis='y', alpha=0.3, linestyle='--')
        
        # Add threshold line
        ax.axhline(y=0.3, color='red', linestyle='--', linewidth=2, 
                  alpha=0.7, label='Flag Threshold (0.30)')
        
        plt.tight_layout()
        
        # Save figure
        if save_path is None:
            save_path = self.output_dir / f"score_comparison_{scope.lower().replace(' ', '_')}.png"
        else:
            save_path = Path(save_path)
        
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        return str(save_path)
    
    def plot_overall_score_comparison(self, results: List[Dict[str, Any]], 
                                     baseline_scores: Optional[List[float]] = None,
                                     save_path: Optional[str] = None) -> str:
        """
        Generate comparison of overall bias scores across multiple analyses
        
        Args:
            results: List of analysis results, each with 'scope' and 'score_results'
            baseline_scores: Optional list of baseline overall scores
            save_path: Optional path to save the figure
            
        Returns:
            Path to saved figure
        """
        fig, ax = plt.subplots(figsize=(14, 8))
        
        scopes = [r.get('scope', 'Unknown') for r in results]
        llm_scores = [r.get('score_results', {}).get('score', 0.0) for r in results]
        
        x = np.arange(len(scopes))
        width = 0.35
        
        # Plot LLM scores
        bars1 = ax.bar(x - width/2 if baseline_scores else x, llm_scores, 
                      width, label='MagnifyingMed LLM', color=self.colors['llm'], 
                      alpha=0.8, edgecolor='black', linewidth=1.5)
        
        # Plot baseline if provided
        if baseline_scores:
            bars2 = ax.bar(x + width/2, baseline_scores, width, 
                          label='Baseline', color=self.colors['baseline'], 
                          alpha=0.8, edgecolor='black', linewidth=1.5)
            
            # Add value labels
            for bars in [bars1, bars2]:
                for bar in bars:
                    height = bar.get_height()
                    ax.text(bar.get_x() + bar.get_width()/2., height,
                           f'{height:.3f}',
                           ha='center', va='bottom', fontsize=9, fontweight='bold')
        else:
            # Add value labels for single set
            for bar in bars1:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height,
                       f'{height:.3f}',
                       ha='center', va='bottom', fontsize=9, fontweight='bold')
        
        # Customize plot
        ax.set_ylabel('Overall Bias Score', fontsize=13, fontweight='bold')
        ax.set_xlabel('Medical Field/Scope', fontsize=13, fontweight='bold')
        ax.set_title('Overall Bias Score Comparison Across Medical Fields\n(LLM vs Baseline)', 
                    fontsize=15, fontweight='bold', pad=20)
        ax.set_xticks(x)
        ax.set_xticklabels(scopes, rotation=45, ha='right', fontsize=11)
        ax.set_ylim(0, 1.0)
        ax.legend(loc='upper right', fontsize=12, framealpha=0.9)
        ax.grid(axis='y', alpha=0.3, linestyle='--')
        
        # Add threshold line
        ax.axhline(y=0.3, color='red', linestyle='--', linewidth=2, 
                  alpha=0.7, label='Flag Threshold (0.30)')
        
        plt.tight_layout()
        
        # Save figure
        if save_path is None:
            save_path = self.output_dir / "overall_score_comparison.png"
        else:
            save_path = Path(save_path)
        
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        return str(save_path)
    
    def plot_driver_analysis(self, score_results: Dict[str, Any], 
                            scope: str = "Medical AI",
                            save_path: Optional[str] = None) -> str:
        """
        Generate pie chart or horizontal bar chart showing bias drivers
        
        Args:
            score_results: Score results with breakdown and drivers
            scope: Medical field/scope being analyzed
            save_path: Optional path to save the figure
            
        Returns:
            Path to saved figure
        """
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 7))
        
        breakdown = score_results.get('breakdown', {})
        drivers = score_results.get('drivers', [])
        
        # Left plot: Breakdown pie chart
        categories = list(breakdown.keys())
        values = [breakdown.get(cat, 0.0) for cat in categories]
        display_names = [self._format_category_name(cat) for cat in categories]
        
        # Create color map
        colors_list = plt.cm.Set3(np.linspace(0, 1, len(categories)))
        
        wedges, texts, autotexts = ax1.pie(values, labels=display_names, 
                                           autopct='%1.1f%%', colors=colors_list,
                                           startangle=90, textprops={'fontsize': 9})
        
        ax1.set_title(f'Bias Score Component Distribution\n{scope}', 
                     fontsize=12, fontweight='bold', pad=15)
        
        # Right plot: Driver importance (horizontal bar)
        if drivers:
            driver_names = [d.split(':')[0] if ':' in d else d[:30] for d in drivers]
            # Extract scores from breakdown for drivers
            driver_scores = []
            for driver in drivers:
                # Try to match driver to breakdown category
                matched = False
                for cat in categories:
                    if cat.replace('_', ' ').lower() in driver.lower():
                        driver_scores.append(breakdown[cat])
                        matched = True
                        break
                if not matched:
                    driver_scores.append(0.5)  # Default if not found
            
            y_pos = np.arange(len(driver_names))
            bars = ax2.barh(y_pos, driver_scores, color=self.colors['accent'], 
                           alpha=0.8, edgecolor='black', linewidth=1.2)
            
            ax2.set_yticks(y_pos)
            ax2.set_yticklabels(driver_names, fontsize=10)
            ax2.set_xlabel('Score', fontsize=11, fontweight='bold')
            ax2.set_title('Top Bias Drivers', fontsize=12, fontweight='bold', pad=15)
            ax2.set_xlim(0, 1.0)
            ax2.grid(axis='x', alpha=0.3, linestyle='--')
            
            # Add value labels
            for i, (bar, score) in enumerate(zip(bars, driver_scores)):
                ax2.text(score + 0.02, bar.get_y() + bar.get_height()/2,
                        f'{score:.2f}', va='center', fontsize=9, fontweight='bold')
        
        plt.tight_layout()
        
        # Save figure
        if save_path is None:
            save_path = self.output_dir / f"driver_analysis_{scope.lower().replace(' ', '_')}.png"
        else:
            save_path = Path(save_path)
        
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        return str(save_path)
    
    def plot_trend_analysis(self, historical_results: List[Dict[str, Any]],
                           save_path: Optional[str] = None) -> str:
        """
        Generate line plot showing bias score trends over time
        
        Args:
            historical_results: List of results with 'year' or 'date' and 'score_results'
            save_path: Optional path to save the figure
            
        Returns:
            Path to saved figure
        """
        fig, ax = plt.subplots(figsize=(12, 7))
        
        # Extract data
        years = []
        scores = []
        for result in historical_results:
            year = result.get('year') or result.get('date', {}).get('year')
            if year:
                years.append(year)
                scores.append(result.get('score_results', {}).get('score', 0.0))
        
        if not years:
            # If no years, use index
            years = list(range(len(historical_results)))
            scores = [r.get('score_results', {}).get('score', 0.0) for r in historical_results]
        
        # Sort by year
        sorted_data = sorted(zip(years, scores))
        years, scores = zip(*sorted_data) if sorted_data else ([], [])
        
        # Plot
        ax.plot(years, scores, marker='o', linewidth=2.5, markersize=8,
               color=self.colors['llm'], label='Bias Score Trend', 
               markerfacecolor='white', markeredgewidth=2, markeredgecolor=self.colors['llm'])
        
        # Add threshold line
        ax.axhline(y=0.3, color='red', linestyle='--', linewidth=2, 
                  alpha=0.7, label='Flag Threshold (0.30)')
        
        # Customize
        ax.set_xlabel('Year', fontsize=12, fontweight='bold')
        ax.set_ylabel('Overall Bias Score', fontsize=12, fontweight='bold')
        ax.set_title('Bias Score Trend Over Time', fontsize=14, fontweight='bold', pad=20)
        ax.legend(loc='best', fontsize=11, framealpha=0.9)
        ax.grid(True, alpha=0.3, linestyle='--')
        ax.set_ylim(0, 1.0)
        
        # Add value labels
        for year, score in zip(years, scores):
            ax.text(year, score + 0.03, f'{score:.3f}', 
                   ha='center', fontsize=9, fontweight='bold')
        
        plt.tight_layout()
        
        # Save figure
        if save_path is None:
            save_path = self.output_dir / "trend_analysis.png"
        else:
            save_path = Path(save_path)
        
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        return str(save_path)
    
    def plot_dataset_composition(self, dataset_analysis: Dict[str, Any],
                                scope: str = "Medical AI",
                                save_path: Optional[str] = None) -> str:
        """
        Generate visualization of dataset composition issues
        
        Args:
            dataset_analysis: Dataset analysis results
            scope: Medical field/scope being analyzed
            save_path: Optional path to save the figure
            
        Returns:
            Path to saved figure
        """
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
        
        summary = dataset_analysis.get('summary', {})
        
        # Plot 1: Race label availability
        total = summary.get('total_datasets', 0)
        with_labels = summary.get('datasets_with_race_labels', 0)
        without_labels = total - with_labels
        
        if total > 0:
            ax1.bar(['With Labels', 'Without Labels'], 
                   [with_labels, without_labels],
                   color=[self.colors['success'], self.colors['warning']],
                   alpha=0.8, edgecolor='black', linewidth=1.5)
            ax1.set_title('Race Label Availability', fontsize=11, fontweight='bold')
            ax1.set_ylabel('Number of Datasets', fontsize=10)
            ax1.grid(axis='y', alpha=0.3)
            
            # Add value labels
            for i, v in enumerate([with_labels, without_labels]):
                ax1.text(i, v + 0.5, str(v), ha='center', fontweight='bold')
        
        # Plot 2: Dark skin representation
        dark_skin_prop = summary.get('avg_dark_skin_proportion', 0.0)
        target = 0.25
        
        categories = ['Current', 'Target']
        values = [dark_skin_prop, target]
        colors_list = [self.colors['warning'], self.colors['success']]
        
        bars = ax2.bar(categories, values, color=colors_list, alpha=0.8, 
                      edgecolor='black', linewidth=1.5)
        ax2.set_title('Dark Skin Representation', fontsize=11, fontweight='bold')
        ax2.set_ylabel('Proportion', fontsize=10)
        ax2.set_ylim(0, max(values) * 1.3)
        ax2.grid(axis='y', alpha=0.3)
        
        # Add value labels
        for bar, val in zip(bars, values):
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height,
                   f'{val:.1%}', ha='center', va='bottom', fontweight='bold')
        
        # Plot 3: Minority representation
        minority_rep = summary.get('avg_minority_representation', 0.0)
        target_minority = 0.25
        
        categories = ['Current', 'Target']
        values = [minority_rep, target_minority]
        
        bars = ax3.bar(categories, values, color=colors_list, alpha=0.8,
                      edgecolor='black', linewidth=1.5)
        ax3.set_title('Minority Representation', fontsize=11, fontweight='bold')
        ax3.set_ylabel('Proportion', fontsize=10)
        ax3.set_ylim(0, max(values) * 1.3 if values else 0.3)
        ax3.grid(axis='y', alpha=0.3)
        
        # Add value labels
        for bar, val in zip(bars, values):
            height = bar.get_height()
            ax3.text(bar.get_x() + bar.get_width()/2., height,
                   f'{val:.1%}', ha='center', va='bottom', fontweight='bold')
        
        # Plot 4: Geographic diversity
        geo_diversity = summary.get('geographic_diversity', 'low')
        diversity_map = {'low': 0.33, 'medium': 0.66, 'high': 1.0}
        diversity_score = diversity_map.get(geo_diversity.lower(), 0.33)
        
        ax4.barh(['Geographic Diversity'], [diversity_score],
                color=self.colors['accent'], alpha=0.8, edgecolor='black', linewidth=1.5)
        ax4.set_xlim(0, 1.0)
        ax4.set_title(f'Geographic Diversity: {geo_diversity.title()}', 
                     fontsize=11, fontweight='bold')
        ax4.set_xlabel('Diversity Score', fontsize=10)
        ax4.grid(axis='x', alpha=0.3)
        
        # Add value label
        ax4.text(diversity_score/2, 0, f'{geo_diversity.title()}', 
               ha='center', va='center', fontweight='bold', fontsize=12)
        
        fig.suptitle(f'Dataset Composition Analysis: {scope}', 
                    fontsize=14, fontweight='bold', y=0.995)
        
        plt.tight_layout()
        
        # Save figure
        if save_path is None:
            save_path = self.output_dir / f"dataset_composition_{scope.lower().replace(' ', '_')}.png"
        else:
            save_path = Path(save_path)
        
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        return str(save_path)
    
    def _format_category_name(self, category: str) -> str:
        """Format category name for display"""
        return category.replace('_', ' ').title()
    
    def plot_success_metrics(self, metrics_data: Dict[str, Any],
                            save_path: Optional[str] = None) -> str:
        """
        Generate visualization of success metrics vs targets
        
        Args:
            metrics_data: Dictionary with metrics from MetricsTracker
            save_path: Optional path to save the figure
            
        Returns:
            Path to saved figure
        """
        fig, axes = plt.subplots(2, 3, figsize=(18, 12))
        axes = axes.flatten()
        
        metrics = metrics_data.get('metrics', {})
        
        # Define metric order and positions
        metric_configs = [
            ('citation_verification_rate', 0, '≥', 'green'),
            ('false_uncited_claims_rate', 1, '≤', 'red'),
            ('demographic_flagging_rate', 2, '≥', 'green'),
            ('time_to_first_gap', 3, '≤', 'red'),
            ('reproducibility_rate', 4, '≥', 'green')
        ]
        
        for metric_key, idx, comparison, color in metric_configs:
            if metric_key not in metrics:
                axes[idx].axis('off')
                continue
            
            metric = metrics[metric_key]
            value = metric['value']
            target = metric['target']
            met = metric.get('met', False)
            label = metric['label']
            unit = metric['unit']
            
            ax = axes[idx]
            
            # Determine if it's a percentage or time metric
            is_percentage = unit == '%'
            is_time = unit == 's'
            
            # Normalize values for comparison
            if is_percentage:
                value_display = value * 100
                target_display = target * 100
            else:
                value_display = value
                target_display = target
            
            # Create bar chart
            bars = ax.bar(['Actual', 'Target'], 
                         [value_display, target_display],
                         color=[color if met else 'orange', 'gray'],
                         alpha=0.8, edgecolor='black', linewidth=2)
            
            # Add value labels
            for bar, val in zip(bars, [value_display, target_display]):
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height,
                       f'{val:.1f}{unit}',
                       ha='center', va='bottom', fontsize=12, fontweight='bold')
            
            # Add status indicator
            status = '✓ MET' if met else '✗ NOT MET'
            status_color = 'green' if met else 'red'
            ax.text(0.5, 0.95, status, transform=ax.transAxes,
                   ha='center', va='top', fontsize=14, fontweight='bold',
                   color=status_color,
                   bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
            
            ax.set_title(label, fontsize=14, fontweight='bold', pad=10)
            ax.set_ylabel(f'Value ({unit})', fontsize=11)
            ax.grid(axis='y', alpha=0.3)
            
            # Set y-axis limits appropriately
            if is_percentage:
                ax.set_ylim(0, 105)
            elif is_time:
                max_val = max(value_display, target_display) * 1.2
                ax.set_ylim(0, max_val)
            else:
                max_val = max(value_display, target_display) * 1.2
                ax.set_ylim(0, max_val)
        
        # Hide the 6th subplot
        axes[5].axis('off')
        
        fig.suptitle('Success Metrics: Actual vs Target Performance', 
                    fontsize=18, fontweight='bold', y=0.995)
        
        plt.tight_layout()
        
        # Save figure
        if save_path is None:
            save_path = self.output_dir / "success_metrics.png"
        else:
            save_path = Path(save_path)
        
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        return str(save_path)
    
    def plot_combined_comparison(self, llm_results: Dict[str, Any],
                                baseline_comparison: Dict[str, Any],
                                metrics_data: Optional[Dict[str, Any]] = None,
                                scope: str = "Medical AI",
                                save_path: Optional[str] = None) -> str:
        """
        Generate combined visualization with bias scores and success metrics
        
        Args:
            llm_results: LLM analysis results
            baseline_comparison: Baseline comparison data
            metrics_data: Optional success metrics data
            scope: Medical field/scope
            save_path: Optional path to save
            
        Returns:
            Path to saved figure
        """
        if metrics_data:
            # Create figure with two rows: bias comparison and metrics
            fig = plt.figure(figsize=(20, 14))
            
            # Top: Bias score comparison (larger)
            gs = fig.add_gridspec(2, 1, height_ratios=[2, 1], hspace=0.3)
            ax1 = fig.add_subplot(gs[0])
            ax2 = fig.add_subplot(gs[1])
            
            # Bias comparison plot
            llm_breakdown = llm_results.get('score_results', {}).get('breakdown', {})
            baseline_breakdown = baseline_comparison.get('baseline_breakdown', {})
            
            categories = list(llm_breakdown.keys())
            llm_values = [llm_breakdown.get(cat, 0.0) for cat in categories]
            baseline_values = [baseline_breakdown.get(cat, 0.0) for cat in categories]
            
            display_names = [self._format_category_name(cat) for cat in categories]
            x = np.arange(len(categories))
            width = 0.35
            
            bars1 = ax1.bar(x - width/2, llm_values, width,
                          label='MagnifyingMed LLM', color=self.colors['llm'],
                          alpha=0.9, edgecolor='black', linewidth=2)
            bars2 = ax1.bar(x + width/2, baseline_values, width,
                          label='Baseline', color=self.colors['baseline'],
                          alpha=0.9, edgecolor='black', linewidth=2)
            
            for bars in [bars1, bars2]:
                for bar in bars:
                    height = bar.get_height()
                    ax1.text(bar.get_x() + bar.get_width()/2., height + 0.02,
                           f'{height:.2f}',
                           ha='center', va='bottom', fontsize=11, fontweight='bold')
            
            ax1.set_ylabel('Bias Score Component', fontsize=16, fontweight='bold')
            ax1.set_xlabel('Bias Dimension', fontsize=16, fontweight='bold')
            ax1.set_title(f'Bias Score Comparison: {scope}', 
                         fontsize=18, fontweight='bold', pad=20)
            ax1.set_xticks(x)
            ax1.set_xticklabels(display_names, rotation=45, ha='right', fontsize=12)
            ax1.set_ylim(0, 1.15)
            ax1.legend(loc='upper right', fontsize=14, framealpha=0.95)
            ax1.grid(axis='y', alpha=0.3, linestyle='--')
            ax1.axhline(y=0.3, color='red', linestyle='--', linewidth=2, alpha=0.7)
            
            # Success metrics plot (simplified)
            metrics = metrics_data.get('metrics', {})
            metric_keys = ['citation_verification_rate', 'false_uncited_claims_rate', 
                         'demographic_flagging_rate', 'time_to_first_gap']
            
            metric_labels = []
            actual_values = []
            target_values = []
            met_status = []
            
            for key in metric_keys:
                if key in metrics:
                    metric = metrics[key]
                    metric_labels.append(metric['label'][:30])  # Truncate long labels
                    if metric['unit'] == '%':
                        actual_values.append(metric['value'] * 100)
                        target_values.append(metric['target'] * 100)
                    else:
                        actual_values.append(metric['value'])
                        target_values.append(metric['target'])
                    met_status.append(metric.get('met', False))
            
            if metric_labels:
                x_metrics = np.arange(len(metric_labels))
                width_metrics = 0.35
                
                colors_actual = ['green' if met else 'orange' for met in met_status]
                bars_actual = ax2.bar(x_metrics - width_metrics/2, actual_values, width_metrics,
                                     label='Actual', color=colors_actual, alpha=0.8,
                                     edgecolor='black', linewidth=1.5)
                bars_target = ax2.bar(x_metrics + width_metrics/2, target_values, width_metrics,
                                    label='Target', color='gray', alpha=0.8,
                                    edgecolor='black', linewidth=1.5)
                
                for bar in bars_actual:
                    height = bar.get_height()
                    ax2.text(bar.get_x() + bar.get_width()/2., height,
                           f'{height:.1f}',
                           ha='center', va='bottom', fontsize=9, fontweight='bold')
                
                ax2.set_ylabel('Value', fontsize=14, fontweight='bold')
                ax2.set_title('Success Metrics: Actual vs Target', fontsize=16, fontweight='bold', pad=15)
                ax2.set_xticks(x_metrics)
                ax2.set_xticklabels(metric_labels, rotation=45, ha='right', fontsize=10)
                ax2.legend(loc='upper right', fontsize=12)
                ax2.grid(axis='y', alpha=0.3)
            
            fig.suptitle(f'MagnifyingMed Performance: Bias Analysis & Success Metrics\n{scope}',
                        fontsize=20, fontweight='bold', y=0.995)
            
            plt.tight_layout()
            
            if save_path is None:
                save_path = self.output_dir / f"combined_comparison_{scope.lower().replace(' ', '_')}.png"
            else:
                save_path = Path(save_path)
            
            plt.savefig(save_path, dpi=600, bbox_inches='tight', facecolor='white')
            plt.close()
            
            return str(save_path)
        else:
            # Fallback to regular comparison if no metrics
            return self.plot_score_comparison(
                llm_results.get('score_results', {}).get('breakdown', {}),
                baseline_comparison.get('baseline_breakdown', {}),
                scope, save_path
            )
    
    def generate_comparison_report(self, llm_results: Dict[str, Any],
                                  baseline_results: Optional[Dict[str, Any]] = None,
                                  scope: str = "Medical AI") -> Dict[str, str]:
        """
        Generate a comprehensive comparison report with multiple visualizations
        
        Args:
            llm_results: LLM analysis results
            baseline_results: Optional baseline results for comparison
            scope: Medical field/scope being analyzed
            
        Returns:
            Dictionary mapping visualization type to file path
        """
        report_paths = {}
        
        # Extract data
        score_results = llm_results.get('score_results', {})
        breakdown = score_results.get('breakdown', {})
        
        baseline_breakdown = None
        if baseline_results:
            baseline_breakdown = baseline_results.get('score_results', {}).get('breakdown', {})
        
        # Generate visualizations
        report_paths['score_comparison'] = self.plot_score_comparison(
            breakdown, baseline_breakdown, scope
        )
        
        report_paths['driver_analysis'] = self.plot_driver_analysis(
            score_results, scope
        )
        
        if 'dataset_analysis' in llm_results:
            report_paths['dataset_composition'] = self.plot_dataset_composition(
                llm_results['dataset_analysis'], scope
            )
        
        return report_paths

