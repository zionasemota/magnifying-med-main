"""
Configuration settings for MagnifyingMed
"""

import os
from typing import Dict, List

# API Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-5")

# Azure OpenAI Configuration
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT", "")
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY", "")
AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION", "")
AZURE_OPENAI_DEPLOYMENT_NAME = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "")  # Replace with your actual deployment name

# Scoring Configuration
BIAS_SCORE_THRESHOLD = 0.30
MIN_SOURCES_FOR_FLAG = 2

# Weight configuration for Under-Explored Bias Score
SCORE_WEIGHTS = {
    "race_label_availability": 0.15,
    "dark_skin_representation": 0.25,
    "subgroup_metrics": 0.20,
    "geographic_concentration": 0.15,
    "fairness_method_coverage": 0.15,
    "external_validation": 0.10
}

# Required context fields for analysis
REQUIRED_CONTEXT_FIELDS = [
    "medical_field",
    "time_range",
    "specific_condition"
]

# Fitzpatrick scale ranges
FITZPATRICK_LIGHT = [1, 2, 3]  # I-III
FITZPATRICK_DARK = [4, 5, 6]   # IV-VI
TARGET_DARK_SKIN_PROPORTION = 0.25  # 25% target for dark skin representation

