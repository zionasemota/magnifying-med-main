"""
Prompt templates for different analysis stages
"""

DATASET_COMPOSITION_PROMPT = """You are an equity-focused biomedical analyst. Output valid JSON only.

IMPORTANT: Real research papers will be provided below. Analyze those actual papers and extract dataset information from them. Base your analysis ONLY on the papers provided, not on general knowledge.

Analyze datasets for {scope} from research published in the past {years} years. Extract information about race/ethnicity labels, skin-tone/Fitzpatrick distribution (if applicable to the medical field), geography/sites, and missing fields from the provided papers.

For dermatology/skin conditions: Include Fitzpatrick scale distribution.
For other fields (cardiology, radiology, etc.): Focus on race/ethnicity labels and demographic composition.

Return JSON in this format:
{{
  "datasets": [
    {{
      "name": "dataset name",
      "race_labels": true/false,
      "ethnicity_labels": true/false,
      "skin_tone_labels": true/false,
      "fitzpatrick_distribution": {{"I": 0.1, "II": 0.2, "III": 0.3, "IV": 0.2, "V": 0.1, "VI": 0.1}},
      "racial_composition": {{"White": 0.7, "Black": 0.1, "Hispanic": 0.1, "Asian": 0.1}},
      "geography": ["US", "Europe"],
      "sites": ["Hospital A", "Hospital B"],
      "total_samples": 1000,
      "dark_skin_proportion": 0.3,
      "underrepresented_groups": ["Black", "Hispanic"],
      "missing_fields": ["race", "geography"]
    }}
  ],
  "summary": {{
    "total_datasets": 10,
    "datasets_with_race_labels": 3,
    "datasets_with_ethnicity_labels": 2,
    "datasets_with_skin_tone": 2,
    "avg_dark_skin_proportion": 0.15,
    "avg_minority_representation": 0.12,
    "geographic_diversity": "low/medium/high"
  }}
}}"""

SUBGROUP_PERFORMANCE_PROMPT = """You are an equity-focused biomedical analyst. Output valid JSON only.

IMPORTANT: Real research papers will be provided below. Extract subgroup metrics from those actual papers. Base your analysis ONLY on the papers provided.

From the provided research papers about {scope}, extract subgroup metrics for different racial/ethnic groups or skin tones (if applicable). Reference specific papers by title when providing metrics.

For dermatology: Include light vs dark skin metrics (Fitzpatrick scale).
For other fields: Focus on racial/ethnic group performance metrics.

Return JSON in this format:
{{
  "studies": [
    {{
      "paper": "Paper title",
      "metric": "AUROC or Accuracy",
      "light_skin": 0.90,
      "dark_skin": 0.76,
      "gap": 0.14,
      "race_groups": {{"White": 0.90, "Black": 0.76, "Hispanic": 0.80, "Asian": 0.85}},
      "gender_groups": {{"Male": 0.88, "Female": 0.82}},
      "performance_gap": 0.14,
      "url": "paper URL if available"
    }}
  ],
  "no_subgroup_reporting": 12,
  "summary": {{
    "total_studies": 30,
    "studies_with_subgroup_metrics": 18,
    "studies_with_race_metrics": 15,
    "studies_with_skin_tone_metrics": 8,
    "avg_performance_gap": 0.12,
    "largest_gap": 0.25,
    "common_gaps": ["Black patients show 10-15% lower accuracy", "Hispanic patients underrepresented"]
  }}
}}"""

MITIGATION_VALIDATION_PROMPT = """You are an equity-focused biomedical analyst. Output valid JSON only.

IMPORTANT: Real research papers will be provided below. Analyze those actual papers for fairness methods and validation. Base your analysis ONLY on the papers provided.

Analyze the provided {scope} research papers from the past {years} years for fairness method application and external validation. Reference specific papers by title when listing methods.

Return JSON in this format:
{{
  "fairness_methods": {{
    "reweighting": 5,
    "tone_aware_augmentation": 3,
    "threshold_adjustment": 4,
    "subgroup_specific_calibration": 2,
    "data_augmentation": 3,
    "none": 20
  }},
  "validation": {{
    "single_site": 25,
    "multi_site": 3,
    "external_validation": 2,
    "geographic_diversity": "low",
    "validation_regions": ["US", "Europe"],
    "validation_populations": ["White majority", "Limited diversity"]
  }},
  "studies": [
    {{
      "paper": "Paper title",
      "fairness_methods": ["reweighting", "threshold_adjustment"],
      "validation_sites": ["US Hospital A", "US Hospital B"],
      "external_validation": false,
      "geographic_scope": "US only",
      "population_diversity": "low",
      "url": "paper URL if available"
    }}
  ],
  "summary": {{
    "total_studies": 30,
    "studies_with_fairness_methods": 5,
    "studies_with_external_validation": 2,
    "studies_with_multi_site_validation": 3,
    "coverage_percentage": 16.7,
    "geographic_concentration": "high"
  }}
}}"""

TREND_SYNTHESIZER_PROMPT = """You are an equity-focused biomedical analyst. Output valid JSON only.

Combine the following analysis results to compute UnderExploredBiasScore for {scope}.

Dataset Analysis:
{dataset_analysis}

Subgroup Performance Analysis:
{subgroup_analysis}

Mitigation & Validation Analysis:
{mitigation_analysis}

Compute the score using these weights:
{weights}

Threshold for flagging: {threshold}

Return JSON in this format:
{{
  "topic": "{scope}",
  "score": 0.45,
  "threshold": {threshold},
  "flagged": true,
  "drivers": [
    "missing race labels in 80% of datasets",
    "dark skin representation only 15% (target: 25%)",
    "only 5 studies report subgroup metrics"
  ],
  "confidence": "high/medium/low",
  "citations": [
    {{
      "title": "Paper title",
      "url": "paper URL",
      "evidence_type": "dataset_composition/subgroup_performance/mitigation"
    }}
  ],
  "breakdown": {{
    "race_label_availability": 0.8,
    "dark_skin_representation": 0.6,
    "subgroup_metrics": 0.7,
    "geographic_concentration": 0.5,
    "fairness_method_coverage": 0.9,
    "external_validation": 0.8
  }}
}}"""

INITIAL_GREETING = """Hello! I'm MagnifyingMed. I analyze racial bias in medical AI research using current literature.

Tell me what medical field or condition you'd like me to analyze (e.g., dermatology, skin cancer, cardiology), and I'll provide research-backed findings on bias gaps."""

CONTEXT_GATHERING_PROMPT = """I'll analyze under-explored racial bias areas in medical AI research. 

You mentioned: {user_input}

I can work with just the medical field. If you want to specify a condition or time range, that's helpful but not required. I'll proceed with analysis using research from the past 5 years by default.
"""

ANALYSIS_PROMPT = """Based on the analysis of {scope} research (past {years} years), here are the key findings:

{findings}

Under-Explored Bias Score: {score} (Threshold: {threshold})
Status: {flagged_status}

Key Drivers:
{drivers}

Would you like me to:
1. Provide specific mitigation methods to address these gaps?
2. Show you recent papers that applied fairness methods?
3. Dive deeper into any specific dimension?
4. Analyze a different medical field or condition?"""

MITIGATION_RECOMMENDATIONS_PROMPT = """Based on the identified gaps in {scope} research, here are recommended mitigation methods:

{recommendations}

Recent papers that applied these methods:
{papers}

Would you like me to:
1. Provide more details on any specific method?
2. Show you implementation examples?
3. Analyze another area?"""

