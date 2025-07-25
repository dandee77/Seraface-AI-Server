from typing import List, Optional, Literal
from pydantic import BaseModel


class ProductExperience(BaseModel):
    product: str
    experience: Literal["good", "bad", "neutral"]
    reason: Optional[str] = None


class FormData(BaseModel):
    skin_type: List[Literal["oily", "dry", "combination", "normal", "sensitive", "acne-prone"]]
    skin_conditions: List[str]
    budget: str
    allergies: List[str]
    product_experiences: List[ProductExperience]
    goals: List[str]
    custom_goal: Optional[str] = None
