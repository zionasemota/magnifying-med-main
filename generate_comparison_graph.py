"""
Script to generate comparison graphs between LLM analysis and baseline
Usage: python generate_comparison_graph.py
"""

import json
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from visualization import BiasVisualizer
from analysis import InDepthAnalyzer
from conversation_handler import ConversationHandler


def main():
    """Generate comparison graphs"""
    print("=" * 60)
    print("MagnifyingMed - Graph Generation Tool")
    print("=" * 60)
    print()
    
    # Initialize components
    handler = ConversationHandler()
    visualizer = BiasVisualizer()
    analyzer = InDepthAnalyzer(handler.llm_client)
    
    # Check if we have analysis results
    if not handler.analysis_results:
        print("No analysis results found. Please run an analysis first.")
        print("\nExample usage:")
        print("1. Run the main CLI: python -m magnifying_med")
        print("2. Ask about a medical field (e.g., 'dermatology')")
        print("3. Then run this script to generate graphs")
        return
    
    scope = handler.context_manager.get_scope()
    print(f"Generating comparison graphs for: {scope}")
    print()
    
    # Generate baseline comparison
    print("Generating baseline comparison...")
    baseline_comparison = analyzer.generate_baseline_comparison(
        handler.analysis_results, baseline_type="standard"
    )
    
    print(f"LLM Score: {baseline_comparison['llm_score']:.3f}")
    print(f"Baseline Score: {baseline_comparison['baseline_score']:.3f}")
    print(f"Difference: {baseline_comparison['difference']:+.3f}")
    print()
    
    # Generate visualizations
    print("Generating visualizations...")
    
    # 1. Score comparison
    llm_breakdown = handler.analysis_results['score_results'].get('breakdown', {})
    baseline_breakdown = baseline_comparison.get('baseline_breakdown', {})
    
    score_path = visualizer.plot_score_comparison(
        llm_breakdown, baseline_breakdown, scope
    )
    print(f"✓ Score comparison saved to: {score_path}")
    
    # 2. Driver analysis
    driver_path = visualizer.plot_driver_analysis(
        handler.analysis_results['score_results'], scope
    )
    print(f"✓ Driver analysis saved to: {driver_path}")
    
    # 3. Dataset composition
    if 'dataset_analysis' in handler.analysis_results:
        dataset_path = visualizer.plot_dataset_composition(
            handler.analysis_results['dataset_analysis'], scope
        )
        print(f"✓ Dataset composition saved to: {dataset_path}")
    
    # 4. Comprehensive report
    baseline_results = {
        'score_results': {
            'breakdown': baseline_breakdown
        }
    }
    report_paths = visualizer.generate_comparison_report(
        handler.analysis_results, baseline_results, scope
    )
    print(f"✓ Comprehensive report generated with {len(report_paths)} visualizations")
    
    print()
    print("=" * 60)
    print("Graph generation complete!")
    print("=" * 60)
    print()
    print("Generated files:")
    for viz_type, path in report_paths.items():
        print(f"  - {viz_type}: {path}")
    print()
    print("Baseline Comparison Summary:")
    print(f"  {baseline_comparison['interpretation']}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nInterrupted. Goodbye!")
        sys.exit(0)
    except Exception as e:
        print(f"\nError: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

