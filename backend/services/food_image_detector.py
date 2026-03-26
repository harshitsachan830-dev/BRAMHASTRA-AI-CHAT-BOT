import base64
from google import genai
from google.genai import types
from backend.config import GEMINI_API_KEY, GEMINI_MODEL


def detect_food_from_image(image_data: str) -> dict:
    try:
        if not GEMINI_API_KEY:
            return {
                "type": "food",
                "title": "Food Image Analysis",
                "answer": "Gemini API key missing.",
                "risk_level": "Unknown",
                "health_score": 50,
                "explanation": "No Gemini API key found.",
                "next_steps": ["Add GEMINI_API_KEY in .env"]
            }

        if "," in image_data:
            image_data = image_data.split(",", 1)[1]

        image_bytes = base64.b64decode(image_data)

        client = genai.Client(api_key=GEMINI_API_KEY)

        prompt = """
Look at this food image and respond in this exact format:

Food Name:
Estimated Ingredients:
Estimated Calories:
Protein:
Carbs:
Fat:
Food Type: Healthy / Moderate / Junk
Can I Eat It Regularly:
Who Should Avoid It:
Health Advice:
Short Verdict:

Keep it practical and short.
If the image is unclear, say that clearly.
"""

        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=[
                prompt,
                types.Part.from_bytes(
                    data=image_bytes,
                    mime_type="image/jpeg"
                )
            ]
        )

        answer = (response.text or "").strip()
        answer_lower = answer.lower()

        risk_level = "Moderate"
        health_score = 65

        if "junk" in answer_lower or "avoid" in answer_lower:
            risk_level = "High"
            health_score = 40
        elif "healthy" in answer_lower:
            risk_level = "Low"
            health_score = 85

        return {
            "type": "food",
            "title": "Food Image Analysis",
            "answer": answer,
            "risk_level": risk_level,
            "health_score": health_score,
            "explanation": "AI-generated nutrition and food-health analysis from uploaded image.",
            "next_steps": [
                "Check portion size before eating.",
                "Prefer fresh and balanced meals.",
                "Consult a nutritionist if you have diabetes, obesity, or heart disease."
            ],
            "doctor_recommendation": {
                "specialist": "Dietitian / Nutritionist" if risk_level != "Low" else "General Healthy Diet",
                "urgency": "Low" if risk_level == "Low" else "Moderate",
                "action": "Take moderation seriously and prefer healthier alternatives." if risk_level != "Low" else "This food appears generally okay in moderation."
            }
        }

    except Exception as e:
        error_text = str(e).lower()

        if "resource_exhausted" in error_text or "quota" in error_text or "429" in error_text:
            return {
                "type": "food",
                "title": "Food Image Analysis",
                "answer": "Food image scan is temporarily unavailable because the AI API request limit has been reached.",
                "risk_level": "Unknown",
                "health_score": 50,
                "explanation": "Gemini API quota exceeded. Please try again later.",
                "next_steps": [
                    "Wait a few minutes and try again.",
                    "Upload a clearer image later.",
                    "Use another API key if available."
                ]
            }

        return {
            "type": "food",
            "title": "Food Image Analysis",
            "answer": "Error while analyzing food image.",
            "risk_level": "Unknown",
            "health_score": 50,
            "explanation": "An unexpected error occurred during food image analysis.",
            "next_steps": [
                "Try again with a clearer image.",
                "Keep only the food item in frame."
            ]
        }