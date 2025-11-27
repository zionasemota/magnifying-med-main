"""
Generate success metrics visualization
Usage: python generate_metrics_graph.py [--metrics-file path/to/metrics.json]
"""

import sys
import json
from pathlib import Path
from visualization import BiasVisualizer
from metrics import MetricsTracker


def load_metrics_from_file(filepath: str) -> dict:
    """Load metrics from JSON file"""
    with open(filepath, 'r') as f:
        return json.load(f)


def main():
    """Generate success metrics graph"""
    print("=" * 60)
    print("Generating Success Metrics Graph")
    print("=" * 60)
    print()
    
    visualizer = BiasVisualizer(output_dir="outputs/visualizations")
    metrics_tracker = MetricsTracker()
    
    # Check for metrics file argument
    metrics_data = None
    if len(sys.argv) > 1 and sys.argv[1].startswith('--'):
        if sys.argv[1] == '--metrics-file' and len(sys.argv) > 2:
            metrics_file = sys.argv[2]
            try:
                metrics_dict = load_metrics_from_file(metrics_file)
                # Convert to expected format
                metrics_data = {
                    "metrics": metrics_dict.get("metrics", {}),
                    "total_sessions": metrics_dict.get("total_sessions", 0)
                }
                print(f"Loaded metrics from: {metrics_file}")
            except Exception as e:
                print(f"Error loading metrics file: {e}")
                print("Using default sample metrics...")
        else:
            print(f"Unknown option: {sys.argv[1]}")
            print("Usage: python generate_metrics_graph.py [--metrics-file path/to/metrics.json]")
            return
    
    # If no metrics file, try to get from tracker or use sample
    if not metrics_data:
        try:
            metrics_data = metrics_tracker.get_metrics_for_visualization()
            if metrics_data.get('total_sessions', 0) == 0:
                raise ValueError("No metrics history")
        except:
            print("No metrics history found. Using sample metrics for demonstration.")
            print("(To use real metrics, provide a metrics file or run sessions first)")
            print()
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
    
    # Generate visualization
    print("Generating success metrics graph...")
    output_path = visualizer.plot_success_metrics(metrics_data)
    
    print(f"✓ Success metrics graph saved to: {output_path}")
    print()
    print("Metrics Summary:")
    for key, metric in metrics_data['metrics'].items():
        status = "✓ MET" if metric.get('met', False) else "✗ NOT MET"
        if metric['unit'] == '%':
            value_str = f"{metric['value']*100:.1f}%"
            target_str = f"{metric['target']*100:.1f}%"
        else:
            value_str = f"{metric['value']:.1f}{metric['unit']}"
            target_str = f"{metric['target']:.1f}{metric['unit']}"
        print(f"  {metric['label']}: {value_str} (target: {target_str}) {status}")
    print()
    print("=" * 60)
    print("Done!")
    print("=" * 60)


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

