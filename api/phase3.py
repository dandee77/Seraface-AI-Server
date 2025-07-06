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
    """
Generates a budget allocation based on user profile and skincare concerns.
The budget is divided into four tiers based on the user's total budget:
    Tier	     Priority	                    Description
    🟢 Tier 1	Core Essentials	                Cleanser, Moisturizer, Sunscreen
    🟡 Tier 2	First Add-ons	                Treatment, Toner, Serum, Spot Treatment
    🟠 Tier 3	Specialized Boosters	        Eye Cream, Essence, Ampoule, Exfoliants
    🔵 Tier 4	Occasional / Luxury	            Masks, Face Mist, Facial Oil, Neck Cream, Lip Care
    """
    model = genai.GenerativeModel("gemini-2.0-flash")

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


# TODO: ADD ATTR: "REASON WHY" TO PRODUCT RECOMMENDATIONS
# ------------------------------
# Step 2: Product Recommendation Prompt
# ------------------------------
def get_product_recommendations(
    category: str,
    category_budget: float,
    form_data: FormData,
    skin_analysis: Optional[SkinAnalysis] = None
) -> List[dict]:
    model = genai.GenerativeModel("gemini-2.0-flash")

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
# ! REMOVED: PRIORITY INDEXES, IDK IF THEY ARE EVEN NEEDED NGL
def get_future_recommendations(
    form_data: FormData,
    current_categories: List[str],
    skin_analysis: Optional[SkinAnalysis] = None,
) -> List[dict]:
    model = genai.GenerativeModel("gemini-2.0-flash")

    # ? Convert budget string (e.g., "$25") to float
    numeric_budget = float(form_data.budget.replace("$", "").strip())

    prompt = f"""
You are a skincare assistant helping a user expand their skincare routine *gradually*.

User Profile:
- Skin Type: {', '.join(form_data.skin_type)}
- Skin Conditions: {', '.join(form_data.skin_conditions)}
- Goals: {', '.join(form_data.goals + ([form_data.custom_goal] if form_data.custom_goal else []))}
- Allergies: {', '.join(form_data.allergies)}
- Budget Tier: {"Low" if numeric_budget <= 30 else "Medium" if numeric_budget <= 80 else "High"}

Current routine already includes the following categories:
- {', '.join(current_categories)}

Instructions:
1. Suggest 2 to 4 product **categories** the user can consider next, based on their goals and needs.
2. The new categories must NOT include or duplicate the current ones.
3. Each suggestion must include:
   - "category" (e.g., "serum", "clay_mask", "eye_cream")
   - One example product with:
       - "name"
       - "price" (in USD like "$12")

4. Output a valid JSON array of objects like:
[
  {{
    "category": "serum",
    "products": [{{ "name": "Product", "price": "$X" }}]
  }},
  ...
]

5. Do NOT include explanations, notes, or markdown — only valid JSON output.
"""

    if skin_analysis:
        prompt += f"\n\nSkin Analysis:\n{skin_analysis.model_dump_json(indent=2)}"

    try:
        response = model.generate_content(prompt)
        raw = getattr(response, 'text', '').strip()
        print("🧪 Raw Future Recommendations:\n", raw)

        if raw.startswith("```"):
            raw = raw.strip("`").strip()
            if raw.startswith("json"):
                raw = raw[4:].strip()

        parsed = json.loads(raw)
        return parsed

    except Exception as e:
        print("❌ Failed to parse future recommendations:", e)
        raise HTTPException(status_code=500, detail="Failed to generate future recommendations")


# NOTE TO MY DEMENTIA AHH SELF: No more budget_remaining + total_cost calculations here. As it will be based on the user's choice of products.
# ------------------------------  
# Main API Route for Phase 3
# ------------------------------
@router.post("/budget-distribution")
def budget_distribution(data: dict):
    try:
        form_data = FormData(**data.get("form_data"))
        skin_analysis_data = data.get("skin_analysis")
        skin_analysis = SkinAnalysis(**skin_analysis_data) if skin_analysis_data else None

        # Step 1: Budget allocation
        allocation = get_budget_allocation(form_data)

        # Step 2: Convert total budget
        total_budget = float(form_data.budget.replace("$", "").strip())

        # Step 3: Generate product recommendations
        product_results = {}
        product_categories = list(allocation.keys())

        for category, percent in allocation.items():
            category_budget = round((percent / 100) * total_budget, 2)
            print(f"🧮 Budget for {category}: ${category_budget}")
            products = get_product_recommendations(category, category_budget, form_data, skin_analysis)
            product_results[category] = products

        # Step 4: Generate future recommendations
        future = get_future_recommendations(
            form_data,
            current_categories=product_categories,
            skin_analysis=skin_analysis
        )

        print("categories:", product_categories)

        return {
            "allocation": allocation,
            "products": product_results,
            "total_budget": f"${total_budget}",
            "future_recommendations": future
        }

    except Exception as e:
        print("❌ Error in /phase3/budget-distribution:", str(e))
        raise HTTPException(status_code=500, detail="Failed to complete budget distribution phase")
