from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, validator
from dotenv import load_dotenv
import google.generativeai as genai
import os
import json
import re
from typing import List, Dict, Optional

router = APIRouter()

# === Load API Key ===
load_dotenv()
GOOGLE_API_KEY = os.getenv("GEMINI_API_KEY")
if not GOOGLE_API_KEY:
    raise RuntimeError("GEMINI_API_KEY not found in environment variables")

genai.configure(api_key=GOOGLE_API_KEY)


# === 1st Prompt ===
def build_budget_distribution_prompt(form_data: Dict) -> str:
    prompt = f"""
You are a skincare planning assistant. Your task is to create a personalized budget allocation plan for skincare categories based on a user's skincare profile and total budget.

Here is the user's profile:
- Skin Type: {', '.join(form_data['skin_type'])}
- Skin Conditions: {', '.join(form_data['skin_conditions'])}
- Allergies: {', '.join(form_data['allergies'])}
- Previous Product Experiences: {', '.join([f"{exp['product']} ({exp['experience']})" for exp in form_data['product_experiences']])}
- Goals: {', '.join(form_data['goals'])}
- Custom Goal: {form_data.get('custom_goal', 'None')}
- Total Budget: {form_data['budget']}

Your job is to decide how much percentage of the budget should be allocated to each product category. You must prioritize essential categories first (e.g., facial wash, moisturizer, sunscreen) and then distribute the remaining percentage to secondary categories (like toner, treatment serum, night cream, etc.) only if necessary.

Output your answer in valid JSON format like this:
{{
  "facial_wash": 25,
  "moisturizer": 25,
  "sunscreen": 25,
  "treatment": 15,
  "toner": 10
}}

The total should always equal 100. Return only valid JSON.
"""
    return prompt


# === 2nd Prompt ===
def build_product_recommendation_prompt(category: str, allocated_amount: float, form_data: Dict, skin_analysis: Dict) -> str:
    prompt = f"""
You are a skincare expert AI. Your task is to recommend up to 3 suitable skincare products in the category of "{category}" for a user based on their skin profile and face analysis results.

The user has a budget of ${allocated_amount:.2f} for this category.

User Profile:
- Skin Type: {', '.join(form_data['skin_type'])}
- Skin Conditions: {', '.join(form_data['skin_conditions'])}
- Allergies: {', '.join(form_data['allergies'])}
- Product Experiences: {', '.join([f"{exp['product']} ({exp['experience']})" for exp in form_data['product_experiences']])}
- Goals: {', '.join(form_data['goals'])}
- Custom Goal: {form_data.get('custom_goal', 'None')}

Face Scan Analysis:
- Redness/Irritation: {skin_analysis['redness_irritation']}
- Uneven Skin Tone: {skin_analysis['uneven_skin_tone']}
- Hormonal Acne Signs: {skin_analysis['hormonal_acne_signs']}
- Stress-Related Flare-Ups: {skin_analysis['stress_related_flareups']}
- Dehydrated Skin Signs: {skin_analysis['dehydrated_skin_signs']}
- Skin Elasticity: {skin_analysis['skin_elasticity']}

Product-specific observations:
- Acne Breakouts: {skin_analysis['acne_breakouts']}
- Blackheads/Whiteheads: {skin_analysis['blackheads_whiteheads']}
- Oiliness/Shine: {skin_analysis['oiliness_shine']}
- Dryness/Flaking: {skin_analysis['dryness_flaking']}
- Dark Spots/Scars: {skin_analysis['dark_spots_scars']}
- Pores Size: {skin_analysis['pores_size']}
- Fine Lines/Wrinkles: {skin_analysis['fine_lines_wrinkles']}

Please recommend up to 3 products in this category that match the user's needs and do not exceed the ${allocated_amount:.2f} limit. Return only a valid JSON list in this format:
[
  {{"name": "Product Name", "price": "$XX.XX", "importance_rank": 1}},
  {{"name": "Product Name", "price": "$XX.XX", "importance_rank": 2}},
  ...
]

Return only valid JSON. No explanations, notes, or markdown.
"""
    return prompt




