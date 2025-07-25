"""
Phase 1 Service: Form Processing

Handles user form data collection and validation for skincare analysis.
PRESERVED ORIGINAL LOGIC - Only extracted into service class.
"""

from typing import List, Dict, Any
from ..models.skincare.form_schemas import FormData


class Phase1Service:
    """Service for Phase 1: Form Processing (Original logic preserved)"""
    
    def __init__(self):
        # In-memory storage (same as original)
        self.submitted_forms = []
    
    def submit_form(self, data: FormData) -> Dict[str, Any]:
        """
        Endpoint to submit a skincare form.
        Accepts structured data about skin type, conditions, allergies, product experiences, and goals.
        - data: The structured form data to submit.
        - Returns a success message with the index of the stored form and the data.
        
        ORIGINAL LOGIC PRESERVED
        """
        self.submitted_forms.append(data)

        return {
            "message": "Form submitted successfully",
            "form_index": len(self.submitted_forms) - 1,
            "stored_data": data
        }
    
    def list_forms(self) -> List[FormData]:
        """
        Endpoint to list all submitted forms.
        Returns a list of all submitted forms.
        
        ORIGINAL LOGIC PRESERVED
        """
        return self.submitted_forms


# Global instance to maintain state
phase1_service = Phase1Service()
