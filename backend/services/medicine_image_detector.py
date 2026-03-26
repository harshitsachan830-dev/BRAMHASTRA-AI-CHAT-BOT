import base64
from google import genai
from google.genai import types
from backend.config import GEMINI_API_KEY, GEMINI_MODEL
from backend.services.symptom_analyzer import get_medicine_info
from backend.services.llm_engine import ask_ai


def detect_medicine_from_image(image_data: str) -> dict:
    try:
        if not GEMINI_API_KEY:
            return {
                "type": "vision",
                "title": "Medicine Image Detection",
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
Identify the medicine name visible in this image.

Rules:
- Return only the most likely medicine name
- If no medicine name is clearly visible, return only: unknown
- Do not explain anything
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

        medicine_name = (response.text or "").strip().lower()
        original_name = medicine_name

        if not medicine_name or "unknown" in medicine_name:
            return {
                "type": "vision",
                "title": "Medicine Image Detection",
                "answer": "Could not clearly identify the medicine from the image.",
                "risk_level": "Unknown",
                "health_score": 60,
                "explanation": "Image text was unclear or medicine could not be recognized.",
                "next_steps": [
                    "Capture a clearer image.",
                    "Keep only the medicine strip or bottle in frame.",
                    "Ensure the medicine name is visible."
                ]
            }

        # First try database/FDA
        med_response = get_medicine_info(medicine_name)

        if "not found" not in med_response.get("answer", "").lower():
            med_response["title"] = f"Detected Medicine: {original_name.title()}"
            med_response["explanation"] = (
                med_response.get("explanation", "") +
                f" | Medicine detected from image as '{original_name}'."
            )
            return med_response

        # If database doesn't have it, try AI fallback
        ai_result = ask_ai(
            f"What is {original_name} medicine used for? "
            f"Give short structured answer with uses, precautions, side effects, and when to see a doctor.",
            mode="health"
        )

        if ai_result.get("success"):
            return {
                "type": "vision_ai_fallback",
                "title": f"Detected Medicine: {original_name.title()}",
                "answer": ai_result["answer"],
                "risk_level": "AI Generated",
                "health_score": 65,
                "explanation": (
                    f"Medicine detected from image as '{original_name}'. "
                    "FDA/database match not found, so AI-generated explanation was used."
                ),
                "next_steps": [
                    "Verify the medicine name on the strip or box.",
                    "Consult a pharmacist or doctor before use.",
                    "Do not rely only on AI for dosage or serious conditions."
                ]
            }

        return {
            "type": "vision",
            "title": f"Detected Medicine: {original_name.title()}",
            "answer": "Medicine was detected, but complete information could not be retrieved.",
            "risk_level": "Unknown",
            "health_score": 55,
            "explanation": "Detection succeeded but information retrieval failed.",
            "next_steps": [
                "Try again with a clearer image.",
                "Search by generic name if available.",
                "Consult a doctor or pharmacist."
            ]
        }

    except Exception as e:
        error_text = str(e).lower()

        if "resource_exhausted" in error_text or "quota" in error_text or "429" in error_text:
            return {
                "type": "vision",
                "title": "Medicine Image Detection",
                "answer": "Image scan is temporarily unavailable because the AI API request limit has been reached.",
                "risk_level": "Unknown",
                "health_score": 50,
                "explanation": "Gemini API quota exceeded. Please try again later or enter the medicine name manually.",
                "next_steps": [
                    "Wait a few minutes and try again.",
                    "Type the medicine name manually in the text box.",
                    "Use another API key if available."
                ]
            }

        return {
            "type": "vision",
            "title": "Medicine Image Detection",
            "answer": "Error while detecting medicine from image.",
            "risk_level": "Unknown",
            "health_score": 50,
            "explanation": "An unexpected error occurred during image analysis.",
            "next_steps": [
                "Try again with a clearer image.",
                "Make sure the medicine name is visible.",
                "Enter the medicine name manually if needed."
            ]
        }