"""
Generate comprehensive metrics graphs for all 5 key metrics
Usage: python generate_metrics_graphs.py [--metrics-file path/to/metrics.json]
"""

import sys
import json
import argparse
from pathlib import Path
from typing import Dict, Any, List, Optional
import matplotlib.pyplot as plt
import numpy as np


class MetricsGraphGenerator:
    """Generate graphs for all 5 key metrics"""
    
    def __init__(self, output_dir: str = "outputs/visualizations"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Set style
        try:
            plt.style.use('seaborn-v0_8-darkgrid')
        except OSError:
            try:
                plt.style.use('seaborn-darkgrid')
            except OSError:
                plt.style.use('default')
    
    def load_metrics_from_file(self, filepath: str) -> Dict[str, Any]:
        """Load metrics from JSON file"""
        with open(filepath, 'r') as f:
            return json.load(f)
    
    def calculate_metrics(self, sessions: List[Dict[str, Any]]) -> Dict[str, float]:
        """Calculate all 5 metrics from session data"""
        if not sessions:
            return {}
        
        # 1. % of model claims with verifiable citations
        all_claims = []
        for session in sessions:
            # Extract claims from session (if stored)
            # For now, use the session metrics directly
            if "claims" in session:
                all_claims.extend(session["claims"])
        
        total_claims = len(all_claims)
        claims_with_citations = sum(1 for c in all_claims if c.get("has_citation", False))
        citation_rate = claims_with_citations / total_claims if total_claims > 0 else 0.0
        
        # 2. % of checked claims that are false or uncited
        false_uncited = sum(1 for c in all_claims if not c.get("has_citation", False) or not c.get("is_verified", True))
        false_uncited_rate = false_uncited / total_claims if total_claims > 0 else 0.0
        
        # 3. Share of gaps that flag demographic or geographic under-representation
        all_gaps = []
        for session in sessions:
            if "gaps_identified" in session:
                all_gaps.extend(session["gaps_identified"])
        
        # Only consider gaps that have sources
        applicable_gaps = [g for g in all_gaps if g.get("has_sources", False)]
        flagged_gaps = [g for g in applicable_gaps if g.get("flags_demographic", False) or g.get("flags_geographic", False)]
        flagging_rate = len(flagged_gaps) / len(applicable_gaps) if applicable_gaps else 0.0
        
        # 4. Median time from first query to first vetted gap with sources
        first_gap_times = []
        for session in sessions:
            time_to_first = session.get("time_to_first_vetted_gap")
            if time_to_first is not None:
                first_gap_times.append(time_to_first)
        
        median_time_to_gap = sorted(first_gap_times)[len(first_gap_times) // 2] if first_gap_times else 0.0
        
        # 5. % of sessions that reproduce identical outputs (from batch run)
        # This would need to be calculated from batch run data
        reproducibility_rate = 0.0  # Default, will be set from batch data if available
        
        return {
            "citation_verification_rate": citation_rate,
            "false_uncited_claims_rate": false_uncited_rate,
            "demographic_flagging_rate": flagging_rate,
            "median_time_to_first_gap": median_time_to_gap,
            "reproducibility_rate": reproducibility_rate
        }
    
    def extract_metrics_from_batch_data(self, batch_data: Dict[str, Any]) -> Dict[str, float]:
        """Extract metrics from batch run data"""
        sessions = batch_data.get("sessions", [])
        
        # Calculate from session metrics
        metrics = self.calculate_metrics(sessions)
        
        # Override reproducibility if available
        if "reproducibility_rate" in batch_data:
            metrics["reproducibility_rate"] = batch_data["reproducibility_rate"]
        
        # Aggregate citation rates from session metrics
        citation_rates = [s.get("citation_verification_rate", 0.0) for s in sessions if "citation_verification_rate" in s]
        if citation_rates:
            metrics["citation_verification_rate"] = sum(citation_rates) / len(citation_rates)
        
        # Aggregate false/uncited rates
        false_uncited_rates = [s.get("false_uncited_claims_rate", 0.0) for s in sessions if "false_uncited_claims_rate" in s]
        if false_uncited_rates:
            metrics["false_uncited_claims_rate"] = sum(false_uncited_rates) / len(false_uncited_rates)
        
        # Aggregate flagging rates
        flagging_rates = [s.get("demographic_flagging_rate", 0.0) for s in sessions if "demographic_flagging_rate" in s]
        if flagging_rates:
            metrics["demographic_flagging_rate"] = sum(flagging_rates) / len(flagging_rates)
        
        # Median time to first gap
        first_gap_times = [s.get("time_to_first_vetted_gap") for s in sessions if s.get("time_to_first_vetted_gap") is not None]
        if first_gap_times:
            metrics["median_time_to_first_gap"] = sorted(first_gap_times)[len(first_gap_times) // 2]
        
        return metrics
    
    def plot_all_metrics(self, metrics: Dict[str, float], save_path: Optional[str] = None) -> str:
        """Generate a comprehensive graph showing all 5 metrics"""
        fig, axes = plt.subplots(2, 3, figsize=(18, 12))
        axes = axes.flatten()
        
        # Define metrics with their targets
        metric_configs = [
            {
                "key": "citation_verification_rate",
                "label": "% Claims with Verifiable Citations",
                "target": 0.95,
                "unit": "%",
                "is_percentage": True,
                "higher_is_better": True,
                "color": "green" if metrics.get("citation_verification_rate", 0) >= 0.95 else "orange"
            },
            {
                "key": "false_uncited_claims_rate",
                "label": "% False/Uncited Claims",
                "target": 0.02,
                "unit": "%",
                "is_percentage": True,
                "higher_is_better": False,
                "color": "green" if metrics.get("false_uncited_claims_rate", 1.0) <= 0.02 else "red"
            },
            {
                "key": "demographic_flagging_rate",
                "label": "% Gaps Flagging Demographics/Geography",
                "target": 0.80,
                "unit": "%",
                "is_percentage": True,
                "higher_is_better": True,
                "color": "green" if metrics.get("demographic_flagging_rate", 0) >= 0.80 else "orange"
            },
            {
                "key": "median_time_to_first_gap",
                "label": "Median Time to First Vetted Gap",
                "target": 90.0,
                "unit": "s",
                "is_percentage": False,
                "higher_is_better": False,
                "color": "green" if metrics.get("median_time_to_first_gap", 999) <= 90.0 else "orange"
            },
            {
                "key": "reproducibility_rate",
                "label": "% Reproducible Sessions",
                "target": 0.95,
                "unit": "%",
                "is_percentage": True,
                "higher_is_better": True,
                "color": "green" if metrics.get("reproducibility_rate", 0) >= 0.95 else "orange"
            }
        ]
        
        # Plot each metric
        for idx, config in enumerate(metric_configs):
            ax = axes[idx]
            key = config["key"]
            value = metrics.get(key, 0.0)
            target = config["target"]
            
            # Convert to display units
            if config["is_percentage"]:
                value_display = value * 100
                target_display = target * 100
            else:
                value_display = value
                target_display = target
            
            # Determine if target met
            if config["higher_is_better"]:
                met = value >= target
            else:
                met = value <= target
            
            # Create bar chart
            bars = ax.bar(['Actual', 'Target'], 
                         [value_display, target_display],
                         color=[config["color"] if met else 'orange', 'gray'],
                         alpha=0.8, edgecolor='black', linewidth=2)
            
            # Add value labels
            for bar, val in zip(bars, [value_display, target_display]):
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height,
                       f'{val:.1f}{config["unit"]}',
                       ha='center', va='bottom', fontsize=11, fontweight='bold')
            
            # Add status indicator
            status = '✓ MET' if met else '✗ NOT MET'
            status_color = 'green' if met else 'red'
            ax.text(0.5, 0.95, status, transform=ax.transAxes,
                   ha='center', va='top', fontsize=12, fontweight='bold',
                   color=status_color,
                   bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
            
            ax.set_title(config["label"], fontsize=13, fontweight='bold', pad=10)
            ax.set_ylabel(f'Value ({config["unit"]})', fontsize=11)
            ax.grid(axis='y', alpha=0.3)
            
            # Set y-axis limits
            if config["is_percentage"]:
                ax.set_ylim(0, max(105, value_display * 1.2, target_display * 1.2))
            else:
                max_val = max(value_display, target_display) * 1.3
                ax.set_ylim(0, max_val)
        
        # Hide the 6th subplot
        axes[5].axis('off')
        
        fig.suptitle('LLM Success Metrics: All 5 Key Metrics', 
                    fontsize=18, fontweight='bold', y=0.995)
        
        plt.tight_layout()
        
        # Save figure
        if save_path is None:
            save_path = self.output_dir / "all_metrics_graph.png"
        else:
            save_path = Path(save_path)
        
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        return str(save_path)
    
    def plot_metrics_summary(self, metrics: Dict[str, float], save_path: Optional[str] = None) -> str:
        """Generate a summary dashboard with all metrics"""
        fig, ax = plt.subplots(figsize=(14, 8))
        
        # Prepare data
        labels = [
            "Citation\nVerification",
            "False/Uncited\nClaims",
            "Demographic\nFlagging",
            "Time to Gap\n(seconds)",
            "Reproducibility"
        ]
        
        values = [
            metrics.get("citation_verification_rate", 0.0) * 100,
            metrics.get("false_uncited_claims_rate", 0.0) * 100,
            metrics.get("demographic_flagging_rate", 0.0) * 100,
            metrics.get("median_time_to_first_gap", 0.0),
            metrics.get("reproducibility_rate", 0.0) * 100
        ]
        
        targets = [95.0, 2.0, 80.0, 90.0, 95.0]
        colors = ['#2E86AB', '#A23B72', '#F18F01', '#C73E1D', '#6C757D']
        
        x = np.arange(len(labels))
        width = 0.35
        
        # Plot actual and target
        bars1 = ax.bar(x - width/2, values, width, label='Actual', 
                      color=colors, alpha=0.8, edgecolor='black', linewidth=1.5)
        bars2 = ax.bar(x + width/2, targets, width, label='Target', 
                      color='gray', alpha=0.6, edgecolor='black', linewidth=1.5)
        
        # Add value labels
        for bars in [bars1, bars2]:
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height,
                       f'{height:.1f}',
                       ha='center', va='bottom', fontsize=9, fontweight='bold')
        
        ax.set_ylabel('Value', fontsize=14, fontweight='bold')
        ax.set_xlabel('Metric', fontsize=14, fontweight='bold')
        ax.set_title('LLM Success Metrics Dashboard', fontsize=16, fontweight='bold', pad=20)
        ax.set_xticks(x)
        ax.set_xticklabels(labels, fontsize=11)
        ax.legend(loc='upper right', fontsize=12, framealpha=0.9)
        ax.grid(axis='y', alpha=0.3, linestyle='--')
        
        plt.tight_layout()
        
        if save_path is None:
            save_path = self.output_dir / "metrics_summary_dashboard.png"
        else:
            save_path = Path(save_path)
        
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        return str(save_path)


def main():
    parser = argparse.ArgumentParser(description="Generate comprehensive metrics graphs")
    parser.add_argument("--metrics-file", type=str, default="batch_metrics.json", 
                       help="JSON file with batch metrics")
    parser.add_argument("--output-dir", type=str, default="outputs/visualizations",
                       help="Output directory for graphs")
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("Generating Metrics Graphs")
    print("=" * 60)
    print()
    
    generator = MetricsGraphGenerator(output_dir=args.output_dir)
    
    # Load metrics
    if not Path(args.metrics_file).exists():
        print(f"Error: Metrics file not found: {args.metrics_file}")
        print("\nTo generate metrics, first run:")
        print("  python run_metrics_batch.py --sessions 5 --output batch_metrics.json")
        sys.exit(1)
    
    print(f"Loading metrics from: {args.metrics_file}")
    batch_data = generator.load_metrics_from_file(args.metrics_file)
    
    # Extract metrics
    metrics = generator.extract_metrics_from_batch_data(batch_data)
    
    print(f"\nMetrics calculated from {batch_data.get('total_sessions', 0)} sessions:")
    print(f"  1. Citation Verification Rate: {metrics.get('citation_verification_rate', 0)*100:.1f}%")
    print(f"  2. False/Uncited Claims Rate: {metrics.get('false_uncited_claims_rate', 0)*100:.1f}%")
    print(f"  3. Demographic Flagging Rate: {metrics.get('demographic_flagging_rate', 0)*100:.1f}%")
    print(f"  4. Median Time to First Gap: {metrics.get('median_time_to_first_gap', 0):.1f}s")
    print(f"  5. Reproducibility Rate: {metrics.get('reproducibility_rate', 0)*100:.1f}%")
    print()
    
    # Generate graphs
    print("Generating graphs...")
    all_metrics_path = generator.plot_all_metrics(metrics)
    summary_path = generator.plot_metrics_summary(metrics)
    
    print(f"\n✓ Graphs generated:")
    print(f"  - All metrics graph: {all_metrics_path}")
    print(f"  - Summary dashboard: {summary_path}")
    print("\nTo view graphs, run:")
    print(f"  python view_metrics_graphs.py --dir {args.output_dir}")
    print("=" * 60)


if __name__ == "__main__":
    main()

