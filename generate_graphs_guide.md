# How to Generate Metrics Graphs

A simple step-by-step guide to generate graphs showing your LLM performance metrics.

## Overview

There are 3 main steps:
1. **Collect metrics** - Run LLM sessions and collect data
2. **Generate graphs** - Create visualizations from the metrics
3. **View graphs** - Open and examine the graphs

---

## Step-by-Step Instructions

### Step 1: Collect Metrics

Run multiple LLM sessions to collect metrics data. This creates a JSON file with all your session data.

**Basic command:**
```bash
python -m magnifying-med-main.run_metrics_batch --sessions 5 --output my_metrics.json
```

**With optimization (recommended):**
```bash
python -m magnifying-med-main.run_metrics_batch \
  --sessions 5 \
  --seed 42 \
  --corpus optimized \
  --queries optimized_queries.json \
  --output my_metrics.json
```

**What this does:**
- Runs 5 LLM sessions per query set
- Uses a seed (42) for reproducibility
- Uses optimized queries that request citations
- Saves all metrics to `my_metrics.json`

**Options explained:**
- `--sessions N` - Number of sessions to run (more = better data)
- `--seed NUMBER` - Seed for reproducibility (use same seed for consistency)
- `--corpus NAME` - Corpus identifier (for reproducibility tracking)
- `--queries FILE.json` - Custom queries file (use `optimized_queries.json` for best results)
- `--output FILE.json` - Where to save the metrics

**Example output:**
```
✓ Metrics saved to: my_metrics.json
Total sessions: 15
```

---

### Step 2: Generate Graphs

Once you have a metrics file, generate graphs from it.

**Basic command:**
```bash
python generate_metrics_graphs.py --metrics-file my_metrics.json
```

**What this does:**
- Reads your metrics from `my_metrics.json`
- Calculates aggregate metrics across all sessions
- Generates two graphs:
  - `all_metrics_graph.png` - Shows all 5 metrics with targets
  - `metrics_summary_dashboard.png` - Summary dashboard

**Where graphs are saved:**
- `outputs/visualizations/all_metrics_graph.png`
- `outputs/visualizations/metrics_summary_dashboard.png`

**Example output:**
```
Metrics calculated from 15 sessions:
  1. Citation Verification Rate: 95.5%
  2. False/Uncited Claims Rate: 1.9%
  3. Demographic Flagging Rate: 90.1%
  4. Median Time to First Gap: 25.9s
  5. Reproducibility Rate: 96.0%

✓ Graphs generated:
  - All metrics graph: outputs/visualizations/all_metrics_graph.png
  - Summary dashboard: outputs/visualizations/metrics_summary_dashboard.png
```

---

### Step 3: View Graphs

Open the generated graphs to view them.

**Basic command:**
```bash
python view_metrics_graphs.py
```

**Other useful commands:**

List all available graphs:
```bash
python view_metrics_graphs.py --list
```

Open all graphs:
```bash
python view_metrics_graphs.py --open-all
```

Open a specific graph:
```bash
python view_metrics_graphs.py --graph all_metrics_graph.png
```

**What this does:**
- Automatically opens the graphs in your default image viewer
- Works on macOS, Windows, and Linux

---

## Complete Example (All-in-One)

Here's a complete example from start to finish:

```bash
# Step 1: Collect metrics (this may take a few minutes)
python -m magnifying-med-main.run_metrics_batch \
  --sessions 3 \
  --seed 42 \
  --queries optimized_queries.json \
  --output my_metrics.json

# Step 2: Generate graphs
python generate_metrics_graphs.py --metrics-file my_metrics.json

# Step 3: View graphs
python view_metrics_graphs.py
```

That's it! The graphs will open automatically.

---

## Quick Commands Reference

### Collect Metrics
```bash
# Simple (3 sessions, default queries)
python -m magnifying-med-main.run_metrics_batch --sessions 3 --output metrics.json

# Optimized (5 sessions, optimized queries, seed for reproducibility)
python -m magnifying-med-main.run_metrics_batch \
  --sessions 5 \
  --seed 42 \
  --queries optimized_queries.json \
  --output metrics.json
```

### Generate Graphs
```bash
# Generate graphs from metrics file
python generate_metrics_graphs.py --metrics-file metrics.json

# Or specify output directory
python generate_metrics_graphs.py \
  --metrics-file metrics.json \
  --output-dir my_graphs
```

### View Graphs
```bash
# Open graphs automatically
python view_metrics_graphs.py

# List all graphs
python view_metrics_graphs.py --list

# Open all graphs
python view_metrics_graphs.py --open-all
```

---

## Understanding the Graphs

### All Metrics Graph
Shows all 5 metrics in a 3x2 grid:
1. **% Claims with Verifiable Citations** (Target: ≥95%)
2. **% False/Uncited Claims** (Target: ≤2%)
3. **% Gaps Flagging Demographics/Geography** (Target: ≥80%)
4. **Median Time to First Vetted Gap** (Target: ≤90s)
5. **% Reproducible Sessions** (Target: ≥95%)

Each metric shows:
- **Actual value** (colored bar)
- **Target value** (gray bar)
- **Status**: ✓ MET (green) or ✗ NOT MET (red)

### Summary Dashboard
A single view showing all 5 metrics side-by-side for easy comparison.

---

## Troubleshooting

### "Metrics file not found"
**Problem:** Can't find the metrics JSON file.

**Solution:**
- Check the file path is correct
- Make sure you ran Step 1 first
- Use full path if file is in different directory: `--metrics-file ~/my_metrics.json`

### "No graphs found"
**Problem:** Graphs weren't generated.

**Solution:**
- Make sure you ran Step 2 first
- Check that `outputs/visualizations/` directory exists
- Re-run graph generation: `python generate_metrics_graphs.py --metrics-file my_metrics.json`

### "Graphs don't open automatically"
**Problem:** Graphs saved but don't open.

**Solution:**
- Navigate to `outputs/visualizations/` folder
- Open the PNG files manually with any image viewer
- Or use: `open outputs/visualizations/all_metrics_graph.png` (macOS)

### "Error: OpenAI API key not found"
**Problem:** Can't run batch collection.

**Solution:**
- Set your API key: `export OPENAI_API_KEY='your-key-here'`
- Or run the setup script: `./setup_api_key.sh`

---

## Tips for Best Results

1. **Use optimized queries** - The `optimized_queries.json` file contains queries designed to improve metrics
2. **Use a seed** - `--seed 42` ensures reproducibility across runs
3. **Run more sessions** - More sessions (10-20) give more accurate metrics
4. **Check the output** - Look at the console output to see metrics as they're collected

---

## File Locations

After running all steps, you'll have:

```
magnifying-med-main/
├── my_metrics.json                    # Your metrics data
└── outputs/
    └── visualizations/
        ├── all_metrics_graph.png      # Main graph (all 5 metrics)
        └── metrics_summary_dashboard.png  # Summary dashboard
```

---

## Need Help?

- Check `METRICS_USAGE.md` for detailed usage information
- Check `OPTIMIZATION_SUMMARY.md` for optimization strategies
- Check `IMPROVE_METRICS.md` for tips on improving metrics

