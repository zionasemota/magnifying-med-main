# Metrics Collection and Visualization Guide

This guide explains how to collect metrics from LLM conversations and generate graphs showing the 5 key metrics.

## Quick Start

The easiest way to collect metrics and view graphs:

```bash
python collect_and_view_metrics.py --sessions 5
```

This will:
1. Run 5 LLM sessions to collect metrics
2. Generate graphs for all 5 metrics
3. Automatically open the graphs

## The 5 Metrics Tracked

1. **% of model claims with verifiable citations to papers/datasets**
2. **% of checked claims that are false or uncited**
3. **Share of gaps that explicitly flag demographic or geographic under-representation when present**
4. **Median time from first query to first vetted gap with sources**
5. **% of sessions that reproduce identical outputs given same corpus and seed**

## Step-by-Step Usage

### Step 1: Collect Metrics

Run multiple LLM sessions to collect metrics:

```bash
python run_metrics_batch.py --sessions 5 --output batch_metrics.json
```

Options:
- `--sessions N`: Number of sessions to run per query set (default: 3)
- `--seed SEED`: Optional seed for reproducibility testing
- `--corpus CORPUS`: Corpus identifier for reproducibility tracking
- `--output FILE`: Output JSON file for metrics (default: batch_metrics.json)
- `--queries FILE`: Optional JSON file with custom queries

### Step 2: Generate Graphs

Generate graphs from collected metrics:

```bash
python generate_metrics_graphs.py --metrics-file batch_metrics.json
```

This creates two graphs:
- `all_metrics_graph.png` - Shows all 5 metrics with targets
- `metrics_summary_dashboard.png` - Summary dashboard

### Step 3: View Graphs

View the generated graphs:

```bash
python view_metrics_graphs.py
```

Options:
- `--list`: List all available graphs
- `--open-all`: Open all graphs
- `--graph FILE`: Open a specific graph file
- `--dir DIR`: Specify graph directory (default: outputs/visualizations)

## Complete Command Reference

### Collect Metrics Only

```bash
python run_metrics_batch.py --sessions 10 --seed 42 --corpus test --output my_metrics.json
```

### Generate Graphs Only

```bash
python generate_metrics_graphs.py --metrics-file my_metrics.json --output-dir outputs/visualizations
```

### View Graphs Only

```bash
# View all graphs
python view_metrics_graphs.py

# List available graphs
python view_metrics_graphs.py --list

# Open all graphs
python view_metrics_graphs.py --open-all

# Open specific graph
python view_metrics_graphs.py --graph all_metrics_graph.png
```

### All-in-One Command

```bash
python collect_and_view_metrics.py --sessions 5 --seed 42
```

## Understanding the Metrics

### Citation Verification Rate
Percentage of claims made by the LLM that include verifiable citations to papers or datasets. Target: ≥95%

### False/Uncited Claims Rate
Percentage of claims that are either false or lack citations. Target: ≤2%

### Demographic/Geographic Flagging Rate
Percentage of identified gaps that explicitly mention demographic or geographic under-representation. Target: ≥80%

### Median Time to First Vetted Gap
Median time (in seconds) from the first user query to the first gap identified with sources. Target: ≤90s

### Reproducibility Rate
Percentage of sessions with identical outputs when using the same corpus and seed. Target: ≥95%

## Output Files

After running the metrics collection:

- `batch_metrics.json` - Contains all session metrics in JSON format
- `outputs/visualizations/all_metrics_graph.png` - Comprehensive graph showing all 5 metrics
- `outputs/visualizations/metrics_summary_dashboard.png` - Summary dashboard

## Notes

- Metrics tracking is automatically enabled in `ConversationHandler` without changing LLM conversation behavior
- The system extracts claims, citations, and gaps from LLM responses automatically
- Reproducibility is calculated by comparing outputs from sessions with the same corpus and seed
- All metrics are calculated from actual conversation data

## Troubleshooting

**Error: Metrics file not found**
- Make sure you've run `run_metrics_batch.py` first
- Check that the `--output` file exists

**Error: No graphs found**
- Run `generate_metrics_graphs.py` to create graphs
- Check the `--output-dir` path

**Graphs don't open automatically**
- Use `view_metrics_graphs.py` to manually open graphs
- Check your system's default image viewer

