from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Optional, Literal

router = APIRouter()

# ------- Pydantic Models -------- #

class ProductExperience(BaseModel):
    brand: str
    experience: Literal["good", "bad", "neutral"]
    reason: Optional[str] = None

class FormData(BaseModel):
    skin_type: List[Literal["oily", "dry", "combination", "normal", "sensitive", "acne-prone"]]
    skin_conditions: List[str]
    allergies: List[str]
    product_experiences: List[ProductExperience]
    goals: List[str]
    custom_goal: Optional[str] = None

# ------- In-memory Storage (mock for now) -------- #

submitted_forms = []

# ------- Route -------- #
"""
This endpoint allows users to submit their skincare form data.
It accepts various skin-related information and stores it in memory.
This is a mock implementation for Phase 1, which will later be sent to Phase 3.
"""
@router.post("/submitform")
def submit_form(data: FormData):
    # Simulate saving to memory (will later send this later to Phase 3
    submitted_forms.append(data)

    return {
        "message": "Form submitted successfully",
        "form_index": len(submitted_forms) - 1,
        "stored_data": data
    }

# ? debug endpoint to list submissions
@router.get("/forms")
def list_forms():
    return submitted_forms
