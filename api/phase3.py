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
