from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Literal, Optional, Dict
import google.generativeai as genai
import os
import json
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

router = APIRouter()

# ------------------------------
# Models
# ------------------------------
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


class SkinAnalysis(BaseModel):
    redness_irritation: Optional[str]
    acne_breakouts: Optional[dict]
    blackheads_whiteheads: Optional[dict]
    oiliness_shine: Optional[dict]
    dryness_flaking: Optional[dict]
    uneven_skin_tone: Optional[str]
    dark_spots_scars: Optional[dict]
    pores_size: Optional[dict]
    hormonal_acne_signs: Optional[str]
    stress_related_flareups: Optional[str]
    dehydrated_skin_signs: Optional[str]
    fine_lines_wrinkles: Optional[dict]
    skin_elasticity: Optional[str]


# ------------------------------
# Step 1: Budget Distribution Prompt
# ------------------------------
def get_budget_allocation(form_data: FormData) -> dict:
    model = genai.GenerativeModel("gemini-1.5-flash")

    # ? Converts budget string (e.g., "$25") to float
    try:
        budget_value = float(form_data.budget.replace("$", "").strip())
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid budget format.")

    # ? selects allowed categories based on budget
    allowed_categories = []
    if budget_value <= 15:
        allowed_categories = ["facial_wash", "moisturizer"]
    elif budget_value <= 30:
        allowed_categories = ["facial_wash", "moisturizer", "sunscreen", "treatment"]
    elif budget_value <= 60:
        allowed_categories = ["facial_wash", "moisturizer", "sunscreen", "treatment", "toner", "serum"]
    else:
        allowed_categories = [
            "facial_wash", "moisturizer", "sunscreen", "treatment", "toner",
            "serum", "eye_cream", "exfoliant", "mask", "essence", "ampoule"
        ]

    # Format for the prompt
    categories_str = ", ".join(allowed_categories)

    prompt = f"""
You are a skincare budget planning assistant. Based on the user's profile and skincare concerns, allocate their total skincare budget into percentage per product category.

Only use from the following allowed categories (based on budget): {categories_str}

User Profile:
- Skin Type: {', '.join(form_data.skin_type)}
- Skin Conditions: {', '.join(form_data.skin_conditions)}
- Allergies: {', '.join(form_data.allergies)}
- Product Experiences: {[f"{p.product} ({p.experience})" for p in form_data.product_experiences]}
- Goals: {', '.join(form_data.goals + ([form_data.custom_goal] if form_data.custom_goal else []))}
- Budget: {form_data.budget}

Instructions:
- Output a valid JSON object with keys as category names (e.g., facial_wash, moisturizer, sunscreen).
- The values must be raw numbers (not strings), and they must sum up to 100.
- Do NOT include notes, explanations, or markdown — return pure JSON only.
"""

    try:
        response = model.generate_content(prompt)
        raw = getattr(response, 'text', '').strip()

        print("🧪 Raw Budget Response:\n", raw)

        if raw.startswith("```"):
            raw = raw.strip("`").strip()
            if raw.startswith("json"):
                raw = raw[4:].strip()

        parsed = json.loads(raw)
        print("💰 Budget Allocation:", parsed)
        return parsed
    except Exception as e:
        print("❌ Failed to parse budget allocation:", e)
        raise HTTPException(status_code=500, detail="Failed to parse budget allocation")



# ------------------------------
# Step 2: Product Recommendation Prompt
# ------------------------------
def get_product_recommendations(
    category: str,
    category_budget: float,
    form_data: FormData,
    skin_analysis: Optional[SkinAnalysis] = None
) -> List[dict]:
    model = genai.GenerativeModel("gemini-1.5-flash")

    prompt = f"""
You are a skincare product recommendation assistant.

Instructions:
- Recommend exactly 2 to 3 product options for the category: "{category}".
- The **price of each recommended products must not exceed this amount: ${category_budget}**.
- Recommend products that match their skin type, goals, allergies, and product experience.
- Return a valid JSON list of objects with "name" and "price" (e.g., "$10").
- Do NOT include notes, markdown, or explanations — return raw JSON only.

User Profile:
- Skin Type: {', '.join(form_data.skin_type)}
- Skin Conditions: {', '.join(form_data.skin_conditions)}
- Allergies: {', '.join(form_data.allergies)}
- Product Experiences: {[f"{p.product} ({p.experience})" for p in form_data.product_experiences]}
- Goals: {', '.join(form_data.goals + ([form_data.custom_goal] if form_data.custom_goal else []))}
"""

    if skin_analysis:
        prompt += f"\n\nAdditional Skin Analysis:\n{skin_analysis.model_dump_json(indent=2)}"

    try:
        response = model.generate_content(prompt)
        raw = getattr(response, 'text', '').strip()

        print(f"📦 Raw Response for {category}:\n", raw)

        if raw.startswith("```"):
            raw = raw.strip("`").strip()
            if raw.startswith("json"):
                raw = raw[4:].strip()

        parsed = json.loads(raw)
        return parsed

    except Exception as e:
        print("❌ Failed to parse product recommendation:", e)
        raise HTTPException(status_code=500, detail=f"Failed to generate product list for {category}")

# TODO: ADD FUTURE RECOMMENDATIONS PROMPT 3

# ------------------------------  
# Main API Route for Phase 3
# ------------------------------
@router.post("/budget-distribution")
def budget_distribution(data: dict):
    try:
        form_data = FormData(**data.get("form_data"))
        skin_analysis_data = data.get("skin_analysis")
        skin_analysis = SkinAnalysis(**skin_analysis_data) if skin_analysis_data else None

        # Step 1: Get allocation percentages
        allocation = get_budget_allocation(form_data)

        # Convert budget string to float
        raw_budget = form_data.budget.replace("$", "").strip()
        try:
            total_budget = float(raw_budget)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid budget format")

        # Step 2: Calculate per-category dollar budget
        product_results = {}
        for i, (category, percent) in enumerate(allocation.items()):
            category_budget = round((percent / 100) * total_budget, 2)
            print(f"🧮 Budget for {category}: ${category_budget}")
            products = get_product_recommendations(category, category_budget, form_data, skin_analysis)
            product_results[category] = products

        return {
            "allocation": allocation,
            "products": product_results
        }

    except Exception as e:
        print("❌ Error in /phase3/budget-distribution:", str(e))
        raise HTTPException(status_code=500, detail="Failed to complete budget distribution phase")
