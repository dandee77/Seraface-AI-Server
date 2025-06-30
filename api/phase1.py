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

@router.post("/submitform")
def submit_form(data: FormData):
    # Simulate saving to memory (will later send this later to Phase 2)
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
