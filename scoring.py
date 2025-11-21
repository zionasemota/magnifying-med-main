"""
Scoring system for computing Under-Explored Bias Score
"""

import json
from typing import Dict, Any, List, Optional
from .config import (
    SCORE_WEIGHTS, BIAS_SCORE_THRESHOLD, MIN_SOURCES_FOR_FLAG,
    TARGET_DARK_SKIN_PROPORTION
)


class BiasScorer:
    """Compute Under-Explored Bias Score from analysis results"""
    
    def __init__(self, weights: Optional[Dict[str, float]] = None, 
                 threshold: Optional[float] = None):
        self.weights = weights or SCORE_WEIGHTS
        self.threshold = threshold or BIAS_SCORE_THRESHOLD
        
        # Validate weights sum to 1.0
        total_weight = sum(self.weights.values())
        if abs(total_weight - 1.0) > 0.01:
            raise ValueError(f"Weights must sum to 1.0, got {total_weight}")
    
    def compute_race_label_score(self, dataset_analysis: Dict[str, Any]) -> float:
        """
        Score based on race label availability
        Higher score = more missing labels (worse)
        
        Args:
            dataset_analysis: Dataset composition analysis
            
        Returns:
            Score between 0 and 1
        """
        summary = dataset_analysis.get("summary", {})
        total = summary.get("total_datasets", 0)
        with_labels = summary.get("datasets_with_race_labels", 0)
        
        if total == 0:
            return 1.0  # No datasets = worst case
        
        missing_ratio = 1.0 - (with_labels / total)
        return min(missing_ratio, 1.0)
    
    def compute_dark_skin_representation_score(self, dataset_analysis: Dict[str, Any]) -> float:
        """
        Score based on dark skin representation gap or minority representation
        Higher score = larger gap from target (worse)
        
        Args:
            dataset_analysis: Dataset composition analysis
            
        Returns:
            Score between 0 and 1
        """
        summary = dataset_analysis.get("summary", {})
        
        # For dermatology: use dark skin proportion
        avg_dark_skin_prop = summary.get("avg_dark_skin_proportion", None)
        if avg_dark_skin_prop is not None:
            if avg_dark_skin_prop >= TARGET_DARK_SKIN_PROPORTION:
                return 0.0  # Target met or exceeded
            
            # Score increases as gap increases
            gap = TARGET_DARK_SKIN_PROPORTION - avg_dark_skin_prop
            max_gap = TARGET_DARK_SKIN_PROPORTION  # Worst case: 0% dark skin
            score = gap / max_gap if max_gap > 0 else 1.0
            return min(score, 1.0)
        
        # For other fields: use minority representation (target: at least 25%)
        avg_minority_rep = summary.get("avg_minority_representation", 0.0)
        target_minority = 0.25  # 25% target for minority representation
        
        if avg_minority_rep >= target_minority:
            return 0.0
        
        gap = target_minority - avg_minority_rep
        max_gap = target_minority
        score = gap / max_gap if max_gap > 0 else 1.0
        return min(score, 1.0)
    
    def compute_subgroup_metrics_score(self, subgroup_analysis: Dict[str, Any]) -> float:
        """
        Score based on subgroup metric reporting
        Higher score = fewer studies report subgroup metrics (worse)
        
        Args:
            subgroup_analysis: Subgroup performance analysis
            
        Returns:
            Score between 0 and 1
        """
        summary = subgroup_analysis.get("summary", {})
        total = summary.get("total_studies", 0)
        with_metrics = summary.get("studies_with_subgroup_metrics", 0)
        no_reporting = subgroup_analysis.get("no_subgroup_reporting", 0)
        
        if total == 0:
            return 1.0
        
        missing_ratio = no_reporting / total if no_reporting > 0 else (1.0 - (with_metrics / total))
        return min(missing_ratio, 1.0)
    
    def compute_geographic_concentration_score(self, dataset_analysis: Dict[str, Any],
                                              mitigation_analysis: Dict[str, Any]) -> float:
        """
        Score based on geographic concentration
        Higher score = more concentrated (worse)
        
        Args:
            dataset_analysis: Dataset composition analysis
            mitigation_analysis: Mitigation and validation analysis
            
        Returns:
            Score between 0 and 1
        """
        # Check dataset geographic diversity
        dataset_summary = dataset_analysis.get("summary", {})
        geo_diversity = dataset_summary.get("geographic_diversity", "low")
        
        # Check validation geographic diversity
        validation = mitigation_analysis.get("validation", {})
        val_geo_diversity = validation.get("geographic_diversity", "low")
        
        # Map to scores
        diversity_map = {"low": 1.0, "medium": 0.5, "high": 0.0}
        dataset_score = diversity_map.get(geo_diversity.lower(), 1.0)
        val_score = diversity_map.get(val_geo_diversity.lower(), 1.0)
        
        # Take average
        return (dataset_score + val_score) / 2.0
    
    def compute_fairness_method_score(self, mitigation_analysis: Dict[str, Any]) -> float:
        """
        Score based on fairness method coverage
        Higher score = fewer studies use fairness methods (worse)
        
        Args:
            mitigation_analysis: Mitigation and validation analysis
            
        Returns:
            Score between 0 and 1
        """
        summary = mitigation_analysis.get("summary", {})
        total = summary.get("total_studies", 0)
        with_methods = summary.get("studies_with_fairness_methods", 0)
        
        if total == 0:
            return 1.0
        
        missing_ratio = 1.0 - (with_methods / total)
        return min(missing_ratio, 1.0)
    
    def compute_external_validation_score(self, mitigation_analysis: Dict[str, Any]) -> float:
        """
        Score based on external validation
        Higher score = fewer external validations (worse)
        
        Args:
            mitigation_analysis: Mitigation and validation analysis
            
        Returns:
            Score between 0 and 1
        """
        summary = mitigation_analysis.get("summary", {})
        total = summary.get("total_studies", 0)
        with_validation = summary.get("studies_with_external_validation", 0)
        
        if total == 0:
            return 1.0
        
        missing_ratio = 1.0 - (with_validation / total)
        return min(missing_ratio, 1.0)
    
    def compute_bias_score(self, dataset_analysis: Dict[str, Any],
                          subgroup_analysis: Dict[str, Any],
                          mitigation_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Compute overall Under-Explored Bias Score
        
        Args:
            dataset_analysis: Dataset composition analysis
            subgroup_analysis: Subgroup performance analysis
            mitigation_analysis: Mitigation and validation analysis
            
        Returns:
            Dictionary with score, breakdown, and drivers
        """
        # Compute individual scores
        breakdown = {
            "race_label_availability": self.compute_race_label_score(dataset_analysis),
            "dark_skin_representation": self.compute_dark_skin_representation_score(dataset_analysis),
            "subgroup_metrics": self.compute_subgroup_metrics_score(subgroup_analysis),
            "geographic_concentration": self.compute_geographic_concentration_score(
                dataset_analysis, mitigation_analysis
            ),
            "fairness_method_coverage": self.compute_fairness_method_score(mitigation_analysis),
            "external_validation": self.compute_external_validation_score(mitigation_analysis)
        }
        
        # Weighted sum
        total_score = sum(
            breakdown[key] * self.weights.get(key, 0.0)
            for key in breakdown
        )
        
        # Identify drivers (top contributors)
        drivers = []
        sorted_breakdown = sorted(breakdown.items(), key=lambda x: x[1], reverse=True)
        
        for key, score in sorted_breakdown[:3]:  # Top 3 drivers
            if score > 0.5:
                driver_desc = self._get_driver_description(key, score, dataset_analysis, 
                                                          subgroup_analysis, mitigation_analysis)
                drivers.append(driver_desc)
        
        # Determine if flagged
        flagged = total_score >= self.threshold
        
        # Count sources for confidence
        total_sources = (
            dataset_analysis.get("summary", {}).get("total_datasets", 0) +
            subgroup_analysis.get("summary", {}).get("total_studies", 0) +
            mitigation_analysis.get("summary", {}).get("total_studies", 0)
        )
        
        confidence = "high" if total_sources >= MIN_SOURCES_FOR_FLAG else "medium" if total_sources > 0 else "low"
        
        return {
            "score": round(total_score, 3),
            "threshold": self.threshold,
            "flagged": flagged,
            "breakdown": breakdown,
            "drivers": drivers,
            "confidence": confidence
        }
    
    def _get_driver_description(self, key: str, score: float,
                               dataset_analysis: Dict, subgroup_analysis: Dict,
                               mitigation_analysis: Dict) -> str:
        """Generate human-readable description of a driver"""
        if key == "race_label_availability":
            summary = dataset_analysis.get("summary", {})
            total = summary.get("total_datasets", 0)
            with_labels = summary.get("datasets_with_race_labels", 0)
            if total > 0:
                return f"Missing race labels in {total - with_labels}/{total} datasets ({100*(1-score):.0f}% missing)"
            return "Race labels missing in datasets"
        
        elif key == "dark_skin_representation":
            summary = dataset_analysis.get("summary", {})
            avg_dark_prop = summary.get("avg_dark_skin_proportion")
            avg_minority = summary.get("avg_minority_representation")
            
            if avg_dark_prop is not None:
                gap = TARGET_DARK_SKIN_PROPORTION - avg_dark_prop
                return f"Dark skin representation only {avg_dark_prop*100:.0f}% (target: {TARGET_DARK_SKIN_PROPORTION*100:.0f}%, gap: {gap*100:.0f}%)"
            elif avg_minority is not None:
                gap = 0.25 - avg_minority
                return f"Minority representation only {avg_minority*100:.0f}% (target: 25%, gap: {gap*100:.0f}%)"
            return "Underrepresented groups in datasets"
        
        elif key == "subgroup_metrics":
            summary = subgroup_analysis.get("summary", {})
            total = summary.get("total_studies", 0)
            with_metrics = summary.get("studies_with_subgroup_metrics", 0)
            if total > 0:
                return f"Only {with_metrics}/{total} studies report subgroup metrics ({100*score:.0f}% missing)"
            return "Lack of subgroup metric reporting"
        
        elif key == "geographic_concentration":
            summary = dataset_analysis.get("summary", {})
            geo_diversity = summary.get("geographic_diversity", "low")
            return f"Low geographic diversity: {geo_diversity}"
        
        elif key == "fairness_method_coverage":
            summary = mitigation_analysis.get("summary", {})
            total = summary.get("total_studies", 0)
            with_methods = summary.get("studies_with_fairness_methods", 0)
            if total > 0:
                return f"Only {with_methods}/{total} studies apply fairness methods ({100*score:.0f}% missing)"
            return "Lack of fairness method application"
        
        elif key == "external_validation":
            summary = mitigation_analysis.get("summary", {})
            total = summary.get("total_studies", 0)
            with_validation = summary.get("studies_with_external_validation", 0)
            if total > 0:
                return f"Only {with_validation}/{total} studies have external validation ({100*score:.0f}% missing)"
            return "Lack of external validation"
        
        return f"{key}: {score:.2f}"

