# phase2.py
from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from typing import Dict
import uuid
import os

router = APIRouter()

# ------- Directory Setup -------- #
UPLOAD_FOLDER = "uploaded_faces"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# ------- Route for Face Analysis -------- #
"""
Analyze a user's facial image to provide skincare insights.
This endpoint accepts an image file, saves it, and simulates an AI analysis
to return skincare-related data.
"""
@router.post("/analyze-face")
async def analyze_face(image: UploadFile = File(...)) -> Dict:
   
    ext = image.filename.split(".")[-1]
    image_filename = f"{uuid.uuid4()}.{ext}"
    image_path = os.path.join(UPLOAD_FOLDER, image_filename)

    with open(image_path, "wb") as f:
        f.write(await image.read())

    prompt = f"""
You are a skincare AI. Analyze the user's facial image located at: {image_path}

Return the following data in JSON format:
- redness_irritation
- acne_breakouts (severity, count, location)
- blackheads_whiteheads (presence, location)
- oiliness_shine (level, location)
- dryness_flaking (presence, location)
- uneven_skin_tone
- dark_spots_scars (presence, description)
- pores_size (level, location)
- hormonal_acne_signs
- stress_related_flareups
- dehydrated_skin_signs
- fine_lines_wrinkles (presence, areas)
- skin_elasticity
"""

    mock_ai_output = {
        "redness_irritation": "moderate",
        "acne_breakouts": {
            "severity": "mild",
            "count_estimate": 5,
            "location": ["cheeks", "chin"]
        },
        "blackheads_whiteheads": {
            "presence": True,
            "location": ["nose", "chin"]
        },
        "oiliness_shine": {
            "level": "medium",
            "location": ["T-zone"]
        },
        "dryness_flaking": {
            "presence": True,
            "location": ["cheeks"]
        },
        "uneven_skin_tone": "moderate",
        "dark_spots_scars": {
            "presence": True,
            "description": "Post-acne marks visible on cheeks"
        },
        "pores_size": {
            "level": "large",
            "location": ["nose", "cheeks"]
        },
        "hormonal_acne_signs": "uncertain",
        "stress_related_flareups": "yes",
        "dehydrated_skin_signs": "yes",
        "fine_lines_wrinkles": {
            "presence": False,
            "areas": []
        },
        "skin_elasticity": "average"
    }

    print("=== AI Prompt Sent ===")
    print(prompt)

    return {
        "message": "Face scanned successfully",
        "image_path": image_path,
        "ai_output": mock_ai_output
    }
