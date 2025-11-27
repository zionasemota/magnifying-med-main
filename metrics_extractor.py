"""
Metrics extractor for analyzing LLM responses to track claims, citations, gaps, etc.
"""

import re
import json
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime


class MetricsExtractor:
    """Extract metrics from LLM responses without changing conversation behavior"""
    
    def __init__(self):
        # Patterns for detecting citations
        self.citation_patterns = [
            r'\[(\d+)\]',  # [1], [2], etc.
            r'\([A-Za-z]+ et al\.?, \d{4}\)',  # (Smith et al., 2020)
            r'\([A-Za-z]+, \d{4}\)',  # (Smith, 2020)
            r'doi:\s*10\.\d+[/.][^\s]+',  # doi:10.1234/...
            r'https?://[^\s]+',  # URLs
            r'arXiv:\d+\.\d+',  # arXiv IDs
            r'PMID:\s*\d+',  # PubMed IDs
        ]
        
        # Patterns for detecting claims (sentences with factual statements)
        self.claim_patterns = [
            r'[A-Z][^.!?]*[.!?]',  # Complete sentences
        ]
        
        # Keywords for demographic/geographic flagging
        self.demographic_keywords = [
            'demographic', 'race', 'racial', 'ethnic', 'ethnicity', 'minority',
            'african american', 'black', 'hispanic', 'latino', 'asian', 'white',
            'under-represented', 'underrepresented', 'demographic gap',
            'population bias', 'demographic bias'
        ]
        
        self.geographic_keywords = [
            'geographic', 'geographical', 'region', 'country', 'continent',
            'US-only', 'US only', 'United States', 'Europe', 'Asia', 'Africa',
            'geographic gap', 'geographical gap', 'geographic bias',
            'location bias', 'regional', 'global', 'international'
        ]
    
    def extract_claims_with_citations(self, text: str) -> List[Dict[str, Any]]:
        """Extract claims and check if they have citations"""
        claims = []
        
        # Split text into sentences
        sentences = re.split(r'[.!?]+', text)
        
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) < 20:  # Skip very short fragments
                continue
            
            # Check if sentence contains a claim (has some factual content)
            if not self._is_claim(sentence):
                continue
            
            # Check for citations
            has_citation = self._has_citation(sentence)
            citations = self._extract_citations(sentence)
            
            claims.append({
                "claim": sentence,
                "has_citation": has_citation,
                "citations": citations,
                "is_verified": has_citation,  # Will be checked later if needed
            })
        
        return claims
    
    def extract_gaps(self, text: str, analysis_results: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Extract identified gaps and check for demographic/geographic flagging"""
        gaps = []
        
        # Look for gap-related keywords
        gap_keywords = [
            'gap', 'lack', 'missing', 'insufficient', 'under-represented',
            'underrepresented', 'bias', 'disparity', 'inequality', 'limitation'
        ]
        
        # Split into sentences
        sentences = re.split(r'[.!?]+', text)
        
        for sentence in sentences:
            sentence = sentence.strip()
            
            # Check if sentence mentions a gap
            if not any(keyword in sentence.lower() for keyword in gap_keywords):
                continue
            
            # Check for demographic/geographic flagging
            flags_demographic = self._flags_demographic(sentence)
            flags_geographic = self._flags_geographic(sentence)
            
            # Check if gap has sources (citations)
            has_sources = self._has_citation(sentence)
            sources = self._extract_citations(sentence) if has_sources else []
            
            # Also check if gap appears in analysis results
            if analysis_results:
                has_sources = has_sources or self._gap_in_analysis_results(sentence, analysis_results)
            
            gaps.append({
                "description": sentence,
                "flags_demographic": flags_demographic,
                "flags_geographic": flags_geographic,
                "has_sources": has_sources,
                "sources": sources,
            })
        
        return gaps
    
    def check_claim_verification(self, claim: str, citations: List[str]) -> bool:
        """Check if a claim with citations is verifiable"""
        if not citations:
            return False
        
        # Simple heuristic: if it has citations, consider it verifiable
        # In practice, this could be enhanced to actually verify citations
        return len(citations) > 0
    
    def _is_claim(self, text: str) -> bool:
        """Check if text contains a factual claim"""
        # Exclude questions, greetings, etc.
        question_words = ['what', 'how', 'why', 'when', 'where', 'can you', 'would you']
        if any(text.lower().startswith(word) for word in question_words):
            return False
        
        # Should have some factual content (numbers, specific terms, etc.)
        has_factual_content = (
            bool(re.search(r'\d+', text)) or  # Contains numbers
            len(text.split()) > 5  # Or is a substantial statement
        )
        
        return has_factual_content
    
    def _has_citation(self, text: str) -> bool:
        """Check if text contains citations"""
        for pattern in self.citation_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        return False
    
    def _extract_citations(self, text: str) -> List[str]:
        """Extract all citations from text"""
        citations = []
        
        for pattern in self.citation_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            citations.extend(matches)
        
        return citations
    
    def _flags_demographic(self, text: str) -> bool:
        """Check if text flags demographic under-representation"""
        text_lower = text.lower()
        return any(keyword in text_lower for keyword in self.demographic_keywords)
    
    def _flags_geographic(self, text: str) -> bool:
        """Check if text flags geographic under-representation"""
        text_lower = text.lower()
        return any(keyword in text_lower for keyword in self.geographic_keywords)
    
    def _gap_in_analysis_results(self, gap_text: str, analysis_results: Dict[str, Any]) -> bool:
        """Check if gap is mentioned in analysis results (has sources)"""
        # Check dataset analysis
        if 'dataset_analysis' in analysis_results:
            dataset_summary = analysis_results['dataset_analysis'].get('summary', {})
            if dataset_summary.get('total_datasets', 0) > 0:
                return True
        
        # Check subgroup analysis
        if 'subgroup_analysis' in analysis_results:
            subgroup_summary = analysis_results['subgroup_analysis'].get('summary', {})
            if subgroup_summary.get('total_studies', 0) > 0:
                return True
        
        # Check mitigation analysis
        if 'mitigation_analysis' in analysis_results:
            mitigation_summary = analysis_results['mitigation_analysis'].get('summary', {})
            if mitigation_summary.get('total_studies', 0) > 0:
                return True
        
        return False

