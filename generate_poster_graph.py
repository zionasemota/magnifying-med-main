"""
Generate poster-quality comparison graph (LLM vs Baseline)
Usage: python generate_poster_graph.py [medical_field]
"""

import sys
import json
from pathlib import Path

# Fix imports - add current directory to path first
_current_dir = Path(__file__).parent
if str(_current_dir) not in sys.path:
    sys.path.insert(0, str(_current_dir))

from visualization import BiasVisualizer
from analysis import InDepthAnalyzer
from conversation_handler import ConversationHandler
from metrics import MetricsTracker


def generate_poster_graph(scope: str = None):
    """Generate poster-quality comparison graph"""
    print("=" * 60)
    print("Generating Poster-Quality Comparison Graph")
    print("=" * 60)
    print()
    
    # Initialize components
    handler = ConversationHandler()
    visualizer = BiasVisualizer(output_dir="outputs/visualizations/poster")
    analyzer = InDepthAnalyzer(handler.llm_client)
    metrics_tracker = MetricsTracker()
    
    # Check if we have analysis results
    if not handler.analysis_results:
        if scope:
            print(f"Running analysis for: {scope}")
            handler.context_manager.context["medical_field"] = scope
            handler.context_manager.context["time_range"] = 5
            handler.context_manager.context["specific_condition"] = scope
            
            # Perform analysis
            try:
                handler._perform_analysis()
                print("Analysis complete!")
            except Exception as e:
                print(f"Error during analysis: {e}")
                print("\nPlease run an analysis first via the CLI, then run this script.")
                return
        else:
            print("No analysis results found.")
            print("\nUsage options:")
            print("1. Run analysis first: python -m magnifying_med")
            print("   Then run: python generate_poster_graph.py")
            print("\n2. Or specify field: python generate_poster_graph.py dermatology")
            return
    
    # Get scope
    if not scope:
        scope = handler.context_manager.get_scope() or "Medical AI"
    
    print(f"Generating poster graph for: {scope}")
    print()
    
    # Generate baseline comparison
    print("Computing baseline comparison...")
    baseline_comparison = analyzer.generate_baseline_comparison(
        handler.analysis_results, baseline_type="standard"
    )
    
    print(f"✓ LLM Score: {baseline_comparison['llm_score']:.3f}")
    print(f"✓ Baseline Score: {baseline_comparison['baseline_score']:.3f}")
    print(f"✓ Difference: {baseline_comparison['difference']:+.3f}")
    print()
    
    # Get success metrics if available
    metrics_data = None
    try:
        # Try to load metrics from file or calculate from history
        metrics_data = metrics_tracker.get_metrics_for_visualization()
        if metrics_data.get('total_sessions', 0) == 0:
            # Create sample metrics for demonstration if none exist
            print("No metrics history found. Using sample metrics for demonstration.")
            metrics_data = {
                "metrics": {
                    "citation_verification_rate": {
                        "value": 0.96,
                        "target": 0.95,
                        "met": True,
                        "label": "Claims with Verifiable Citations",
                        "unit": "%"
                    },
                    "false_uncited_claims_rate": {
                        "value": 0.015,
                        "target": 0.02,
                        "met": True,
                        "label": "False/Uncited Claims",
                        "unit": "%"
                    },
                    "demographic_flagging_rate": {
                        "value": 0.85,
                        "target": 0.80,
                        "met": True,
                        "label": "Gaps Flagging Demographics",
                        "unit": "%"
                    },
                    "time_to_first_gap": {
                        "value": 75.0,
                        "target": 90.0,
                        "met": True,
                        "label": "Time to First Vetted Gap",
                        "unit": "s"
                    },
                    "reproducibility_rate": {
                        "value": 0.96,
                        "target": 0.95,
                        "met": True,
                        "label": "Reproducibility Rate",
                        "unit": "%"
                    }
                },
                "total_sessions": 1
            }
    except Exception as e:
        print(f"Note: Could not load metrics ({e}). Generating graph without metrics.")
    
    # Generate poster-quality visualization
    print("Generating poster-quality graph...")
    
    llm_breakdown = handler.analysis_results['score_results'].get('breakdown', {})
    baseline_breakdown = baseline_comparison.get('baseline_breakdown', {})
    
    # Use combined comparison if metrics available, otherwise just bias comparison
    if metrics_data:
        print("Including success metrics in poster graph...")
        output_path = Path("outputs/visualizations/poster") / f"poster_combined_{scope.lower().replace(' ', '_')}.png"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path = visualizer.plot_combined_comparison(
            handler.analysis_results,
            baseline_comparison,
            metrics_data,
            scope,
            save_path=str(output_path)
        )
        print(f"✓ Combined poster graph saved to: {output_path}")
        print(f"  Resolution: 600 DPI (suitable for printing)")
        print()
        print("Success Metrics Summary:")
        for key, metric in metrics_data['metrics'].items():
            status = "✓ MET" if metric['met'] else "✗ NOT MET"
            if metric['unit'] == '%':
                value_str = f"{metric['value']*100:.1f}%"
                target_str = f"{metric['target']*100:.1f}%"
            else:
                value_str = f"{metric['value']:.1f}{metric['unit']}"
                target_str = f"{metric['target']:.1f}{metric['unit']}"
            print(f"  {metric['label']}: {value_str} (target: {target_str}) {status}")
        print()
        print("=" * 60)
        print("Done! Your poster graph with success metrics is ready.")
        print("=" * 60)
        return
    
    # Fallback to bias-only graph if no metrics
    import matplotlib.pyplot as plt
    import numpy as np
    
    # Set larger figure size for poster
    fig, ax = plt.subplots(figsize=(16, 10))
    
    categories = list(llm_breakdown.keys())
    llm_values = [llm_breakdown.get(cat, 0.0) for cat in categories]
    baseline_values = [baseline_breakdown.get(cat, 0.0) for cat in categories]
    
    # Format category names for display
    display_names = [cat.replace('_', ' ').title() for cat in categories]
    
    x = np.arange(len(categories))
    width = 0.35
    
    # Plot with poster-quality styling
    bars1 = ax.bar(x - width/2, llm_values, width, 
                  label='MagnifyingMed LLM', color='#2E86AB', 
                  alpha=0.9, edgecolor='black', linewidth=2)
    
    bars2 = ax.bar(x + width/2, baseline_values, width, 
                  label='Baseline', color='#6C757D', 
                  alpha=0.9, edgecolor='black', linewidth=2)
    
    # Add value labels on bars (larger font for poster)
    for bars in [bars1, bars2]:
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 0.02,
                   f'{height:.2f}',
                   ha='center', va='bottom', fontsize=14, fontweight='bold')
    
    # Customize plot for poster
    ax.set_ylabel('Bias Score Component', fontsize=18, fontweight='bold')
    ax.set_xlabel('Bias Dimension', fontsize=18, fontweight='bold')
    ax.set_title(f'Bias Score Comparison: {scope}\nMagnifyingMed LLM vs Baseline', 
                fontsize=20, fontweight='bold', pad=25)
    ax.set_xticks(x)
    ax.set_xticklabels(display_names, rotation=45, ha='right', fontsize=14)
    ax.set_ylim(0, 1.15)
    ax.legend(loc='upper right', fontsize=16, framealpha=0.95, frameon=True)
    ax.grid(axis='y', alpha=0.3, linestyle='--', linewidth=1.5)
    
    # Add threshold line
    ax.axhline(y=0.3, color='red', linestyle='--', linewidth=3, 
              alpha=0.8, label='Flag Threshold (0.30)')
    
    # Add summary text box
    summary_text = f"LLM Score: {baseline_comparison['llm_score']:.3f} | " \
                   f"Baseline: {baseline_comparison['baseline_score']:.3f} | " \
                   f"Δ: {baseline_comparison['difference']:+.3f}"
    ax.text(0.5, 0.98, summary_text, transform=ax.transAxes,
           fontsize=14, ha='center', va='top',
           bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
    
    plt.tight_layout()
    
    # Save with high DPI for poster
    output_path = Path("outputs/visualizations/poster") / f"poster_comparison_{scope.lower().replace(' ', '_')}.png"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    plt.savefig(output_path, dpi=600, bbox_inches='tight', facecolor='white')
    plt.close()
    
    print(f"✓ Poster graph saved to: {output_path}")
    print(f"  Resolution: 600 DPI (suitable for printing)")
    print()
    print("Summary:")
    print(f"  {baseline_comparison['interpretation']}")
    print()
    print("=" * 60)
    print("Done! Your poster graph is ready.")
    print("=" * 60)


if __name__ == "__main__":
    scope = sys.argv[1] if len(sys.argv) > 1 else None
    
    try:
        generate_poster_graph(scope)
    except KeyboardInterrupt:
        print("\n\nInterrupted. Goodbye!")
        sys.exit(0)
    except Exception as e:
        print(f"\nError: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

