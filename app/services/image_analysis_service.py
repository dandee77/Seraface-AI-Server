"""
Phase 2 Service: Image Analysis

Handles facial image analysis using AI for skin condition assessment.
PRESERVED ORIGINAL LOGIC - Only extracted into service class.
"""

import re
import json
import io
from PIL import Image
from fastapi import HTTPException
from fastapi.responses import JSONResponse
import google.generativeai as genai
from ..core.config import settings

# Configure the AI model (same as original)
genai.configure(api_key=settings.GEMINI_API_KEY)


class Phase2Service:
    """Service for Phase 2: Image Analysis (Original logic preserved)"""
    
    @staticmethod
    def clean_response(text: str) -> str:
        """Clean Gemini Response Text - ORIGINAL LOGIC PRESERVED"""
        text = text.replace("`", "").replace(""", '"').replace(""", '"').replace("'", "'").strip()
        text = re.sub(r'^\s*```[a-zA-Z]*', '', text, flags=re.MULTILINE)
        text = re.sub(r'```\s*$', '', text, flags=re.MULTILINE)
        return text

    @staticmethod
    def analyze_face_image(image: Image.Image):
        """Analyze face image - ORIGINAL LOGIC PRESERVED"""
        model = genai.GenerativeModel(model_name="gemini-2.0-flash")

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
            cleaned = Phase2Service.clean_response(response.text)

            result = json.loads(re.search(r"\{.*\}", cleaned, re.DOTALL).group())

            return result

        except Exception as e:
            print(f"[Gemini Error] {e}")
            raise HTTPException(status_code=500, detail=f"Gemini parsing error: {e}")

    @staticmethod
    async def analyze_face(file_bytes: bytes) -> JSONResponse:
        """
        Analyze a face image using Gemini 1.5 Flash.
        Accepts image bytes and returns structured analysis data.
        - file_bytes: The image file bytes to analyze.
        - Returns a JSON response with the analysis results.
        
        ORIGINAL LOGIC PRESERVED
        """
        try:
            image = Image.open(io.BytesIO(file_bytes)).convert("RGB")
            ai_result = Phase2Service.analyze_face_image(image)

            return JSONResponse(content={
                "message": "Face analyzed using Gemini 1.5 Flash",
                "ai_output": ai_result
            })

        except Exception as e:
            return JSONResponse(content={"error": str(e)}, status_code=500)


# Global instance
phase2_service = Phase2Service()
