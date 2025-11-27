"""
Batch runner to execute multiple LLM sessions and collect metrics
Usage: python run_metrics_batch.py [--sessions N] [--seed SEED] [--corpus CORPUS]
"""

import sys
import json
import time
import argparse
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime

# Handle imports
try:
    from conversation_handler import ConversationHandler
    from metrics import MetricsTracker
except ImportError:
    from .conversation_handler import ConversationHandler
    from .metrics import MetricsTracker


class BatchRunner:
    """Run multiple LLM sessions and collect metrics"""
    
    def __init__(self, seed: Optional[int] = None, corpus: Optional[str] = None):
        """
        Initialize batch runner
        
        Args:
            seed: Optional seed for reproducibility
            corpus: Optional corpus identifier for reproducibility tracking
        """
        self.seed = seed
        self.corpus = corpus or "default"
        self.session_outputs = []  # Track outputs for reproducibility
        self.all_sessions_metrics = []
    
    def run_session(self, queries: List[str], session_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Run a single session with given queries
        
        Args:
            queries: List of user queries to run
            session_id: Optional session ID
            
        Returns:
            Dictionary with session results and metrics
        """
        if session_id is None:
            session_id = f"batch_{int(time.time())}_{len(self.all_sessions_metrics)}"
        
        print(f"\n{'='*60}")
        print(f"Running session: {session_id}")
        print(f"{'='*60}")
        
        # Create handler (metrics tracking enabled by default)
        handler = ConversationHandler(enable_metrics_tracking=True)
        
        # Store session outputs for reproducibility
        session_outputs = []
        
        # Run queries
        for i, query in enumerate(queries, 1):
            print(f"\nQuery {i}/{len(queries)}: {query[:60]}...")
            response = handler.handle_message(query)
            session_outputs.append({
                "query": query,
                "response": response[:500] if len(response) > 500 else response  # Store truncated for comparison
            })
            print(f"Response received ({len(response)} chars)")
        
        # End session and get metrics
        session_metrics = handler.end_session()
        session_metrics["session_id"] = session_id
        session_metrics["corpus"] = self.corpus
        session_metrics["seed"] = self.seed
        session_metrics["outputs"] = session_outputs  # Store for reproducibility
        
        # Store for later analysis
        self.all_sessions_metrics.append(session_metrics)
        self.session_outputs.append({
            "session_id": session_id,
            "outputs": session_outputs,
            "corpus": self.corpus,
            "seed": self.seed
        })
        
        print(f"\n✓ Session completed: {session_id}")
        print(f"  Claims recorded: {session_metrics.get('total_claims', 0)}")
        print(f"  Gaps identified: {session_metrics.get('total_gaps', 0)}")
        
        return session_metrics
    
    def run_multiple_sessions(self, queries_list: List[List[str]], num_sessions: int) -> List[Dict[str, Any]]:
        """
        Run multiple sessions (same queries for reproducibility)
        
        Args:
            queries_list: List of query sets (each will be run as a session)
            num_sessions: Number of times to run each query set
            
        Returns:
            List of all session metrics
        """
        all_metrics = []
        
        for session_num in range(num_sessions):
            for query_set_idx, queries in enumerate(queries_list):
                session_id = f"session_{session_num}_{query_set_idx}"
                metrics = self.run_session(queries, session_id)
                all_metrics.append(metrics)
                
                # Small delay between sessions
                time.sleep(1)
        
        return all_metrics
    
    def calculate_reproducibility(self) -> float:
        """Calculate reproducibility rate (identical outputs with same corpus/seed)"""
        if len(self.session_outputs) < 2:
            return 0.0
        
        # Group by corpus and seed
        groups = {}
        for session in self.session_outputs:
            key = (session["corpus"], session["seed"])
            if key not in groups:
                groups[key] = []
            groups[key].append(session)
        
        # Check reproducibility within each group
        reproducible_sessions = 0
        total_comparisons = 0
        
        for key, sessions in groups.items():
            if len(sessions) < 2:
                continue
            
            # Compare outputs pairwise
            for i in range(len(sessions)):
                for j in range(i + 1, len(sessions)):
                    total_comparisons += 1
                    if self._outputs_identical(sessions[i]["outputs"], sessions[j]["outputs"]):
                        reproducible_sessions += 1
        
        if total_comparisons == 0:
            return 0.0
        
        return reproducible_sessions / total_comparisons
    
    def _outputs_identical(self, outputs1: List[Dict], outputs2: List[Dict]) -> bool:
        """Check if two output sequences are identical"""
        if len(outputs1) != len(outputs2):
            return False
        
        for o1, o2 in zip(outputs1, outputs2):
            if o1["query"] != o2["query"]:
                return False
            # Compare responses (using truncated versions stored)
            if o1["response"] != o2["response"]:
                return False
        
        return True
    
    def save_metrics(self, output_file: str):
        """Save all collected metrics to JSON file"""
        output = {
            "timestamp": datetime.now().isoformat(),
            "corpus": self.corpus,
            "seed": self.seed,
            "sessions": self.all_sessions_metrics,
            "reproducibility_rate": self.calculate_reproducibility(),
            "total_sessions": len(self.all_sessions_metrics)
        }
        
        with open(output_file, 'w') as f:
            json.dump(output, f, indent=2)
        
        print(f"\n✓ Metrics saved to: {output_file}")


def get_default_queries() -> List[List[str]]:
    """Get default query sets for batch runs"""
    return [
        ["analyze bias in dermatology", "what are the gaps?"],
        ["analyze bias in cardiology", "show me mitigation methods"],
        ["analyze bias in radiology"],
    ]


def main():
    parser = argparse.ArgumentParser(description="Run batch LLM sessions to collect metrics")
    parser.add_argument("--sessions", type=int, default=3, help="Number of sessions to run per query set")
    parser.add_argument("--seed", type=int, default=None, help="Seed for reproducibility")
    parser.add_argument("--corpus", type=str, default="default", help="Corpus identifier")
    parser.add_argument("--output", type=str, default="batch_metrics.json", help="Output file for metrics")
    parser.add_argument("--queries", type=str, default=None, help="JSON file with queries (list of query lists)")
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("Batch Metrics Collection Runner")
    print("=" * 60)
    print(f"Sessions per query set: {args.sessions}")
    print(f"Corpus: {args.corpus}")
    print(f"Seed: {args.seed or 'None'}")
    print()
    
    # Load queries
    if args.queries:
        with open(args.queries, 'r') as f:
            queries_list = json.load(f)
    else:
        queries_list = get_default_queries()
    
    print(f"Query sets to run: {len(queries_list)}")
    print()
    
    # Create runner
    runner = BatchRunner(seed=args.seed, corpus=args.corpus)
    
    # Run sessions
    try:
        metrics = runner.run_multiple_sessions(queries_list, args.sessions)
        
        # Save metrics
        runner.save_metrics(args.output)
        
        # Print summary
        print("\n" + "=" * 60)
        print("Batch Run Summary")
        print("=" * 60)
        print(f"Total sessions: {len(metrics)}")
        print(f"Reproducibility rate: {runner.calculate_reproducibility():.2%}")
        print(f"Metrics saved to: {args.output}")
        print("\nTo generate graphs, run:")
        print(f"  python generate_metrics_graphs.py --metrics-file {args.output}")
        print("=" * 60)
        
    except KeyboardInterrupt:
        print("\n\nInterrupted. Saving partial metrics...")
        runner.save_metrics(args.output)
        sys.exit(0)
    except Exception as e:
        print(f"\nError: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

