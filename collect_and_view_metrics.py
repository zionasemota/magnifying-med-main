#!/usr/bin/env python3
"""
End-to-end script to collect metrics and generate/view graphs
Usage: python collect_and_view_metrics.py [--sessions N]
"""

import sys
import subprocess
import argparse
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(
        description="Collect LLM metrics and generate/view graphs",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run 5 sessions and view graphs
  python collect_and_view_metrics.py --sessions 5
  
  # Run 10 sessions but don't auto-open graphs
  python collect_and_view_metrics.py --sessions 10 --no-open
        """
    )
    parser.add_argument("--sessions", type=int, default=3,
                       help="Number of sessions to run per query set (default: 3)")
    parser.add_argument("--seed", type=int, default=None,
                       help="Seed for reproducibility")
    parser.add_argument("--corpus", type=str, default="default",
                       help="Corpus identifier")
    parser.add_argument("--no-open", action="store_true",
                       help="Don't automatically open graphs")
    parser.add_argument("--metrics-file", type=str, default="batch_metrics.json",
                       help="Output file for metrics (default: batch_metrics.json)")
    
    args = parser.parse_args()
    
    print("=" * 70)
    print("MagnifyingMed: Metrics Collection and Visualization")
    print("=" * 70)
    print()
    
    # Step 1: Run batch collection
    print("Step 1: Collecting metrics from LLM sessions...")
    print("-" * 70)
    try:
        batch_cmd = [
            sys.executable, "run_metrics_batch.py",
            "--sessions", str(args.sessions),
            "--output", args.metrics_file
        ]
        if args.seed:
            batch_cmd.extend(["--seed", str(args.seed)])
        if args.corpus:
            batch_cmd.extend(["--corpus", args.corpus])
        
        result = subprocess.run(batch_cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"\nError running batch collection: {e}")
        sys.exit(1)
    except FileNotFoundError:
        print(f"\nError: Could not find run_metrics_batch.py")
        print("Make sure you're in the project root directory.")
        sys.exit(1)
    
    # Step 2: Generate graphs
    print("\nStep 2: Generating graphs...")
    print("-" * 70)
    try:
        graph_cmd = [
            sys.executable, "generate_metrics_graphs.py",
            "--metrics-file", args.metrics_file
        ]
        result = subprocess.run(graph_cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"\nError generating graphs: {e}")
        sys.exit(1)
    except FileNotFoundError:
        print(f"\nError: Could not find generate_metrics_graphs.py")
        sys.exit(1)
    
    # Step 3: View graphs
    if not args.no_open:
        print("\nStep 3: Opening graphs...")
        print("-" * 70)
        try:
            view_cmd = [sys.executable, "view_metrics_graphs.py"]
            subprocess.run(view_cmd, check=False)  # Don't fail if can't open
        except FileNotFoundError:
            print("Could not open graphs automatically.")
            print("Graphs are saved in: outputs/visualizations/")
    
    print("\n" + "=" * 70)
    print("✓ Complete! Metrics collected and graphs generated.")
    print("=" * 70)
    print(f"\nMetrics file: {args.metrics_file}")
    print("Graphs directory: outputs/visualizations/")
    print("\nTo view graphs manually, run:")
    print("  python view_metrics_graphs.py")
    print("\nTo list all graphs:")
    print("  python view_metrics_graphs.py --list")
    print("=" * 70)


if __name__ == "__main__":
    main()

