from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Optional, Literal
import google.generativeai as genai
import os
from dotenv import load_dotenv
import json

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

router = APIRouter()


class RoutineStep(BaseModel):
    name: str
    tag: str
    description: str
    instructions: List[str]
    duration: int
    waiting_time: int
    days: Dict[str, bool]
    time: List[str]

class RoutineResponse(BaseModel):
    product_type: str
    routine: List[RoutineStep]

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
    

# TODO: PASS FACE ANALYSIS DATA
# ------------------------------
# Step 4: Routine Creation Prompt
# ------------------------------
def get_routine_for_user(form_data: FormData, product_recommendations: dict) -> dict:
    model = genai.GenerativeModel("gemini-1.5-flash")

    user_profile = f"""
    User Profile:
    - Skin Type: {', '.join(form_data.skin_type)}
    - Skin Conditions: {', '.join(form_data.skin_conditions)}
    - Allergies: {', '.join(form_data.allergies)}
    - Product Experiences: {[f"{p.product} ({p.experience})" for p in form_data.product_experiences]}
    - Goals: {', '.join(form_data.goals + ([form_data.custom_goal] if form_data.custom_goal else []))}
    """

    prompt = f"""
    You are a skincare assistant creating a personalized skincare routine for a user.

    User Profile:
    {user_profile}

    Products:
    {json.dumps(product_recommendations, indent=2)}

    Instructions:
    - For each product, create a step-by-step usage instruction.
    - Provide a brief description (e.g., 'Gentle Hydrating Cleanser: Ideal for daily use, removes dirt and impurities').
    - Include days for usage (e.g., 'monday', 'tuesday', 'wednesday', etc.).
    - Specify the time(s) of use in an array (e.g., ["morning", "night"] if it is used twice a day).
    - Provide the duration in seconds (e.g., 30 for cleanser).
    - Provide the waiting time in seconds between products (e.g., 900 for waiting 15 minutes).
    - Only provide the raw JSON without markdown or extra commentary.

    Example:
    "cleanser": {{
        "name": "CeraVe Renewing SA Cleanser",
        "tag": "Gentle Hydrating Cleanser",
        "description": "Ideal for daily use, removes dirt and impurities",
        "instructions": [
            "Wet face with lukewarm water.",
            "Apply a small amount to face and neck.",
            "Massage in circular motions.",
            "Rinse thoroughly."
        ],
        "duration": 30,
        "waiting_time": 900,
        "days": {{
            "monday": true,
            "tuesday": true,
            "wednesday": true,
            "thursday": true,
            "friday": true,
            "saturday": true,
            "sunday": true
        }},
        "time": ["morning"]
    }},
    "moisturizer": {{
        "name": "Neutrogena Hydro Boost Water Gel",
        "tag": "Hyaluronic Acid Moisturizer",
        "description": "Hydrates and replenishes moisture",
        "instructions": [
            "Take a small amount and gently apply to face and neck.",
            "Massage in upward circular motions."
        ],
        "duration": 20,
        "waiting_time": 600,
        "days": {{
            "monday": true,
            "tuesday": true,
            "wednesday": true,
            "thursday": true,
            "friday": true,
            "saturday": true,
            "sunday": true
        }},
        "time": ["morning", "night"]
    }}
    """

    try:
        response = model.generate_content(prompt)
        raw = getattr(response, 'text', '').strip()

        if raw.startswith("```"):
            raw = raw.strip("`").strip()
            if raw.startswith("json"):
                raw = raw[4:].strip()

        print("🧪 Raw Response:", raw)

        if not raw:
            raise ValueError("Received an empty response from the AI model.")

        routine = json.loads(raw) 
        return routine

    except Exception as e:
        print("❌ Failed to generate skincare routine:", e)
        raise HTTPException(status_code=500, detail="Failed to create skincare routine")


# ------------------------------
# API Route for Phase 4: Routine Creation
# ------------------------------
@router.post("/routine-creation")
def create_routine(data: dict):
    try:
        form_data = FormData(**data.get("form_data", {}))
        product_recommendations = data.get("product_recommendations", {})

        if not product_recommendations:
            raise HTTPException(status_code=400, detail="No product recommendations provided")


        routine = get_routine_for_user(form_data, product_recommendations)

        if isinstance(routine, dict):
            routine_list = list(routine.values())
        else:
            routine_list = routine

        return RoutineResponse(product_type="custom", routine=routine_list)

    except Exception as e:
        print("❌ Error in /phase4/routine-creation:", str(e))
        raise HTTPException(status_code=500, detail="Failed to create skincare routine")
