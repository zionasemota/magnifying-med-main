"""
Main conversation handler for MagnifyingMed
"""

import json
import time
from typing import Dict, Any, Optional, List
from .context_manager import ContextManager
from .llm_client import LLMClient
from .scoring import BiasScorer
from .prompts import (
    INITIAL_GREETING, CONTEXT_GATHERING_PROMPT, ANALYSIS_PROMPT,
    MITIGATION_RECOMMENDATIONS_PROMPT
)
from .config import SCORE_WEIGHTS, BIAS_SCORE_THRESHOLD

# Handle imports for metrics tracking
try:
    from .metrics import MetricsTracker
    from .metrics_extractor import MetricsExtractor
except ImportError:
    from metrics import MetricsTracker
    from metrics_extractor import MetricsExtractor


class ConversationHandler:
    """Handles the main conversation flow"""
    
    def __init__(self, llm_client: Optional[LLMClient] = None, scorer: Optional[BiasScorer] = None,
                 enable_metrics_tracking: bool = True):
        self.context_manager = ContextManager()
        self.llm_client = llm_client or LLMClient()
        self.scorer = scorer or BiasScorer(weights=SCORE_WEIGHTS, threshold=BIAS_SCORE_THRESHOLD)
        self.analysis_results: Optional[Dict[str, Any]] = None
        
        # Metrics tracking (doesn't change conversation behavior)
        self.enable_metrics_tracking = enable_metrics_tracking
        if self.enable_metrics_tracking:
            self.metrics_tracker = MetricsTracker()
            self.metrics_extractor = MetricsExtractor()
            self.session_start_time = None
            self.first_query_time = None
    
    def handle_message(self, user_input: str) -> str:
        """
        Handle a user message and return response
        
        Args:
            user_input: User's message
            
        Returns:
            Assistant's response
        """
        # Track metrics: start session if first message
        if self.enable_metrics_tracking and not self.session_start_time:
            session_id = f"session_{int(time.time())}"
            self.metrics_tracker.start_session(session_id)
            self.session_start_time = time.time()
            self.first_query_time = time.time()
        
        # Track metrics: record first query time
        if self.enable_metrics_tracking and self.first_query_time is None:
            self.first_query_time = time.time()
        
        # Update context
        self.context_manager.update_context(user_input)
        
        # Record response time start
        response_start_time = time.time()
        
        input_lower = user_input.lower()
        
        # If we have medical field, proceed directly to analysis (be proactive)
        if self.context_manager.has_sufficient_context() and not self.analysis_results:
            # Check if user explicitly doesn't want analysis yet
            if not any(word in input_lower for word in ["wait", "not yet", "don't", "no", "later"]):
                # Proceed with analysis immediately
                response = self._perform_analysis()
                if self.enable_metrics_tracking:
                    response_time = time.time() - response_start_time
                    self._track_response_metrics(response, response_time)
                return response
        
        # Handle special responses first
        if "all of them" in input_lower or "all" in input_lower:
            if self.context_manager.context.get("medical_field") and not self.analysis_results:
                # User wants analysis of all bias aspects
                self.context_manager.context["bias_aspects"] = ["all"]
                if self.context_manager.has_sufficient_context():
                    response = self._perform_analysis()
                    if self.enable_metrics_tracking:
                        response_time = time.time() - response_start_time
                        self._track_response_metrics(response, response_time)
                    return response
        
        # Check if we have sufficient context
        if not self.context_manager.has_sufficient_context():
            # Try to extract medical field using LLM if keyword matching failed
            if not self.context_manager.context.get("medical_field"):
                extracted = self._extract_medical_field_llm(user_input)
                if extracted:
                    self.context_manager.context["medical_field"] = extracted
                    # If we now have enough, proceed
                    if self.context_manager.has_sufficient_context():
                        response = self._perform_analysis()
                        if self.enable_metrics_tracking:
                            response_time = time.time() - response_start_time
                            self._track_response_metrics(response, response_time)
                        return response
            
            # Only ask one simple question if we really need it
            response = self._ask_for_medical_field_only()
            if self.enable_metrics_tracking:
                response_time = time.time() - response_start_time
                self._track_response_metrics(response, response_time)
            return response
        
        # Check if user is asking for analysis
        if self._is_analysis_request(user_input):
            response = self._perform_analysis()
            if self.enable_metrics_tracking:
                response_time = time.time() - response_start_time
                self._track_response_metrics(response, response_time)
            return response
        
        # Check for paper requests FIRST (before mitigation, since "address" might match both)
        if self.analysis_results:
            paper_phrases = ["show", "list", "provide", "give", "find", "recommend", "suggest", "share", "see"]
            paper_terms = ["paper", "study", "research", "citation", "publication", "article"]
            is_paper_request = (
                any(phrase in input_lower for phrase in paper_phrases) and 
                any(term in input_lower for term in paper_terms)
            ) or any(term in input_lower for term in ["papers", "studies", "research papers", "recent papers"])
            
            if is_paper_request:
                response = self._answer_about_papers()
                if self.enable_metrics_tracking:
                    response_time = time.time() - response_start_time
                    self._track_response_metrics(response, response_time)
                return response
        
        # Check if user is asking for mitigation methods
        if self._is_mitigation_request(user_input):
            response = self._provide_mitigation_recommendations()
            if self.enable_metrics_tracking:
                response_time = time.time() - response_start_time
                self._track_response_metrics(response, response_time)
            return response
        
        # Check if user is asking follow-up questions
        if self._is_follow_up(user_input):
            response = self._handle_follow_up(user_input)
            if self.enable_metrics_tracking:
                response_time = time.time() - response_start_time
                self._track_response_metrics(response, response_time)
            return response
        
        # Handle "yes" responses
        if input_lower in ["yes", "y", "yeah", "sure", "please"]:
            if "mitigation" in self.context_manager.conversation_history[-2].get("content", "").lower() if len(self.context_manager.conversation_history) > 1 else "":
                response = self._provide_mitigation_recommendations()
            elif self.analysis_results:
                response = self._provide_mitigation_recommendations()
            else:
                response = self._default_response()
            if self.enable_metrics_tracking:
                response_time = time.time() - response_start_time
                self._track_response_metrics(response, response_time)
            return response
        
        # Check if user is asking about specific topics (even if not a question)
        if self.analysis_results:
            input_lower = user_input.lower()
            # Check for papers first (more specific intent) - prioritize explicit paper requests
            paper_phrases = ["show", "list", "provide", "give", "find", "recommend", "suggest", "share", "see"]
            paper_terms = ["paper", "study", "research", "citation", "publication", "article"]
            
            is_paper_request = (
                any(phrase in input_lower for phrase in paper_phrases) and 
                any(term in input_lower for term in paper_terms)
            ) or (
                # Also catch if they just say "papers" or "studies" directly
                any(term in input_lower for term in ["papers", "studies", "research papers", "recent papers"])
            )
            
            if is_paper_request:
                response = self._answer_about_papers()
            elif any(term in input_lower for term in ["data imbalance", "data representation", "dataset"]):
                response = self._answer_about_data_imbalance()
            elif any(term in input_lower for term in ["performance", "subgroup", "gap"]):
                response = self._answer_about_performance()
            else:
                response = self._default_response()
            if self.enable_metrics_tracking:
                response_time = time.time() - response_start_time
                self._track_response_metrics(response, response_time)
            return response
        
        # Default: acknowledge and offer options
        response = self._default_response()
        
        # Track metrics: extract metrics from response
        if self.enable_metrics_tracking:
            response_time = time.time() - response_start_time
            self._track_response_metrics(response, response_time)
        
        return response
    
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
        input_lower = user_input.lower()
        
        # Exclude paper requests - if asking for papers, it's not an analysis request
        paper_terms = ["paper", "study", "research", "citation", "publication", "article"]
        paper_phrases = ["show", "list", "provide", "give", "find", "recommend", "suggest", "share", "see"]
        is_paper_request = (
            any(phrase in input_lower for phrase in paper_phrases) and 
            any(term in input_lower for term in paper_terms)
        ) or any(term in input_lower for term in ["papers", "studies", "research papers", "recent papers"])
        
        if is_paper_request:
            return False
        
        keywords = ["analyze", "find", "identify", "look at", "examine", "check", 
                   "help", "can you", "areas", "bias"]
        # Check if it's a question about bias/research areas
        if any(keyword in input_lower for keyword in ["bias", "areas", "under-explored"]):
            if any(qword in input_lower for qword in ["find", "identify", "help", "what", "where"]):
                return True
        # Check for "gaps" but only if not asking for papers
        if "gaps" in input_lower and not is_paper_request:
            if any(qword in input_lower for qword in ["find", "identify", "help", "what", "where", "analyze"]):
                return True
        return any(keyword in input_lower for keyword in keywords) and self.context_manager.has_sufficient_context()
    
    def _is_mitigation_request(self, user_input: str) -> bool:
        """Check if user is asking for mitigation methods"""
        input_lower = user_input.lower()
        
        # Exclude paper requests - if asking for papers, it's not a mitigation request
        paper_terms = ["paper", "study", "research", "citation", "publication", "article"]
        paper_phrases = ["show", "list", "provide", "give", "find", "recommend", "suggest", "share", "see"]
        is_paper_request = (
            any(phrase in input_lower for phrase in paper_phrases) and 
            any(term in input_lower for term in paper_terms)
        ) or any(term in input_lower for term in ["papers", "studies", "research papers", "recent papers"])
        
        if is_paper_request:
            return False
        
        keywords = ["mitigation", "method", "solution", "address", "reduce", "fix", "improve"]
        # Only match "address" if it's not part of a paper request
        if "address" in input_lower and not is_paper_request:
            # Check if "address" is used in context of papers/research
            if any(term in input_lower for term in ["paper", "study", "research", "that address"]):
                return False
        return any(keyword in user_input.lower() for keyword in keywords)
    
    def _is_follow_up(self, user_input: str) -> bool:
        """Check if user is asking a follow-up question"""
        input_lower = user_input.lower()
        keywords = ["what", "how", "why", "when", "where", "can you", "show me", "tell me", 
                   "can we", "talk about", "tell me about", "explain", "more about", 
                   "what about", "discuss", "elaborate"]
        # Check if starts with keyword or contains follow-up phrases
        starts_with_keyword = any(input_lower.startswith(keyword) for keyword in keywords)
        contains_followup = any(phrase in input_lower for phrase in ["talk more", "more about", "tell me more", "can we talk"])
        return starts_with_keyword or contains_followup
    
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
        
        # If we have analysis results, use them to answer the question
        if self.analysis_results:
            # Check for papers first (more specific intent) - prioritize explicit paper requests
            # Check for phrases that explicitly request papers
            paper_phrases = ["show", "list", "provide", "give", "find", "recommend", "suggest", "share", "see"]
            paper_terms = ["paper", "study", "research", "citation", "publication", "article"]
            
            is_paper_request = (
                any(phrase in input_lower for phrase in paper_phrases) and 
                any(term in input_lower for term in paper_terms)
            ) or (
                # Also catch if they just say "papers" or "studies" directly
                any(term in input_lower for term in ["papers", "studies", "research papers", "recent papers"])
            )
            
            if is_paper_request:
                return self._answer_about_papers()
            
            # Check for specific topics they might be asking about
            if any(term in input_lower for term in ["data imbalance", "data representation", "dataset", "race label"]):
                return self._answer_about_data_imbalance()
            
            # Check for performance/gap - but only if NOT asking for papers
            if not any(term in input_lower for term in paper_terms):
                if any(term in input_lower for term in ["performance", "subgroup", "accuracy", "gap"]):
                    return self._answer_about_performance()
            
            if any(term in input_lower for term in ["mitigation", "fairness", "method", "solution"]):
                return self._provide_mitigation_recommendations()
        
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
        
        # Final fallback: Use LLM to generate contextual response with analysis results
        # But first, double-check if this is a paper request that we missed
        paper_phrases = ["show", "list", "provide", "give", "find", "recommend", "suggest", "share", "see"]
        paper_terms = ["paper", "study", "research", "citation", "publication", "article"]
        is_paper_request = (
            any(phrase in input_lower for phrase in paper_phrases) and 
            any(term in input_lower for term in paper_terms)
        ) or any(term in input_lower for term in ["papers", "studies", "research papers", "recent papers"])
        
        if is_paper_request and self.analysis_results:
            return self._answer_about_papers()
        
        conversation_summary = self.context_manager.get_conversation_summary()
        
        # Include analysis results in the prompt if available
        analysis_context = ""
        if self.analysis_results:
            import json
            analysis_context = f"""
Previous Analysis Results:
- Scope: {self.analysis_results.get('scope', 'N/A')}
- Bias Score: {self.analysis_results.get('score_results', {}).get('score', 'N/A')}
- Key Findings: {json.dumps(self.analysis_results.get('score_results', {}).get('drivers', []), indent=2)}
- Dataset Summary: {json.dumps(self.analysis_results.get('dataset_analysis', {}).get('summary', {}), indent=2)}
"""
        
        prompt = f"""Based on this conversation about racial bias in medical AI research:

{conversation_summary}
{analysis_context}

User question: {user_input}

Provide a helpful, detailed response based on the analysis results above. Reference specific findings, numbers, and data from the analysis. If the user is asking about:
- Data imbalance: Explain the dataset composition issues found
- Performance gaps: Explain subgroup performance disparities
- Mitigation methods: Provide specific recommendations
- Papers: Reference the papers found in the analysis

Keep responses conversational, informative, and grounded in the actual analysis data."""

        response = self.llm_client.generate_response(prompt, temperature=0.7)
        self.context_manager.add_assistant_response(response)
        return response
    
    def _answer_about_data_imbalance(self) -> str:
        """Provide detailed answer about data imbalance from analysis"""
        if not self.analysis_results:
            return "I need to perform an analysis first. What medical field would you like me to analyze?"
        
        dataset_analysis = self.analysis_results.get("dataset_analysis", {})
        summary = dataset_analysis.get("summary", {})
        score_results = self.analysis_results.get("score_results", {})
        
        total = summary.get("total_datasets", 0)
        with_labels = summary.get("datasets_with_race_labels", 0)
        dark_skin_prop = summary.get("avg_dark_skin_proportion", 0.0)
        minority_rep = summary.get("avg_minority_representation", 0.0)
        
        import json
        prompt = f"""Based on the analysis of {self.analysis_results.get('scope', 'medical AI')}, provide a detailed explanation about data imbalance issues found.

Analysis Data:
- Total datasets analyzed: {total}
- Datasets with race labels: {with_labels}
- Average dark skin proportion: {dark_skin_prop*100:.1f}% (target: 25%)
- Average minority representation: {minority_rep*100:.1f}% (target: 25%)
- Bias score breakdown: {json.dumps(score_results.get('breakdown', {}), indent=2)}

Explain:
1. What data imbalance means in this context
2. Specific issues found in the analysis
3. Why this matters for racial bias
4. How it affects model performance

Be specific, reference the numbers, and make it informative."""
        
        response = self.llm_client.generate_response(prompt, temperature=0.7)
        self.context_manager.add_assistant_response(response)
        return response
    
    def _answer_about_performance(self) -> str:
        """Provide detailed answer about performance gaps from analysis"""
        if not self.analysis_results:
            return "I need to perform an analysis first. What medical field would you like me to analyze?"
        
        subgroup_analysis = self.analysis_results.get("subgroup_analysis", {})
        summary = subgroup_analysis.get("summary", {})
        
        total = summary.get("total_studies", 0)
        with_metrics = summary.get("studies_with_subgroup_metrics", 0)
        avg_gap = summary.get("avg_performance_gap", 0.0)
        
        import json
        prompt = f"""Based on the analysis of {self.analysis_results.get('scope', 'medical AI')}, provide a detailed explanation about performance gaps between different racial/ethnic groups.

Analysis Data:
- Total studies analyzed: {total}
- Studies reporting subgroup metrics: {with_metrics}
- Average performance gap: {avg_gap*100:.1f}%
- Common gaps: {json.dumps(summary.get('common_gaps', []), indent=2)}

Explain:
1. What performance gaps mean in medical AI
2. Specific disparities found in the analysis
3. Why these gaps occur
4. Impact on patient outcomes

Be specific, reference the numbers, and make it informative."""
        
        response = self.llm_client.generate_response(prompt, temperature=0.7)
        self.context_manager.add_assistant_response(response)
        return response
    
    def _answer_about_papers(self) -> str:
        """Provide information about papers from analysis"""
        if not self.analysis_results:
            return "I need to perform an analysis first. What medical field would you like me to analyze?"
        
        scope = self.context_manager.get_scope()
        years = self.context_manager.get_time_range()
        
        # Collect papers from all analyses
        all_papers = []
        for analysis_type in ["dataset_analysis", "subgroup_analysis", "mitigation_analysis"]:
            analysis = self.analysis_results.get(analysis_type, {})
            papers = analysis.get("real_papers", [])
            all_papers.extend(papers[:5])  # Top 5 from each
        
        if all_papers:
            # Format found papers
            papers_text = "\n".join([
                f"- {p.get('title', 'Unknown')} ({p.get('year', 'N/A')}) - {p.get('url', 'No URL')}"
                for p in all_papers[:10]
            ])
            response = f"Based on my analysis of {scope}, here are relevant papers I found:\n\n{papers_text}\n\nWould you like more details about any specific aspect of the analysis?"
        else:
            # Use LLM to suggest relevant papers based on the analysis
            score_results = self.analysis_results.get("score_results", {})
            drivers = score_results.get("drivers", [])
            
            import json
            analysis_summary = {
                "scope": scope,
                "years": years,
                "drivers": drivers,
                "bias_score": score_results.get("score", 0.0),
                "dataset_summary": self.analysis_results.get("dataset_analysis", {}).get("summary", {}),
                "subgroup_summary": self.analysis_results.get("subgroup_analysis", {}).get("summary", {}),
                "mitigation_summary": self.analysis_results.get("mitigation_analysis", {}).get("summary", {})
            }
            
            papers_prompt = f"""Based on the bias analysis of {scope} research from the past {years} years, suggest 3-5 relevant recent papers that address racial bias gaps, fairness, or mitigation methods in this field.

Analysis Findings:
{json.dumps(analysis_summary, indent=2)}

The main bias issues identified are:
{', '.join(drivers) if drivers else 'General racial bias concerns'}

Provide paper suggestions that:
1. Address the specific bias gaps found (e.g., dataset diversity, subgroup performance, fairness methods)
2. Are recent (published in the past 5 years)
3. Are relevant to {scope}

Format as a list with:
- Paper title
- Brief description of how it addresses the identified gaps
- Year (if known)

Be specific about which bias issues each paper addresses."""
            
            papers_suggestions = self.llm_client.generate_response(papers_prompt, temperature=0.7)
            response = f"Based on my analysis of {scope} research, here are papers that address the identified bias gaps:\n\n{papers_suggestions}\n\nWould you like more details about any specific aspect of the analysis?"
        
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
    
    def _track_response_metrics(self, response: str, response_time: float):
        """Track metrics from LLM response without changing conversation behavior"""
        if not self.enable_metrics_tracking:
            return
        
        # Record response time
        self.metrics_tracker.record_response_time(response_time)
        
        # Extract claims with citations
        claims = self.metrics_extractor.extract_claims_with_citations(response)
        for claim_data in claims:
            is_verified = self.metrics_extractor.check_claim_verification(
                claim_data["claim"], claim_data.get("citations", [])
            )
            self.metrics_tracker.record_claim(
                claim_data["claim"],
                claim_data["has_citation"],
                is_verified
            )
        
        # Extract gaps
        gaps = self.metrics_extractor.extract_gaps(response, self.analysis_results)
        for gap_data in gaps:
            self.metrics_tracker.record_gap(
                gap_data["description"],
                gap_data["flags_demographic"],
                gap_data["flags_geographic"],
                gap_data["has_sources"]
            )
    
    def end_session(self) -> Dict[str, Any]:
        """End the current session and return metrics"""
        if self.enable_metrics_tracking:
            return self.metrics_tracker.end_session()
        return {}
    
    def get_metrics_history(self) -> List[Dict[str, Any]]:
        """Get all metrics history"""
        if self.enable_metrics_tracking:
            return self.metrics_tracker.metrics_history
        return []

