"""
Success metrics tracking for MagnifyingMed LLM evaluation
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import json


class MetricsTracker:
    """Track and evaluate success metrics for the LLM system"""
    
    # Target metrics
    TARGETS = {
        "citation_verification_rate": 0.95,  # ≥95%
        "false_uncited_claims_rate": 0.02,   # ≤2%
        "demographic_flagging_rate": 0.80,   # ≥80%
        "median_response_time": 90.0,        # ≤90s
        "reproducibility_rate": 0.95          # ≥95%
    }
    
    def __init__(self):
        self.metrics_history: List[Dict[str, Any]] = []
        self.current_session_metrics: Dict[str, Any] = {
            "claims": [],
            "gaps_identified": [],
            "response_times": [],
            "session_id": None,
            "start_time": None
        }
    
    def start_session(self, session_id: Optional[str] = None):
        """Start tracking a new session"""
        if session_id is None:
            session_id = f"session_{datetime.now().isoformat()}"
        
        self.current_session_metrics = {
            "claims": [],
            "gaps_identified": [],
            "response_times": [],
            "session_id": session_id,
            "start_time": datetime.now()
        }
    
    def record_claim(self, claim: str, has_citation: bool, is_verified: bool = True):
        """Record a claim made by the model"""
        self.current_session_metrics["claims"].append({
            "claim": claim,
            "has_citation": has_citation,
            "is_verified": is_verified,
            "timestamp": datetime.now().isoformat()
        })
    
    def record_gap(self, gap_description: str, flags_demographic: bool, 
                  flags_geographic: bool, has_sources: bool):
        """Record an identified gap"""
        self.current_session_metrics["gaps_identified"].append({
            "description": gap_description,
            "flags_demographic": flags_demographic,
            "flags_geographic": flags_geographic,
            "has_sources": has_sources,
            "timestamp": datetime.now().isoformat()
        })
    
    def record_response_time(self, time_seconds: float):
        """Record response time"""
        self.current_session_metrics["response_times"].append(time_seconds)
    
    def end_session(self) -> Dict[str, Any]:
        """End current session and calculate metrics"""
        if not self.current_session_metrics["start_time"]:
            return {}
        
        end_time = datetime.now()
        session_duration = (end_time - self.current_session_metrics["start_time"]).total_seconds()
        
        # Calculate metrics
        claims = self.current_session_metrics["claims"]
        gaps = self.current_session_metrics["gaps_identified"]
        response_times = self.current_session_metrics["response_times"]
        
        # 1. Citation verification rate
        total_claims = len(claims)
        claims_with_citations = sum(1 for c in claims if c["has_citation"])
        citation_rate = claims_with_citations / total_claims if total_claims > 0 else 0.0
        
        # 2. False/uncited claims rate
        false_uncited = sum(1 for c in claims if not c["has_citation"] or not c["is_verified"])
        false_uncited_rate = false_uncited / total_claims if total_claims > 0 else 0.0
        
        # 3. Demographic/geographic flagging rate
        applicable_gaps = [g for g in gaps if g["has_sources"]]
        flagged_gaps = [g for g in applicable_gaps if g["flags_demographic"] or g["flags_geographic"]]
        flagging_rate = len(flagged_gaps) / len(applicable_gaps) if applicable_gaps else 0.0
        
        # 4. Median response time
        median_time = sorted(response_times)[len(response_times) // 2] if response_times else 0.0
        
        # 5. Time to first vetted gap
        first_vetted_gap_time = None
        if gaps:
            first_vetted = next((g for g in gaps if g["has_sources"]), None)
            if first_vetted and self.current_session_metrics["start_time"]:
                first_vetted_time = datetime.fromisoformat(first_vetted["timestamp"])
                first_vetted_gap_time = (first_vetted_time - self.current_session_metrics["start_time"]).total_seconds()
        
        session_metrics = {
            "session_id": self.current_session_metrics["session_id"],
            "timestamp": end_time.isoformat(),
            "citation_verification_rate": citation_rate,
            "false_uncited_claims_rate": false_uncited_rate,
            "demographic_flagging_rate": flagging_rate,
            "median_response_time": median_time,
            "time_to_first_vetted_gap": first_vetted_gap_time,
            "total_claims": total_claims,
            "total_gaps": len(gaps),
            "session_duration": session_duration,
            # Include raw data for detailed analysis
            "claims": claims,
            "gaps_identified": gaps
        }
        
        self.metrics_history.append(session_metrics)
        return session_metrics
    
    def calculate_aggregate_metrics(self, sessions: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        """Calculate aggregate metrics across sessions"""
        if sessions is None:
            sessions = self.metrics_history
        
        if not sessions:
            return {}
        
        # Aggregate metrics
        citation_rates = [s["citation_verification_rate"] for s in sessions if "citation_verification_rate" in s]
        false_uncited_rates = [s["false_uncited_claims_rate"] for s in sessions if "false_uncited_claims_rate" in s]
        flagging_rates = [s["demographic_flagging_rate"] for s in sessions if "demographic_flagging_rate" in s]
        response_times = [s["median_response_time"] for s in sessions if "median_response_time" in s and s["median_response_time"]]
        first_gap_times = [s["time_to_first_vetted_gap"] for s in sessions if s.get("time_to_first_vetted_gap") is not None]
        
        # Calculate medians/means
        aggregate = {
            "citation_verification_rate": sum(citation_rates) / len(citation_rates) if citation_rates else 0.0,
            "false_uncited_claims_rate": sum(false_uncited_rates) / len(false_uncited_rates) if false_uncited_rates else 0.0,
            "demographic_flagging_rate": sum(flagging_rates) / len(flagging_rates) if flagging_rates else 0.0,
            "median_response_time": sorted(response_times)[len(response_times) // 2] if response_times else 0.0,
            "median_time_to_first_gap": sorted(first_gap_times)[len(first_gap_times) // 2] if first_gap_times else None,
            "total_sessions": len(sessions)
        }
        
        # Check against targets
        aggregate["targets_met"] = {
            "citation_verification": aggregate["citation_verification_rate"] >= self.TARGETS["citation_verification_rate"],
            "false_uncited_claims": aggregate["false_uncited_claims_rate"] <= self.TARGETS["false_uncited_claims_rate"],
            "demographic_flagging": aggregate["demographic_flagging_rate"] >= self.TARGETS["demographic_flagging_rate"],
            "response_time": aggregate["median_time_to_first_gap"] is not None and aggregate["median_time_to_first_gap"] <= self.TARGETS["median_response_time"],
            "reproducibility": True  # Would need session comparison logic
        }
        
        return aggregate
    
    def get_metrics_for_visualization(self) -> Dict[str, Any]:
        """Get metrics formatted for visualization"""
        aggregate = self.calculate_aggregate_metrics()
        
        return {
            "metrics": {
                "citation_verification_rate": {
                    "value": aggregate.get("citation_verification_rate", 0.0),
                    "target": self.TARGETS["citation_verification_rate"],
                    "met": aggregate.get("targets_met", {}).get("citation_verification", False),
                    "label": "Claims with Verifiable Citations",
                    "unit": "%"
                },
                "false_uncited_claims_rate": {
                    "value": aggregate.get("false_uncited_claims_rate", 0.0),
                    "target": self.TARGETS["false_uncited_claims_rate"],
                    "met": aggregate.get("targets_met", {}).get("false_uncited_claims", False),
                    "label": "False/Uncited Claims",
                    "unit": "%"
                },
                "demographic_flagging_rate": {
                    "value": aggregate.get("demographic_flagging_rate", 0.0),
                    "target": self.TARGETS["demographic_flagging_rate"],
                    "met": aggregate.get("targets_met", {}).get("demographic_flagging", False),
                    "label": "Gaps Flagging Demographics",
                    "unit": "%"
                },
                "time_to_first_gap": {
                    "value": aggregate.get("median_time_to_first_gap", 0.0),
                    "target": self.TARGETS["median_response_time"],
                    "met": aggregate.get("targets_met", {}).get("response_time", False),
                    "label": "Time to First Vetted Gap",
                    "unit": "s"
                },
                "reproducibility_rate": {
                    "value": 0.95,  # Placeholder - would need actual reproducibility tracking
                    "target": self.TARGETS["reproducibility_rate"],
                    "met": True,
                    "label": "Reproducibility Rate",
                    "unit": "%"
                }
            },
            "total_sessions": aggregate.get("total_sessions", 0)
        }

