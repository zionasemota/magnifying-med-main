"""
LLM client for interacting with external APIs (OpenAI GPT)
"""

import json
import os
import re
from typing import Dict, Any, Optional
from openai import OpenAI
from .config import (
    OPENAI_API_KEY, OPENAI_MODEL,
    AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_API_KEY,
    AZURE_OPENAI_API_VERSION, AZURE_OPENAI_DEPLOYMENT_NAME
)
from .research_client import ResearchClient


class LLMClient:
    """Client for interacting with LLM APIs"""
    
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        # Check if Azure OpenAI is configured
        azure_endpoint = AZURE_OPENAI_ENDPOINT
        azure_api_key = AZURE_OPENAI_API_KEY or api_key
        azure_deployment = AZURE_OPENAI_DEPLOYMENT_NAME or model or OPENAI_MODEL
        
        if azure_endpoint and azure_api_key:
            # Use Azure OpenAI
            self.api_key = azure_api_key
            self.model = azure_deployment
            # Azure OpenAI base_url format
            base_url = f"{azure_endpoint.rstrip('/')}/openai/deployments/{azure_deployment}"
            self.client = OpenAI(
                api_key=azure_api_key,
                base_url=base_url,
                default_query={"api-version": AZURE_OPENAI_API_VERSION}
            )
        else:
            # Use standard OpenAI
            self.api_key = api_key or OPENAI_API_KEY
            self.model = model or OPENAI_MODEL
            
            if not self.api_key:
                raise ValueError("OpenAI API key not found. Set OPENAI_API_KEY or AZURE_OPENAI_API_KEY environment variable.")
            
            self.client = OpenAI(api_key=self.api_key)
        
        # Initialize research client for fetching real papers
        self.research_client = ResearchClient()
    
    def call_llm(self, prompt: str, temperature: float = 0.3, max_tokens: int = 2000) -> str:
        """
        Call the LLM API with a prompt
        
        Args:
            prompt: The prompt to send
            temperature: Temperature for generation (lower = more deterministic)
            max_tokens: Maximum tokens to generate
            
        Returns:
            Response text from the LLM
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an equity-focused biomedical analyst. Always output valid JSON when requested."},
                    {"role": "user", "content": prompt}
                ],
                temperature=temperature,
                max_tokens=max_tokens
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            raise Exception(f"Error calling LLM API: {str(e)}")
    
    def parse_json_response(self, response: str) -> Dict[str, Any]:
        """
        Parse JSON from LLM response, handling code blocks if present
        
        Args:
            response: Raw response from LLM
            
        Returns:
            Parsed JSON dictionary
        """
        # Remove markdown code blocks if present
        response = re.sub(r'```json\s*', '', response)
        response = re.sub(r'```\s*', '', response)
        response = response.strip()
        
        try:
            return json.loads(response)
        except json.JSONDecodeError as e:
            # Try to extract JSON from the response
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                try:
                    return json.loads(json_match.group())
                except json.JSONDecodeError:
                    pass
            raise ValueError(f"Failed to parse JSON response: {str(e)}\nResponse: {response[:500]}")
    
    def analyze_dataset_composition(self, scope: str, years: int) -> Dict[str, Any]:
        """
        Analyze dataset composition for a given scope using real research papers
        
        Args:
            scope: Medical field/condition to analyze
            years: Number of years to look back
            
        Returns:
            Dictionary with dataset analysis results
        """
        from .prompts import DATASET_COMPOSITION_PROMPT
        
        try:
            # Fetch real papers first
            search_query = f"{scope} dataset AI machine learning {years} years"
            papers = self.research_client.search_all(search_query, max_results_per_source=15)
            papers_text = self.research_client.format_papers_for_llm(papers, max_papers=30) if papers else "No papers found."
            
            # Update prompt to include real papers
            prompt = DATASET_COMPOSITION_PROMPT.format(scope=scope, years=years)
            prompt += f"\n\nReal research papers found:\n{papers_text}\n\n"
            prompt += "Analyze these actual papers and extract dataset information from them. Base your analysis on the real papers provided above."
            
            response = self.call_llm(prompt)
            result = self.parse_json_response(response)
            
            # Add real papers to result (ensure result is a dict)
            if result is None:
                result = {}
            if not isinstance(result, dict):
                result = {"analysis": result}
            
            result["real_papers"] = papers[:20] if papers else []  # Store first 20 papers
            result["total_papers_found"] = len(papers) if papers else 0
            
            return result
        except Exception as e:
            # Return a basic structure even if analysis fails
            return {
                "datasets": [],
                "summary": {
                    "total_datasets": 0,
                    "datasets_with_race_labels": 0,
                    "avg_dark_skin_proportion": 0.0
                },
                "error": str(e),
                "real_papers": [],
                "total_papers_found": 0
            }
    
    def analyze_subgroup_performance(self, scope: str) -> Dict[str, Any]:
        """
        Analyze subgroup performance metrics using real research papers
        
        Args:
            scope: Medical field/condition to analyze
            
        Returns:
            Dictionary with subgroup performance analysis
        """
        from .prompts import SUBGROUP_PERFORMANCE_PROMPT
        
        try:
            # Fetch real papers about subgroup performance
            search_query = f"{scope} subgroup performance racial bias fairness AI"
            papers = self.research_client.search_all(search_query, max_results_per_source=15)
            papers_text = self.research_client.format_papers_for_llm(papers, max_papers=30) if papers else "No papers found."
            
            # Update prompt to include real papers
            prompt = SUBGROUP_PERFORMANCE_PROMPT.format(scope=scope)
            prompt += f"\n\nReal research papers found:\n{papers_text}\n\n"
            prompt += "Extract subgroup performance metrics from these actual papers. Reference specific papers when providing metrics."
            
            response = self.call_llm(prompt)
            result = self.parse_json_response(response)
            
            # Add real papers to result (ensure result is a dict)
            if result is None:
                result = {}
            if not isinstance(result, dict):
                result = {"analysis": result}
            
            result["real_papers"] = papers[:20] if papers else []
            result["total_papers_found"] = len(papers) if papers else 0
            
            return result
        except Exception as e:
            return {
                "studies": [],
                "summary": {
                    "total_studies": 0,
                    "studies_with_subgroup_metrics": 0,
                    "avg_performance_gap": 0.0
                },
                "error": str(e),
                "real_papers": [],
                "total_papers_found": 0
            }
    
    def analyze_mitigation_validation(self, scope: str, years: int) -> Dict[str, Any]:
        """
        Analyze fairness method coverage and external validation using real research papers
        
        Args:
            scope: Medical field/condition to analyze
            years: Number of years to look back
            
        Returns:
            Dictionary with mitigation and validation analysis
        """
        from .prompts import MITIGATION_VALIDATION_PROMPT
        
        try:
            # Fetch real papers about fairness methods
            search_query = f"{scope} fairness mitigation bias reduction AI {years} years"
            papers = self.research_client.search_all(search_query, max_results_per_source=15)
            papers_text = self.research_client.format_papers_for_llm(papers, max_papers=30) if papers else "No papers found."
            
            # Update prompt to include real papers
            prompt = MITIGATION_VALIDATION_PROMPT.format(scope=scope, years=years)
            prompt += f"\n\nReal research papers found:\n{papers_text}\n\n"
            prompt += "Analyze these actual papers for fairness methods and validation approaches. Reference specific papers when listing methods."
            
            response = self.call_llm(prompt)
            result = self.parse_json_response(response)
            
            # Add real papers to result (ensure result is a dict)
            if result is None:
                result = {}
            if not isinstance(result, dict):
                result = {"analysis": result}
            
            result["real_papers"] = papers[:20] if papers else []
            result["total_papers_found"] = len(papers) if papers else 0
            
            return result
        except Exception as e:
            return {
                "fairness_methods": {},
                "validation": {},
                "studies": [],
                "summary": {
                    "total_studies": 0,
                    "studies_with_fairness_methods": 0
                },
                "error": str(e),
                "real_papers": [],
                "total_papers_found": 0
            }
    
    def synthesize_trends(self, scope: str, dataset_analysis: Dict, 
                         subgroup_analysis: Dict, mitigation_analysis: Dict,
                         weights: Dict, threshold: float) -> Dict[str, Any]:
        """
        Synthesize all analyses into a bias score
        
        Args:
            scope: Medical field/condition
            dataset_analysis: Dataset composition analysis
            subgroup_analysis: Subgroup performance analysis
            mitigation_analysis: Mitigation and validation analysis
            weights: Weight configuration for scoring
            threshold: Threshold for flagging
            
        Returns:
            Dictionary with bias score and drivers
        """
        from .prompts import TREND_SYNTHESIZER_PROMPT
        
        prompt = TREND_SYNTHESIZER_PROMPT.format(
            scope=scope,
            dataset_analysis=json.dumps(dataset_analysis, indent=2),
            subgroup_analysis=json.dumps(subgroup_analysis, indent=2),
            mitigation_analysis=json.dumps(mitigation_analysis, indent=2),
            weights=json.dumps(weights, indent=2),
            threshold=threshold
        )
        response = self.call_llm(prompt, temperature=0.2)
        return self.parse_json_response(response)
    
    def generate_response(self, prompt: str, temperature: float = 0.7) -> str:
        """
        Generate a conversational response (not JSON)
        
        Args:
            prompt: The prompt for conversation
            temperature: Temperature for generation
            
        Returns:
            Response text
        """
        return self.call_llm(prompt, temperature=temperature)

