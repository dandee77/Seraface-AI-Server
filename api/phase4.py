from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Optional
import google.generativeai as genai
import os
from dotenv import load_dotenv
from phase1 import FormData, ProductExperience
import json

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

router = APIRouter()

class ProductRecommendation(BaseModel):
    name: str
    price: str
    priority_index: int

class RoutineStep(BaseModel):
    name: str
    description: str
    instructions: List[str]
    duration: str
    waiting_time: str
    time_of_use: str
    days_of_use: Dict[str, bool]  # E.g., Monday, Tuesday, etc.

class RoutineResponse(BaseModel):
    product_type: str
    routine: List[RoutineStep]
    

# TODO: PASS FACE ANALYSIS DATA
# ------------------------------
# Step 4: Routine Creation Prompt
# ------------------------------
def get_routine_for_user(form_data: FormData, product_recommendations: dict) -> dict:
    model = genai.GenerativeModel("gemini-1.5-flash")

    user_profile = f"""
    Skin Type: {', '.join(form_data.skin_type)}
    Skin Conditions: {', '.join(form_data.skin_conditions)}
    Goals: {', '.join(form_data.goals + ([form_data.custom_goal] if form_data.custom_goal else []))}
    Allergies: {', '.join(form_data.allergies)}
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
        routine = json.loads(response.text.strip())
        return routine
    except Exception as e:
        print("❌ Failed to generate skincare routine:", e)
        raise HTTPException(status_code=500, detail="Failed to create skincare routine")



# ------------------------------
# API Route for Phase 4: Routine Creation
# ------------------------------
@router.post("/phase4/routine-creation")
def create_routine(data: dict):
    try:
        form_data = FormData(**data.get("form_data"))
        product_recommendations = data.get("product_recommendations")

        # Generate the routine creation prompt
        prompt = get_routine_for_user(form_data, product_recommendations)

        # Call the Gemini AI model to generate the routine
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(prompt)

        # Parse the response and return
        routine = json.loads(response.text)
        return {"routine": routine}

    except Exception as e:
        print("❌ Error in /phase4/routine-creation:", str(e))
        raise HTTPException(status_code=500, detail="Failed to create skincare routine")
