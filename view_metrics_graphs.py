"""
View/load generated metrics graphs
Usage: python view_metrics_graphs.py [--dir outputs/visualizations]
"""

import sys
import argparse
import subprocess
import platform
from pathlib import Path


def open_graph(graph_path: str):
    """Open a graph file using the system's default viewer"""
    system = platform.system()
    
    try:
        if system == "Darwin":  # macOS
            subprocess.run(["open", graph_path], check=True)
        elif system == "Windows":
            subprocess.run(["start", graph_path], shell=True, check=True)
        elif system == "Linux":
            subprocess.run(["xdg-open", graph_path], check=True)
        else:
            print(f"Graph saved to: {graph_path}")
            print("Please open it manually with your preferred image viewer.")
    except Exception as e:
        print(f"Could not open graph automatically: {e}")
        print(f"Graph saved to: {graph_path}")
        print("Please open it manually with your preferred image viewer.")


def list_graphs(directory: Path):
    """List all available graph files"""
    graph_files = list(directory.glob("*.png")) + list(directory.glob("*.jpg")) + list(directory.glob("*.pdf"))
    
    if not graph_files:
        print(f"No graph files found in {directory}")
        return []
    
    # Sort by modification time (newest first)
    graph_files.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    
    return graph_files


def main():
    parser = argparse.ArgumentParser(description="View generated metrics graphs")
    parser.add_argument("--dir", type=str, default="outputs/visualizations",
                       help="Directory containing graphs")
    parser.add_argument("--list", action="store_true",
                       help="List all available graphs")
    parser.add_argument("--open-all", action="store_true",
                       help="Open all graphs")
    parser.add_argument("--graph", type=str, default=None,
                       help="Specific graph file to open")
    
    args = parser.parse_args()
    
    graph_dir = Path(args.dir)
    
    if not graph_dir.exists():
        print(f"Error: Directory not found: {graph_dir}")
        print("\nTo generate graphs, first run:")
        print("  python run_metrics_batch.py --sessions 5")
        print("  python generate_metrics_graphs.py")
        sys.exit(1)
    
    # List graphs
    graph_files = list_graphs(graph_dir)
    
    if not graph_files:
        print(f"No graphs found in {graph_dir}")
        print("\nTo generate graphs, first run:")
        print("  python run_metrics_batch.py --sessions 5")
        print("  python generate_metrics_graphs.py")
        sys.exit(1)
    
    # Handle list option
    if args.list:
        print(f"\nAvailable graphs in {graph_dir}:")
        print("=" * 60)
        for i, graph_file in enumerate(graph_files, 1):
            size = graph_file.stat().st_size / 1024  # KB
            print(f"{i}. {graph_file.name} ({size:.1f} KB)")
        print("=" * 60)
        return
    
    # Handle open all
    if args.open_all:
        print(f"\nOpening all {len(graph_files)} graphs...")
        for graph_file in graph_files:
            print(f"  Opening: {graph_file.name}")
            open_graph(str(graph_file))
        print("\n✓ All graphs opened!")
        return
    
    # Handle specific graph
    if args.graph:
        graph_path = graph_dir / args.graph
        if not graph_path.exists():
            print(f"Error: Graph not found: {graph_path}")
            sys.exit(1)
        open_graph(str(graph_path))
        return
    
    # Default: open the main metrics graphs
    print("=" * 60)
    print("Opening Metrics Graphs")
    print("=" * 60)
    print()
    
    # Find key graphs
    key_graphs = {
        "all_metrics_graph.png": "All 5 Metrics Graph",
        "metrics_summary_dashboard.png": "Summary Dashboard",
        "success_metrics.png": "Success Metrics (legacy)"
    }
    
    opened = False
    for filename, description in key_graphs.items():
        graph_path = graph_dir / filename
        if graph_path.exists():
            print(f"Opening: {description} ({filename})")
            open_graph(str(graph_path))
            opened = True
    
    if not opened:
        # Open the most recent graph
        if graph_files:
            print(f"Opening most recent graph: {graph_files[0].name}")
            open_graph(str(graph_files[0]))
    
    print("\n✓ Graphs opened!")
    print(f"\nAll graphs are in: {graph_dir.absolute()}")
    print("\nTo list all graphs, run:")
    print("  python view_metrics_graphs.py --list")
    print("\nTo open all graphs, run:")
    print("  python view_metrics_graphs.py --open-all")
    print("=" * 60)


if __name__ == "__main__":
    main()

