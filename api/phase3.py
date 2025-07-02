# phase3.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
import google.generativeai as genai
import os
import json
import re

router = APIRouter()

# === Load API Key ===
load_dotenv()
GOOGLE_API_KEY = os.getenv("GEMINI_API_KEY")
if not GOOGLE_API_KEY:
    raise RuntimeError("GEMINI_API_KEY not found in environment variables")

genai.configure(api_key=GOOGLE_API_KEY)

# === Phase 1 & 2 Inputs ===
class ProductExperience(BaseModel):
    product: str
    experience: str

class FormData(BaseModel):
    skin_type: list[str]
    skin_conditions: list[str]
    budget: str
    allergies: list[str]
    product_experiences: list[ProductExperience]
    goals: list[str]
    custom_goal: str | None = None

class SkinAnalysis(BaseModel):
    redness_irritation: str
    acne_breakouts: dict
    blackheads_whiteheads: dict
    oiliness_shine: dict
    dryness_flaking: dict
    uneven_skin_tone: str
    dark_spots_scars: dict
    pores_size: dict
    hormonal_acne_signs: str
    stress_related_flareups: str
    dehydrated_skin_signs: str
    fine_lines_wrinkles: dict
    skin_elasticity: str

class Phase3Request(BaseModel):
    form_data: FormData
    skin_analysis: SkinAnalysis

# === Prompt Builder ===
def build_prompt(form_data: FormData, skin_analysis: SkinAnalysis) -> str:
    experience_str = ", ".join([f"{p.product} ({p.experience})" for p in form_data.product_experiences])

    prompt = f"""
You are a professional AI skincare consultant.

User profile:
- Skin type: {', '.join(form_data.skin_type)}
- Skin conditions: {', '.join(form_data.skin_conditions)}
- Budget: {form_data.budget} (assume this is in USD)
- Allergies: {', '.join(form_data.allergies)}
- Product experiences: {experience_str}
- Skincare goals: {', '.join(form_data.goals)}
"""
    if form_data.custom_goal:
        prompt += f"- Additional goals: {form_data.custom_goal}\n"

    prompt += f"""

Skin Analysis Results:
{json.dumps(skin_analysis.dict(), indent=2)}

---

TASK:
You are to recommend a full skincare routine based on the user’s profile and needs. You must:

1. Prioritize products by importance: facial wash > treatment > moisturizer > sunscreen > serum > toner > night cream > eye cream > etc.
2. MAXIMIZE the budget but do NOT exceed it. Ensure total cost <= budget.
3. Product prices are in USD. Calculate the total cost and remaining budget precisely.
4. If budget is too low, include only the essentials and defer additional products as `future_recommendations`.
5. `future_recommendations` must contain at least TWO categories (e.g., serum, toner) if budget allows only the essentials.
6. DO NOT deduct the cost of future recommendations from the budget.
7. Do NOT include notes, explanations, or markdown. Only return structured JSON.

Format the response as:

{{
  "facial_wash": [{{"name": "Product", "price": "$X", "priority_index": 0}}],
  "treatment": [{{...}}],
  "moisturizer": [{{...}}],
  ...
  "future_recommendations": [
    {{"toner": [{{"name": "Product", "price": "$X", "priority_index": N}}]}},
    {{"serum": [{{"name": "Product", "price": "$X", "priority_index": N+1}}]}}
  ],
  "total_cost": "$XX",
  "remaining_budget": "$YY"
}}

Return only valid JSON with no extra formatting or text.
"""
    return prompt

# === Clean and Parse Gemini Response ===
def parse_gemini_response(text: str):
    try:
        text = re.sub(r"```[a-zA-Z]*", "", text).strip()
        json_data = json.loads(text)
        return json_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to parse response: {e}")

# === Endpoint ===
@router.post("/phase3/recommend")
async def phase3_recommend(data: Phase3Request):
    model = genai.GenerativeModel("gemini-1.5-flash")
    prompt = build_prompt(data.form_data, data.skin_analysis)

    try:
        response = model.generate_content(prompt)
        print("RAW GEMINI RESPONSE:\n", response.text)
        result = parse_gemini_response(response.text)
        return result
    except Exception as e:
        print("Error parsing Gemini response:", e)
        raise HTTPException(status_code=500, detail=str(e))
