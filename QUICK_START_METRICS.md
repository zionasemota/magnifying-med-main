# Quick Start: Generate Poster Graph with Success Metrics

## Command for Poster Graph

**Generate poster-quality graph with bias comparison AND success metrics:**

```bash
python generate_poster_graph.py [medical_field]
```

**Examples:**
```bash
# If you already ran analysis
python generate_poster_graph.py

# Or specify field directly
python generate_poster_graph.py dermatology
python generate_poster_graph.py cardiology
```

## What You Get

The script generates a **two-panel poster graph**:

1. **Top Panel**: Bias Score Comparison (LLM vs Baseline)
   - Shows all 6 bias components side-by-side
   - Color-coded bars with values

2. **Bottom Panel**: Success Metrics (Actual vs Target)
   - Citation Verification Rate (target: ≥95%)
   - False/Uncited Claims Rate (target: ≤2%)
   - Demographic Flagging Rate (target: ≥80%)
   - Time to First Vetted Gap (target: ≤90s)
   - Reproducibility Rate (target: ≥95%)

## Output

Saved to: `outputs/visualizations/poster/poster_combined_[field].png`

- **Resolution**: 600 DPI (suitable for printing)
- **Size**: 20x14 inches
- **Format**: PNG with white background

## Success Metrics

The graph automatically includes success metrics. If you have real metrics data:

1. **Use MetricsTracker** to track during sessions
2. **Or provide JSON file** with your metrics (see `example_metrics.json`)

If no metrics are available, the script uses sample metrics for demonstration.

## Standalone Metrics Graph

To generate just the success metrics graph:

```bash
python generate_metrics_graph.py
```

Or with custom metrics:

```bash
python generate_metrics_graph.py --metrics-file your_metrics.json
```

## Full Workflow

```bash
# 1. Run analysis (if needed)
python -m magnifying_med
# (Ask about your field, e.g., "dermatology")

# 2. Generate poster graph with metrics
python generate_poster_graph.py dermatology
```

That's it! Your poster-ready graph will be in `outputs/visualizations/poster/`

