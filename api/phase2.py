from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from PIL import Image
import io
import google.generativeai as genai
from dotenv import load_dotenv
import os
import re
import json

router = APIRouter()

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise RuntimeError("GEMINI_API_KEY not found in environment variables")

genai.configure(api_key=GEMINI_API_KEY)

# === Clean Gemini Response Text ===
def clean_response(text: str) -> str:
    text = text.replace("`", "").replace("“", '"').replace("”", '"').replace("’", "'").strip()
    text = re.sub(r'^\s*```[a-zA-Z]*', '', text, flags=re.MULTILINE)
    text = re.sub(r'```\s*$', '', text, flags=re.MULTILINE)
    return text


def analyze_face_image(image: Image.Image):
    model = genai.GenerativeModel(model_name="gemini-1.5-flash")

    prompt = """
You are a skincare AI.

Analyze the face image and return the following structured data in JSON format:

{
  "redness_irritation": "none | mild | moderate | severe",
  "acne_breakouts": {
    "severity": "none | mild | moderate | severe",
    "count_estimate": number,
    "location": ["forehead", "cheeks", "chin", etc.]
  },
  "blackheads_whiteheads": {
    "presence": true | false,
    "location": [areas]
  },
  "oiliness_shine": {
    "level": "low | medium | high",
    "location": [areas]
  },
  "dryness_flaking": {
    "presence": true | false,
    "location": [areas]
  },
  "uneven_skin_tone": "none | mild | moderate | severe",
  "dark_spots_scars": {
    "presence": true | false,
    "description": "short summary"
  },
  "pores_size": {
    "level": "small | medium | large",
    "location": [areas]
  },
  "hormonal_acne_signs": "yes | no | uncertain",
  "stress_related_flareups": "yes | no",
  "dehydrated_skin_signs": "yes | no",
  "fine_lines_wrinkles": {
    "presence": true | false,
    "areas": [areas]
  },
  "skin_elasticity": "low | average | high"
}

Only respond with the valid JSON object.
"""

    try:
        response = model.generate_content([prompt, image])
        cleaned = clean_response(response.text)

        result = json.loads(re.search(r"\{.*\}", cleaned, re.DOTALL).group())

        return result

    except Exception as e:
        print(f"[Gemini Error] {e}")
        raise HTTPException(status_code=500, detail=f"Gemini parsing error: {e}")

# === API Endpoint ===
@router.post("/analyze-face")
async def analyze_face(file: UploadFile = File(...)):
    try:

        image_bytes = await file.read()
        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")

    
        ai_result = analyze_face_image(image)

        return JSONResponse(content={
            "message": "Face analyzed using Gemini 1.5 Flash",
            "ai_output": ai_result
        })

    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)
