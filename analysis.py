"""
In-depth analysis module for case studies and literature contextualization
"""

import json
from typing import Dict, Any, List, Optional
from datetime import datetime

# Handle both package and standalone imports
try:
    from .llm_client import LLMClient
except ImportError:
    from llm_client import LLMClient


class InDepthAnalyzer:
    """Provide in-depth analysis of cases of interest and literature contextualization"""
    
    def __init__(self, llm_client: Optional[LLMClient] = None):
        """
        Initialize analyzer
        
        Args:
            llm_client: LLM client for generating analysis
        """
        self.llm_client = llm_client or LLMClient()
    
    def analyze_case_study(self, analysis_results: Dict[str, Any],
                          case_focus: Optional[str] = None) -> Dict[str, Any]:
        """
        Perform in-depth analysis of a specific case of interest
        
        Args:
            analysis_results: Results from bias analysis
            case_focus: Optional specific aspect to focus on (e.g., "data_imbalance", "performance_gaps")
            
        Returns:
            Dictionary with detailed case study analysis
        """
        scope = analysis_results.get('scope', 'Medical AI')
        score_results = analysis_results.get('score_results', {})
        breakdown = score_results.get('breakdown', {})
        drivers = score_results.get('drivers', [])
        
        # Identify the most concerning aspect if not specified
        if not case_focus:
            # Find the highest scoring component
            case_focus = max(breakdown.items(), key=lambda x: x[1])[0] if breakdown else None
        
        # Extract relevant data
        dataset_analysis = analysis_results.get('dataset_analysis', {})
        subgroup_analysis = analysis_results.get('subgroup_analysis', {})
        mitigation_analysis = analysis_results.get('mitigation_analysis', {})
        
        # Build context for LLM analysis
        analysis_context = {
            "scope": scope,
            "case_focus": case_focus,
            "overall_score": score_results.get('score', 0.0),
            "breakdown": breakdown,
            "drivers": drivers,
            "dataset_summary": dataset_analysis.get('summary', {}),
            "subgroup_summary": subgroup_analysis.get('summary', {}),
            "mitigation_summary": mitigation_analysis.get('summary', {}),
            "papers": self._extract_papers(analysis_results)
        }
        
        # Generate in-depth analysis using LLM
        prompt = self._build_case_study_prompt(analysis_context)
        
        try:
            response = self.llm_client.generate_response(prompt, temperature=0.7)
            # Parse structured response if possible
            case_study = self._parse_case_study_response(response, analysis_context)
        except Exception as e:
            # Fallback to structured analysis
            case_study = self._generate_structured_case_study(analysis_context)
            case_study['error'] = str(e)
        
        return case_study
    
    def contextualize_in_literature(self, analysis_results: Dict[str, Any],
                                    comparison_fields: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Contextualize results within existing literature
        
        Args:
            analysis_results: Results from bias analysis
            comparison_fields: Optional list of medical fields to compare against
            
        Returns:
            Dictionary with literature contextualization
        """
        scope = analysis_results.get('scope', 'Medical AI')
        score_results = analysis_results.get('score_results', {})
        
        # Extract papers from analysis
        papers = self._extract_papers(analysis_results)
        
        # Build context
        context = {
            "scope": scope,
            "overall_score": score_results.get('score', 0.0),
            "breakdown": score_results.get('breakdown', {}),
            "drivers": score_results.get('drivers', []),
            "papers": papers,
            "comparison_fields": comparison_fields or ["dermatology", "cardiology", "radiology"]
        }
        
        # Generate literature contextualization
        prompt = self._build_literature_prompt(context)
        
        try:
            response = self.llm_client.generate_response(prompt, temperature=0.7)
            contextualization = self._parse_literature_response(response, context)
        except Exception as e:
            contextualization = self._generate_structured_contextualization(context)
            contextualization['error'] = str(e)
        
        return contextualization
    
    def identify_notable_cases(self, analysis_results: Dict[str, Any],
                               top_n: int = 3) -> List[Dict[str, Any]]:
        """
        Identify notable cases of interest from the analysis
        
        Args:
            analysis_results: Results from bias analysis
            top_n: Number of notable cases to identify
            
        Returns:
            List of notable case dictionaries
        """
        score_results = analysis_results.get('score_results', {})
        breakdown = score_results.get('breakdown', {})
        
        # Sort by score (highest = most concerning)
        sorted_components = sorted(breakdown.items(), key=lambda x: x[1], reverse=True)
        
        notable_cases = []
        for component, score in sorted_components[:top_n]:
            if score > 0.3:  # Only include if above threshold
                case = {
                    "component": component,
                    "score": score,
                    "severity": self._classify_severity(score),
                    "description": self._get_component_description(component, score, analysis_results)
                }
                notable_cases.append(case)
        
        return notable_cases
    
    def generate_baseline_comparison(self, llm_results: Dict[str, Any],
                                    baseline_type: str = "standard") -> Dict[str, Any]:
        """
        Generate baseline scores for comparison
        
        Args:
            llm_results: LLM analysis results
            baseline_type: Type of baseline ("standard", "conservative", "optimistic")
            
        Returns:
            Dictionary with baseline comparison
        """
        # Define baseline strategies
        baseline_strategies = {
            "standard": {
                "race_label_availability": 0.4,  # 40% missing labels
                "dark_skin_representation": 0.3,  # 30% gap
                "subgroup_metrics": 0.5,  # 50% missing
                "geographic_concentration": 0.6,  # High concentration
                "fairness_method_coverage": 0.7,  # 70% missing
                "external_validation": 0.6  # 60% missing
            },
            "conservative": {
                "race_label_availability": 0.6,
                "dark_skin_representation": 0.5,
                "subgroup_metrics": 0.7,
                "geographic_concentration": 0.8,
                "fairness_method_coverage": 0.8,
                "external_validation": 0.7
            },
            "optimistic": {
                "race_label_availability": 0.2,
                "dark_skin_representation": 0.1,
                "subgroup_metrics": 0.3,
                "geographic_concentration": 0.4,
                "fairness_method_coverage": 0.4,
                "external_validation": 0.3
            }
        }
        
        baseline_breakdown = baseline_strategies.get(baseline_type, baseline_strategies["standard"])
        
        # Calculate overall baseline score using same weights as LLM
        from .config import SCORE_WEIGHTS
        baseline_score = sum(
            baseline_breakdown.get(key, 0.0) * SCORE_WEIGHTS.get(key, 0.0)
            for key in baseline_breakdown
        )
        
        llm_breakdown = llm_results.get('score_results', {}).get('breakdown', {})
        llm_score = llm_results.get('score_results', {}).get('score', 0.0)
        
        # Calculate differences
        differences = {
            key: llm_breakdown.get(key, 0.0) - baseline_breakdown.get(key, 0.0)
            for key in baseline_breakdown
        }
        
        overall_difference = llm_score - baseline_score
        
        return {
            "baseline_type": baseline_type,
            "baseline_score": round(baseline_score, 3),
            "llm_score": round(llm_score, 3),
            "difference": round(overall_difference, 3),
            "baseline_breakdown": baseline_breakdown,
            "llm_breakdown": llm_breakdown,
            "differences": differences,
            "improvement_needed": overall_difference > 0,
            "interpretation": self._interpret_comparison(llm_score, baseline_score, overall_difference)
        }
    
    def _build_case_study_prompt(self, context: Dict[str, Any]) -> str:
        """Build prompt for case study analysis"""
        return f"""You are an expert biomedical equity researcher. Provide an in-depth case study analysis.

Context:
- Medical Field: {context['scope']}
- Focus Area: {context['case_focus']}
- Overall Bias Score: {context['overall_score']:.3f}
- Key Drivers: {', '.join(context['drivers'][:3])}

Analysis Data:
{json.dumps({
    'breakdown': context['breakdown'],
    'dataset_summary': context['dataset_summary'],
    'subgroup_summary': context['subgroup_summary'],
    'mitigation_summary': context['mitigation_summary']
}, indent=2)}

Provide a detailed case study analysis that includes:
1. **Problem Statement**: Clear description of the bias issue in {context['case_focus']}
2. **Root Causes**: Analysis of why this bias exists
3. **Impact Assessment**: How this bias affects patient outcomes and healthcare equity
4. **Evidence**: Specific data points and patterns from the analysis
5. **Comparative Context**: How this compares to other medical fields or general AI bias
6. **Recommendations**: Specific, actionable steps to address this bias

Format your response as a structured analysis with clear sections. Be specific, cite patterns from the data, and provide actionable insights."""
    
    def _build_literature_prompt(self, context: Dict[str, Any]) -> str:
        """Build prompt for literature contextualization"""
        papers_text = "\n".join([
            f"- {p.get('title', 'Unknown')} ({p.get('year', 'N/A')})"
            for p in context['papers'][:10]
        ])
        
        return f"""You are an expert biomedical literature analyst. Contextualize these bias analysis results within existing research literature.

Analysis Results:
- Medical Field: {context['scope']}
- Overall Bias Score: {context['overall_score']:.3f}
- Key Bias Drivers: {', '.join(context['drivers'][:3])}

Relevant Papers Found:
{papers_text}

Provide a literature contextualization that includes:
1. **Literature Landscape**: Overview of existing research on bias in {context['scope']}
2. **Consistency with Literature**: How these findings align with or differ from published research
3. **Gaps in Literature**: What the literature is missing that this analysis reveals
4. **Notable Studies**: Reference specific papers that are particularly relevant
5. **Trends Over Time**: How bias research in this field has evolved
6. **Comparative Analysis**: How {context['scope']} compares to {', '.join(context['comparison_fields'])} in terms of bias research

Be specific, reference actual papers when possible, and provide scholarly context."""
    
    def _parse_case_study_response(self, response: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Parse LLM response into structured case study"""
        return {
            "scope": context['scope'],
            "case_focus": context['case_focus'],
            "analysis_text": response,
            "timestamp": datetime.now().isoformat(),
            "overall_score": context['overall_score'],
            "structured_analysis": self._extract_structured_sections(response)
        }
    
    def _parse_literature_response(self, response: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Parse LLM response into structured literature contextualization"""
        return {
            "scope": context['scope'],
            "contextualization_text": response,
            "timestamp": datetime.now().isoformat(),
            "papers_referenced": len(context['papers']),
            "structured_contextualization": self._extract_structured_sections(response)
        }
    
    def _extract_structured_sections(self, text: str) -> Dict[str, str]:
        """Extract structured sections from text"""
        sections = {}
        current_section = None
        current_content = []
        
        lines = text.split('\n')
        for line in lines:
            # Check if line is a section header
            if line.strip().startswith('**') and line.strip().endswith('**'):
                if current_section:
                    sections[current_section] = '\n'.join(current_content).strip()
                current_section = line.strip().strip('*').strip()
                current_content = []
            elif current_section:
                current_content.append(line)
        
        # Add last section
        if current_section:
            sections[current_section] = '\n'.join(current_content).strip()
        
        return sections
    
    def _generate_structured_case_study(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate structured case study from context"""
        return {
            "scope": context['scope'],
            "case_focus": context['case_focus'],
            "overall_score": context['overall_score'],
            "severity": self._classify_severity(context['overall_score']),
            "key_findings": context['drivers'][:3],
            "timestamp": datetime.now().isoformat()
        }
    
    def _generate_structured_contextualization(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate structured contextualization from context"""
        return {
            "scope": context['scope'],
            "overall_score": context['overall_score'],
            "papers_referenced": len(context['papers']),
            "timestamp": datetime.now().isoformat()
        }
    
    def _extract_papers(self, analysis_results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract papers from analysis results"""
        papers = []
        for analysis_type in ['dataset_analysis', 'subgroup_analysis', 'mitigation_analysis']:
            analysis = analysis_results.get(analysis_type, {})
            papers.extend(analysis.get('real_papers', []))
        # Deduplicate
        seen_titles = set()
        unique_papers = []
        for paper in papers:
            title = paper.get('title', '')
            if title and title not in seen_titles:
                seen_titles.add(title)
                unique_papers.append(paper)
        return unique_papers
    
    def _classify_severity(self, score: float) -> str:
        """Classify severity based on score"""
        if score >= 0.7:
            return "Critical"
        elif score >= 0.5:
            return "High"
        elif score >= 0.3:
            return "Moderate"
        else:
            return "Low"
    
    def _get_component_description(self, component: str, score: float,
                                   analysis_results: Dict[str, Any]) -> str:
        """Get description for a component"""
        descriptions = {
            "race_label_availability": f"Missing race labels in datasets (score: {score:.2f})",
            "dark_skin_representation": f"Insufficient dark skin representation (score: {score:.2f})",
            "subgroup_metrics": f"Lack of subgroup performance reporting (score: {score:.2f})",
            "geographic_concentration": f"Geographic concentration bias (score: {score:.2f})",
            "fairness_method_coverage": f"Limited fairness method application (score: {score:.2f})",
            "external_validation": f"Lack of external validation (score: {score:.2f})"
        }
        return descriptions.get(component, f"{component} (score: {score:.2f})")
    
    def _interpret_comparison(self, llm_score: float, baseline_score: float,
                             difference: float) -> str:
        """Interpret comparison between LLM and baseline"""
        if abs(difference) < 0.05:
            return "LLM results are similar to baseline expectations."
        elif difference > 0:
            return f"LLM analysis reveals {difference:.1%} higher bias than baseline, indicating more severe issues."
        else:
            return f"LLM analysis shows {abs(difference):.1%} lower bias than baseline, suggesting some improvement."

