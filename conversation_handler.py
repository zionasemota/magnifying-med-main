"""
Main conversation handler for MagnifyingMed
"""

import json
from typing import Dict, Any, Optional, List
from .context_manager import ContextManager
from .llm_client import LLMClient
from .scoring import BiasScorer
from .prompts import (
    INITIAL_GREETING, CONTEXT_GATHERING_PROMPT, ANALYSIS_PROMPT,
    MITIGATION_RECOMMENDATIONS_PROMPT
)
from .config import SCORE_WEIGHTS, BIAS_SCORE_THRESHOLD


class ConversationHandler:
    """Handles the main conversation flow"""
    
    def __init__(self, llm_client: Optional[LLMClient] = None, scorer: Optional[BiasScorer] = None):
        self.context_manager = ContextManager()
        self.llm_client = llm_client or LLMClient()
        self.scorer = scorer or BiasScorer(weights=SCORE_WEIGHTS, threshold=BIAS_SCORE_THRESHOLD)
        self.analysis_results: Optional[Dict[str, Any]] = None
    
    def handle_message(self, user_input: str) -> str:
        """
        Handle a user message and return response
        
        Args:
            user_input: User's message
            
        Returns:
            Assistant's response
        """
        # Update context
        self.context_manager.update_context(user_input)
        
        input_lower = user_input.lower()
        
        # If we have medical field, proceed directly to analysis (be proactive)
        if self.context_manager.has_sufficient_context() and not self.analysis_results:
            # Check if user explicitly doesn't want analysis yet
            if not any(word in input_lower for word in ["wait", "not yet", "don't", "no", "later"]):
                # Proceed with analysis immediately
                return self._perform_analysis()
        
        # Handle special responses first
        if "all of them" in input_lower or "all" in input_lower:
            if self.context_manager.context.get("medical_field") and not self.analysis_results:
                # User wants analysis of all bias aspects
                self.context_manager.context["bias_aspects"] = ["all"]
                if self.context_manager.has_sufficient_context():
                    return self._perform_analysis()
        
        # Check if we have sufficient context
        if not self.context_manager.has_sufficient_context():
            # Try to extract medical field using LLM if keyword matching failed
            if not self.context_manager.context.get("medical_field"):
                extracted = self._extract_medical_field_llm(user_input)
                if extracted:
                    self.context_manager.context["medical_field"] = extracted
                    # If we now have enough, proceed
                    if self.context_manager.has_sufficient_context():
                        return self._perform_analysis()
            
            # Only ask one simple question if we really need it
            return self._ask_for_medical_field_only()
        
        # Check if user is asking for analysis
        if self._is_analysis_request(user_input):
            return self._perform_analysis()
        
        # Check if user is asking for mitigation methods
        if self._is_mitigation_request(user_input):
            return self._provide_mitigation_recommendations()
        
        # Check if user is asking follow-up questions
        if self._is_follow_up(user_input):
            return self._handle_follow_up(user_input)
        
        # Handle "yes" responses
        if input_lower in ["yes", "y", "yeah", "sure", "please"]:
            if "mitigation" in self.context_manager.conversation_history[-2].get("content", "").lower() if len(self.context_manager.conversation_history) > 1 else "":
                return self._provide_mitigation_recommendations()
            elif self.analysis_results:
                return self._provide_mitigation_recommendations()
        
        # Default: acknowledge and offer options
        return self._default_response()
    
    def _ask_for_medical_field_only(self) -> str:
        """Ask only for medical field - be direct and brief"""
        return "What medical field or condition would you like me to analyze? (e.g., dermatology, cardiology, radiology, skin cancer, heart disease)"
    
    def _extract_medical_field_llm(self, user_input: str) -> Optional[str]:
        """Use LLM to extract medical field from user input"""
        prompt = f"""Extract the medical field from this user input. Return ONLY the field name (one word) or "none" if unclear.

User input: {user_input}

Common fields: dermatology, cardiology, radiology, oncology, pulmonology, ophthalmology, pathology

Return only the field name:"""
        
        try:
            response = self.llm_client.generate_response(prompt, temperature=0.3)
            field = response.strip().lower()
            # Validate it's a real field
            valid_fields = ["dermatology", "cardiology", "radiology", "oncology", "pulmonology", "ophthalmology", "pathology"]
            if field in valid_fields:
                return field
        except:
            pass
        return None
    
    def _ask_for_missing_context(self) -> str:
        """Ask user for missing context information - simplified"""
        return self._ask_for_medical_field_only()
    
    def _is_analysis_request(self, user_input: str) -> bool:
        """Check if user is requesting analysis"""
        keywords = ["analyze", "find", "identify", "look at", "study", "examine", "check", 
                   "help", "can you", "areas", "gaps", "bias"]
        input_lower = user_input.lower()
        # Check if it's a question about bias/research areas
        if any(keyword in input_lower for keyword in ["bias", "areas", "gaps", "under-explored"]):
            if any(qword in input_lower for qword in ["find", "identify", "help", "what", "where"]):
                return True
        return any(keyword in input_lower for keyword in keywords) and self.context_manager.has_sufficient_context()
    
    def _is_mitigation_request(self, user_input: str) -> bool:
        """Check if user is asking for mitigation methods"""
        keywords = ["mitigation", "method", "solution", "address", "reduce", "fix", "improve"]
        return any(keyword in user_input.lower() for keyword in keywords)
    
    def _is_follow_up(self, user_input: str) -> bool:
        """Check if user is asking a follow-up question"""
        keywords = ["what", "how", "why", "when", "where", "can you", "show me", "tell me"]
        return any(user_input.lower().startswith(keyword) for keyword in keywords)
    
    def _perform_analysis(self) -> str:
        """Perform the bias analysis"""
        scope = self.context_manager.get_scope()
        years = self.context_manager.get_time_range()
        
        try:
            # Perform analyses
            dataset_analysis = self.llm_client.analyze_dataset_composition(scope, years)
            subgroup_analysis = self.llm_client.analyze_subgroup_performance(scope)
            mitigation_analysis = self.llm_client.analyze_mitigation_validation(scope, years)
            
            # Compute bias score
            score_results = self.scorer.compute_bias_score(
                dataset_analysis, subgroup_analysis, mitigation_analysis
            )
            
            # Store results
            self.analysis_results = {
                "scope": scope,
                "years": years,
                "dataset_analysis": dataset_analysis,
                "subgroup_analysis": subgroup_analysis,
                "mitigation_analysis": mitigation_analysis,
                "score_results": score_results
            }
            
            # Generate response
            return self._format_analysis_response(score_results, dataset_analysis, 
                                                 subgroup_analysis, mitigation_analysis)
        
        except Exception as e:
            return f"I encountered an error while analyzing: {str(e)}. Please try again or provide more specific information."
    
    def _format_analysis_response(self, score_results: Dict, dataset_analysis: Dict,
                                 subgroup_analysis: Dict, mitigation_analysis: Dict) -> str:
        """Format the analysis response for the user"""
        scope = self.context_manager.get_scope()
        years = self.context_manager.get_time_range()
        bias_aspects = self.context_manager.context.get("bias_aspects", [])
        
        # Build findings based on what user asked for
        findings_parts = []
        
        # Check if user wants all aspects or specific ones
        wants_all = "all" in " ".join(bias_aspects).lower() or len(bias_aspects) == 0
        
        # Dataset findings (Data Imbalance)
        if wants_all or "data imbalance" in bias_aspects or "data representation" in bias_aspects:
            dataset_summary = dataset_analysis.get("summary", {})
            if dataset_summary.get("total_datasets", 0) > 0:
                race_labels = dataset_summary.get("datasets_with_race_labels", 0)
                total = dataset_summary.get("total_datasets", 0)
                dark_skin_prop = dataset_summary.get("avg_dark_skin_proportion", 0.0)
                
                findings_parts.append(
                    f"**Data Imbalance:** {total - race_labels}/{total} datasets lack race labels. "
                    f"Dark skin representation averages {dark_skin_prop*100:.0f}% (target: 25%)."
                )
        
        # Subgroup performance findings (Performance Gaps)
        if wants_all or "performance gaps" in bias_aspects or "performance" in " ".join(bias_aspects).lower():
            subgroup_summary = subgroup_analysis.get("summary", {})
            if subgroup_summary.get("total_studies", 0) > 0:
                with_metrics = subgroup_summary.get("studies_with_subgroup_metrics", 0)
                total = subgroup_summary.get("total_studies", 0)
                avg_gap = subgroup_summary.get("avg_performance_gap", 0.0)
                
                findings_parts.append(
                    f"**Performance Gaps:** Only {with_metrics}/{total} studies report subgroup metrics. "
                    f"Average performance gap: {avg_gap*100:.1f}%."
                )
        
        # Mitigation findings
        mitigation_summary = mitigation_analysis.get("summary", {})
        if mitigation_summary.get("total_studies", 0) > 0:
            with_methods = mitigation_summary.get("studies_with_fairness_methods", 0)
            with_validation = mitigation_summary.get("studies_with_external_validation", 0)
            total = mitigation_summary.get("total_studies", 0)
            
            if with_methods < total * 0.2:  # Less than 20% use fairness methods
                findings_parts.append(
                    f"Most studies don't apply fairness methods or validate outside the US. "
                    f"I'll scan for mitigation or validation coverage."
                )
        
        # Use LLM to generate a natural, research-backed response
        findings_json = json.dumps({
            "findings": findings_parts,
            "score": score_results.get('score', 0.0),
            "threshold": score_results.get('threshold', 0.30),
            "flagged": score_results.get("flagged", False),
            "drivers": score_results.get("drivers", []),
            "scope": scope,
            "years": years,
            "dataset_summary": dataset_analysis.get("summary", {}),
            "subgroup_summary": subgroup_analysis.get("summary", {}),
            "mitigation_summary": mitigation_analysis.get("summary", {})
        }, indent=2)
        
        prompt = f"""You are an equity-focused biomedical analyst. Based on this analysis of {scope} research (past {years} years), write a clear, research-backed response for the user.

Analysis Results:
{findings_json}

Write a natural, informative response that:
1. Summarizes the key findings about racial bias gaps
2. References specific research patterns and data
3. Explains the Under-Explored Bias Score ({score_results.get('score', 0.0):.2f}) and what it means
4. Highlights the main drivers of bias
5. Is conversational but informative
6. Mentions that you can provide mitigation methods and papers

Keep it concise (3-4 paragraphs max) and focus on actionable insights from the research."""
        
        response = self.llm_client.generate_response(prompt, temperature=0.7)
        
        # Add follow-up options
        response += "\n\nI can also provide specific mitigation methods, show recent papers that address these gaps, or analyze a different medical field."
        
        self.context_manager.add_assistant_response(response)
        return response
    
    def _provide_mitigation_recommendations(self) -> str:
        """Provide mitigation method recommendations"""
        if not self.analysis_results:
            # Perform analysis first if not done
            analysis_response = self._perform_analysis()
            if "error" in analysis_response.lower():
                return analysis_response
        
        scope = self.context_manager.get_scope()
        mitigation_analysis = self.analysis_results["mitigation_analysis"]
        
        # Extract papers that used fairness methods
        papers = []
        for study in mitigation_analysis.get("studies", []):
            if study.get("fairness_methods"):
                papers.append({
                    "title": study.get("paper", "Unknown"),
                    "methods": study.get("fairness_methods", []),
                    "url": study.get("url", "")
                })
        
        # Use LLM to generate research-backed mitigation recommendations
        score_results = self.analysis_results["score_results"]
        scope_lower = scope.lower()
        
        # Check what the user is asking about
        last_user_msg = ""
        if self.context_manager.conversation_history:
            for msg in reversed(self.context_manager.conversation_history):
                if msg.get("role") == "user":
                    last_user_msg = msg.get("content", "").lower()
                    break
        
        analysis_json = json.dumps({
            "scope": scope,
            "score_breakdown": score_results.get("breakdown", {}),
            "drivers": score_results.get("drivers", []),
            "mitigation_analysis": mitigation_analysis,
            "papers_with_methods": papers
        }, indent=2)
        
        prompt = f"""You are an equity-focused biomedical analyst. Based on this bias analysis for {scope}, provide specific, research-backed mitigation recommendations.

Analysis Results:
{analysis_json}

User question context: {last_user_msg if last_user_msg else 'general recommendations'}

Provide practical, research-backed mitigation methods that address the identified gaps. Reference specific techniques from the literature when possible. Format as clear, actionable recommendations with brief explanations of why each method helps."""
        
        recommendations_text = self.llm_client.generate_response(prompt, temperature=0.7)
        
        # Format papers from analysis
        papers_text = ""
        if papers:
            papers_list = []
            for paper in papers[:5]:  # Top 5 papers
                methods_str = ", ".join(paper["methods"])
                url_str = f" ({paper['url']})" if paper.get("url") else ""
                papers_list.append(f"- {paper['title']} - Methods: {methods_str}{url_str}")
            papers_text = "\n\nRecent papers that applied fairness methods:\n" + "\n".join(papers_list)
        else:
            # Use LLM to suggest relevant papers based on scope
            papers_prompt = f"""Based on research about {scope} and racial bias in medical AI, suggest 2-3 relevant recent papers (published in the past 5 years) that address fairness or bias mitigation. 

Format as a list with paper titles and brief descriptions of how they address bias. If you know specific papers, include them. Otherwise, suggest the types of papers researchers should look for."""
            
            papers_text = "\n\n" + self.llm_client.generate_response(papers_prompt, temperature=0.7)
        
        # Format response
        response = f"Based on the identified gaps in {scope} research, here are recommended mitigation methods:\n\n{recommendations_text}"
        if papers_text:
            response += papers_text
        
        self.context_manager.add_assistant_response(response)
        return response
    
    def _handle_follow_up(self, user_input: str) -> str:
        """Handle follow-up questions"""
        input_lower = user_input.lower()
        
        # Handle specific follow-up patterns
        if "concerning" in input_lower or "that's" in input_lower:
            if self.analysis_results:
                response = (
                    "Exactly. The issue starts with who's represented in the data and extends to how "
                    "disease is diagnosed and treated. When clinical norms are built from biased datasets, "
                    "the AI inherits and amplifies those biases."
                )
                
                self.context_manager.add_assistant_response(response)
                return response
        
        if "what can i" in input_lower or "how can i" in input_lower:
            if "focus" in input_lower or "study" in input_lower or "reduce" in input_lower:
                return self._provide_mitigation_recommendations()
        
        # Use LLM to generate contextual response for other questions
        conversation_summary = self.context_manager.get_conversation_summary()
        
        prompt = f"""Based on this conversation about racial bias in medical AI research:

{conversation_summary}

User question: {user_input}

Provide a helpful, concise response. If the user is asking about specific mitigation methods, bias aspects, or wants to see papers, provide that information. Keep responses conversational and natural."""

        response = self.llm_client.generate_response(prompt, temperature=0.7)
        self.context_manager.add_assistant_response(response)
        return response
    
    def _default_response(self) -> str:
        """Default response when intent is unclear - be proactive"""
        if self.context_manager.has_sufficient_context() and not self.analysis_results:
            # If we have context but no analysis, just do it
            return self._perform_analysis()
        elif self.context_manager.has_sufficient_context():
            return ("I can help you with:\n"
                   "1. Provide mitigation method recommendations\n"
                   "2. Answer specific questions about bias in medical AI\n"
                   "3. Analyze a different medical field")
        else:
            return self._ask_for_medical_field_only()
    
    def reset(self):
        """Reset the conversation"""
        self.context_manager = ContextManager()
        self.analysis_results = None
    
    def get_greeting(self) -> str:
        """Get the initial greeting"""
        return INITIAL_GREETING

