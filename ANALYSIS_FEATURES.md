# Analysis and Visualization Features

## Overview

This document describes the new analysis and visualization features added to MagnifyingMed for in-depth analysis, literature contextualization, and baseline comparison graphs.

## New Modules

### 1. `visualization.py` - BiasVisualizer Class

Generates various types of visualizations comparing LLM analysis to baselines:

**Key Methods:**
- `plot_score_comparison()`: Bar chart comparing bias score components (LLM vs baseline)
- `plot_overall_score_comparison()`: Comparison across multiple medical fields
- `plot_driver_analysis()`: Pie chart and bar chart showing bias drivers
- `plot_trend_analysis()`: Line plot showing bias trends over time
- `plot_dataset_composition()`: Four-panel visualization of dataset issues
- `generate_comparison_report()`: Comprehensive report with multiple visualizations

**Features:**
- Professional styling with color schemes
- High-resolution output (300 DPI)
- Automatic file naming and organization
- Support for baseline comparisons

### 2. `analysis.py` - InDepthAnalyzer Class

Provides in-depth analysis and literature contextualization:

**Key Methods:**
- `analyze_case_study()`: Detailed analysis of specific bias cases
- `contextualize_in_literature()`: Contextualize results within existing research
- `identify_notable_cases()`: Identify top cases of interest
- `generate_baseline_comparison()`: Generate baseline scores for comparison

**Baseline Types:**
- `standard`: Typical bias levels in medical AI
- `conservative`: Higher bias assumptions
- `optimistic`: Lower bias assumptions

## Integration

### Conversation Handler Integration

The `ConversationHandler` now includes:
- `BiasVisualizer` instance for generating graphs
- `InDepthAnalyzer` instance for detailed analysis
- New methods:
  - `_generate_visualization()`: Handle visualization requests
  - `_provide_case_study()`: Provide in-depth case studies
  - `_provide_literature_contextualization()`: Literature context

### Usage in CLI

Users can now ask:
- "Generate a comparison graph" / "Show me a graph"
- "Compare to baseline"
- "Provide a case study analysis"
- "Contextualize in literature"

## Example Usage

### Programmatic Usage

```python
from conversation_handler import ConversationHandler
from visualization import BiasVisualizer
from analysis import InDepthAnalyzer

# Initialize
handler = ConversationHandler()

# Run analysis (via conversation or directly)
# ... perform analysis ...

# Generate baseline comparison
analyzer = InDepthAnalyzer(handler.llm_client)
baseline_comparison = analyzer.generate_baseline_comparison(
    handler.analysis_results, baseline_type="standard"
)

# Generate visualizations
visualizer = BiasVisualizer()
llm_breakdown = handler.analysis_results['score_results']['breakdown']
baseline_breakdown = baseline_comparison['baseline_breakdown']

# Score comparison graph
path = visualizer.plot_score_comparison(
    llm_breakdown, baseline_breakdown, scope="dermatology"
)
print(f"Graph saved to: {path}")

# Case study
case_study = analyzer.analyze_case_study(handler.analysis_results)
print(case_study['analysis_text'])

# Literature contextualization
context = analyzer.contextualize_in_literature(handler.analysis_results)
print(context['contextualization_text'])
```

### CLI Usage

1. Start the CLI: `python -m magnifying_med`
2. Ask about a field: "dermatology"
3. Request visualization: "generate a comparison graph"
4. Request case study: "provide a case study analysis"
5. Request literature context: "contextualize in literature"

## Output Files

All visualizations are saved to: `outputs/visualizations/`

File naming convention:
- `score_comparison_{scope}.png`
- `driver_analysis_{scope}.png`
- `dataset_composition_{scope}.png`
- `overall_score_comparison.png`
- `trend_analysis.png`

## Dependencies

New dependencies added:
- `matplotlib>=3.7.0`: For plotting and visualization
- `numpy>=1.24.0`: For numerical operations

Install with:
```bash
pip install -r requirements.txt
```

## Technical Details

### Baseline Calculation

Baselines use the same scoring weights as LLM analysis:
- Race label availability: 15%
- Dark skin representation: 25%
- Subgroup metrics: 20%
- Geographic concentration: 15%
- Fairness method coverage: 15%
- External validation: 10%

### Case Study Focus

Case studies automatically focus on the highest-scoring bias component, but can be customized to focus on specific aspects.

### Literature Contextualization

Uses papers found during the research phase (from PubMed, OpenAlex, arXiv) to provide context and comparisons.

## Future Enhancements

Potential additions:
- Interactive visualizations (plotly)
- Export to PDF reports
- Historical trend analysis with time-series data
- Multi-field comparison dashboards
- Custom baseline definitions

