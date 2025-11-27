# Success Metrics Guide

## Overview

MagnifyingMed now tracks and visualizes success metrics to evaluate LLM performance. These metrics compare actual performance against target thresholds.

## Success Metrics

1. **Citation Verification Rate** (Target: ≥95%)
   - Percentage of model claims with verifiable citations to papers/datasets

2. **False/Uncited Claims Rate** (Target: ≤2%)
   - Percentage of checked claims that are false or uncited

3. **Demographic Flagging Rate** (Target: ≥80%)
   - Share of gaps that explicitly flag demographic or geographic under-representation when present

4. **Time to First Vetted Gap** (Target: ≤90s)
   - Median time from first query to first vetted gap with sources

5. **Reproducibility Rate** (Target: ≥95%)
   - Percentage of sessions that reproduce identical outputs given same corpus and seed

## Generating Graphs

### 1. Combined Poster Graph (Bias + Metrics)

Generate a poster-quality graph with both bias comparison and success metrics:

```bash
python generate_poster_graph.py [medical_field]
```

This creates a two-panel visualization:
- Top: Bias score comparison (LLM vs Baseline)
- Bottom: Success metrics (Actual vs Target)

### 2. Success Metrics Only

Generate a standalone success metrics graph:

```bash
python generate_metrics_graph.py
```

Or with custom metrics file:

```bash
python generate_metrics_graph.py --metrics-file path/to/metrics.json
```

## Metrics File Format

Create a JSON file with your metrics data:

```json
{
  "metrics": {
    "citation_verification_rate": {
      "value": 0.96,
      "target": 0.95,
      "met": true,
      "label": "Claims with Verifiable Citations",
      "unit": "%"
    },
    "false_uncited_claims_rate": {
      "value": 0.015,
      "target": 0.02,
      "met": true,
      "label": "False/Uncited Claims",
      "unit": "%"
    },
    "demographic_flagging_rate": {
      "value": 0.85,
      "target": 0.80,
      "met": true,
      "label": "Gaps Flagging Demographics",
      "unit": "%"
    },
    "time_to_first_gap": {
      "value": 75.0,
      "target": 90.0,
      "met": true,
      "label": "Time to First Vetted Gap",
      "unit": "s"
    },
    "reproducibility_rate": {
      "value": 0.96,
      "target": 0.95,
      "met": true,
      "label": "Reproducibility Rate",
      "unit": "%"
    }
  },
  "total_sessions": 10
}
```

## Using MetricsTracker

For programmatic tracking:

```python
from metrics import MetricsTracker

tracker = MetricsTracker()

# Start a session
tracker.start_session("session_1")

# Record claims
tracker.record_claim("Claim text", has_citation=True, is_verified=True)

# Record gaps
tracker.record_gap("Gap description", flags_demographic=True, 
                  flags_geographic=True, has_sources=True)

# Record response time
tracker.record_response_time(75.0)

# End session and get metrics
session_metrics = tracker.end_session()

# Get aggregate metrics
aggregate = tracker.calculate_aggregate_metrics()
```

## Visualization Features

### Success Metrics Graph
- Shows all 5 metrics side-by-side
- Compares actual vs target values
- Color-coded: Green = target met, Orange/Red = not met
- Status indicators on each metric

### Combined Graph
- Two-panel layout
- Top: Bias score comparison
- Bottom: Success metrics summary
- 600 DPI resolution for posters

## Output Files

- Success metrics only: `outputs/visualizations/success_metrics.png`
- Combined poster: `outputs/visualizations/poster/combined_comparison_[field].png`

## Example Workflow

1. **Track metrics during sessions:**
   ```python
   tracker = MetricsTracker()
   tracker.start_session()
   # ... perform analysis ...
   metrics = tracker.end_session()
   ```

2. **Generate metrics graph:**
   ```bash
   python generate_metrics_graph.py
   ```

3. **Generate combined poster:**
   ```bash
   python generate_poster_graph.py dermatology
   ```

## Notes

- If no metrics are available, the poster graph will use sample/demo metrics
- Metrics are automatically calculated from session history
- You can provide custom metrics via JSON file
- All graphs are saved at 300-600 DPI for high-quality printing

