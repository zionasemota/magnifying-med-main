# Visualization and Analysis Guide

This guide explains how to use the new visualization and analysis features in MagnifyingMed.

## Features Added

1. **Comparison Graphs**: Generate graphs comparing LLM analysis to baseline
2. **In-Depth Case Studies**: Detailed analysis of specific bias cases
3. **Literature Contextualization**: Contextualize results within existing research
4. **Multiple Visualization Types**: Score comparisons, driver analysis, dataset composition, and more

## Usage

### 1. Generate Comparison Graphs

#### Via CLI Conversation:
After running an analysis, you can ask:
- "Generate a comparison graph"
- "Show me a graph comparing to baseline"
- "Create a visualization"
- "Plot the score comparison"

#### Via Script:
```bash
python generate_comparison_graph.py
```

This will generate:
- Score comparison (LLM vs Baseline)
- Driver analysis (pie chart + bar chart)
- Dataset composition analysis
- Comprehensive report with all visualizations

### 2. Request In-Depth Case Studies

In the CLI, ask:
- "Provide a case study analysis"
- "Give me an in-depth analysis"
- "Analyze the most concerning case"

This will generate a detailed case study focusing on the most critical bias component.

### 3. Literature Contextualization

In the CLI, ask:
- "Contextualize this in the literature"
- "Compare to existing research"
- "How does this relate to published papers?"

This will provide context on how your results relate to existing research.

## Baseline Comparison

The system supports three baseline types:

1. **Standard Baseline** (default): Represents typical bias levels in medical AI
2. **Conservative Baseline**: Assumes higher bias levels
3. **Optimistic Baseline**: Assumes lower bias levels

You can specify the baseline type when requesting comparisons:
- "Compare to conservative baseline"
- "Compare to optimistic baseline"

## Visualization Types

### Score Comparison
Bar chart comparing each bias component (race labels, dark skin representation, etc.) between LLM analysis and baseline.

### Driver Analysis
- Pie chart showing distribution of bias components
- Horizontal bar chart showing top bias drivers

### Dataset Composition
Four-panel visualization showing:
- Race label availability
- Dark skin representation vs target
- Minority representation vs target
- Geographic diversity

### Overall Score Comparison
Comparison of overall bias scores across multiple medical fields.

## Output Location

All visualizations are saved to: `outputs/visualizations/`

Files are named with the scope/medical field and visualization type.

## Example Workflow

1. Start the CLI: `python -m magnifying_med`
2. Ask about a field: "dermatology"
3. Wait for analysis to complete
4. Request visualization: "generate a comparison graph"
5. Request case study: "provide a case study analysis"
6. Request literature context: "contextualize in literature"

## Dependencies

Make sure you have installed:
```bash
pip install matplotlib numpy
```

Or install all requirements:
```bash
pip install -r requirements.txt
```

## Notes

- Visualizations are saved as PNG files with 300 DPI resolution
- The baseline comparison uses the same scoring weights as the LLM analysis
- Case studies focus on the highest-scoring bias component by default
- Literature contextualization uses papers found during the research phase

