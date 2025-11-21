"""
Context manager for tracking conversation state and gathering required information
"""

from typing import Dict, Any, Optional, List
from .config import REQUIRED_CONTEXT_FIELDS


class ContextManager:
    """Manages conversation context and tracks missing information"""
    
    def __init__(self):
        self.context: Dict[str, Any] = {
            "medical_field": None,
            "specific_condition": None,
            "time_range": None,
            "bias_aspects": []
        }
        self.conversation_history: List[Dict[str, str]] = []
    
    def update_context(self, user_input: str, extracted_info: Optional[Dict[str, Any]] = None):
        """
        Update context from user input and optional extracted information
        
        Args:
            user_input: User's message
            extracted_info: Optional dictionary with structured information
        """
        self.conversation_history.append({"role": "user", "content": user_input})
        
        if extracted_info:
            # Update context with extracted information
            if "medical_field" in extracted_info:
                self.context["medical_field"] = extracted_info["medical_field"]
            if "condition" in extracted_info or "specific_condition" in extracted_info:
                self.context["specific_condition"] = extracted_info.get("condition") or extracted_info.get("specific_condition")
            if "time_range" in extracted_info or "years" in extracted_info:
                self.context["time_range"] = extracted_info.get("time_range") or extracted_info.get("years")
            if "bias_aspects" in extracted_info:
                self.context["bias_aspects"] = extracted_info["bias_aspects"]
        
        # Try to extract from user input if not provided
        self._extract_from_input(user_input)
    
    def _extract_from_input(self, user_input: str):
        """Extract context information from user input using keyword matching"""
        input_lower = user_input.lower()
        
        # Extract medical field (expanded list)
        if not self.context["medical_field"]:
            fields = {
                "dermatology": ["dermatology", "skin", "melanoma", "acne", "eczema", "dermatological", "skin cancer"],
                "cardiology": ["cardiology", "heart", "cardiovascular", "ecg", "troponin", "cardiac"],
                "radiology": ["radiology", "x-ray", "xray", "ct scan", "mri", "imaging", "radiographic"],
                "oncology": ["oncology", "cancer", "tumor", "tumour", "malignancy"],
                "pulmonology": ["pulmonology", "lung", "pneumonia", "respiratory", "pulmonary"],
                "ophthalmology": ["ophthalmology", "eye", "retinal", "retina", "diabetic retinopathy"],
                "pathology": ["pathology", "histopathology", "biopsy"]
            }
            
            for field, keywords in fields.items():
                if any(keyword in input_lower for keyword in keywords):
                    self.context["medical_field"] = field
                    break
        
        # Extract condition (expanded)
        if not self.context["specific_condition"]:
            conditions = {
                "melanoma": ["melanoma", "skin cancer"],
                "heart disease": ["heart disease", "cardiovascular disease", "cardiac", "heart failure"],
                "pneumonia": ["pneumonia", "lung infection"],
                "acne": ["acne"],
                "eczema": ["eczema", "atopic dermatitis"],
                "diabetic retinopathy": ["diabetic retinopathy", "retinopathy"]
            }
            
            for condition, keywords in conditions.items():
                if any(keyword in input_lower for keyword in keywords):
                    self.context["specific_condition"] = condition
                    break
        
        # Extract time range (more flexible)
        if not self.context["time_range"]:
            if any(x in input_lower for x in ["5 years", "past 5", "last 5", "5 year"]):
                self.context["time_range"] = 5
            elif any(x in input_lower for x in ["3 years", "past 3", "last 3", "3 year"]):
                self.context["time_range"] = 3
            elif any(x in input_lower for x in ["10 years", "past 10", "last 10", "10 year"]):
                self.context["time_range"] = 10
            elif any(x in input_lower for x in ["recent", "latest", "current"]):
                self.context["time_range"] = 3  # Default to recent = 3 years
        
        # Extract bias aspects
        if "data imbalance" in input_lower or "data representation" in input_lower:
            if "data imbalance" not in self.context["bias_aspects"]:
                self.context["bias_aspects"].append("data imbalance")
        if "diagnostic bias" in input_lower:
            if "diagnostic bias" not in self.context["bias_aspects"]:
                self.context["bias_aspects"].append("diagnostic bias")
        if "performance" in input_lower and "gap" in input_lower:
            if "performance gaps" not in self.context["bias_aspects"]:
                self.context["bias_aspects"].append("performance gaps")
    
    def get_missing_fields(self) -> List[str]:
        """
        Get list of missing required context fields
        
        Returns:
            List of missing field names
        """
        missing = []
        
        if not self.context["medical_field"]:
            missing.append("medical_field")
        if not self.context["specific_condition"]:
            missing.append("specific_condition")
        if not self.context["time_range"]:
            missing.append("time_range")
        
        return missing
    
    def has_sufficient_context(self) -> bool:
        """
        Check if we have sufficient context to proceed with analysis
        Only requires medical_field - other fields can be inferred/defaulted
        
        Returns:
            True if sufficient context is available
        """
        # Only require medical_field - we can proceed with just that
        return self.context["medical_field"] is not None
    
    def get_scope(self) -> str:
        """
        Get the scope string for analysis (combination of field and condition)
        
        Returns:
            Scope string
        """
        parts = []
        if self.context["medical_field"]:
            parts.append(self.context["medical_field"])
        if self.context["specific_condition"]:
            parts.append(self.context["specific_condition"])
        
        if not parts:
            return "medical AI"
        
        return " ".join(parts)
    
    def get_time_range(self) -> int:
        """
        Get time range in years (defaults to 5 if not specified)
        
        Returns:
            Number of years
        """
        return self.context["time_range"] or 5
    
    def add_assistant_response(self, response: str):
        """Add assistant response to conversation history"""
        self.conversation_history.append({"role": "assistant", "content": response})
    
    def get_conversation_summary(self) -> str:
        """Get a summary of the conversation for context"""
        if not self.conversation_history:
            return ""
        
        summary_parts = []
        for msg in self.conversation_history[-6:]:  # Last 6 messages
            role = msg["role"]
            content = msg["content"][:200]  # Truncate long messages
            summary_parts.append(f"{role}: {content}")
        
        return "\n".join(summary_parts)

