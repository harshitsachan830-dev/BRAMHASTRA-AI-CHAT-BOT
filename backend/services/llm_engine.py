from google import genai
from backend.config import GEMINI_API_KEY, GEMINI_MODEL


def ask_ai(question: str, mode: str = "general") -> dict:
    if not GEMINI_API_KEY:
        return {
            "success": False,
            "answer": "Gemini API key is missing. Please add it in the .env file."
        }

    if mode == "health":
        system_prompt = """
You are SwasthyaAI Ultra, a safe health assistant.

Rules:
- Give educational guidance only
- Do not give a final diagnosis
- Do not prescribe prescription medicines
- Keep answer short, practical, and structured
- Use simple English

Always respond in this exact format:

Overview:
- brief summary

Possible causes:
- point 1
- point 2
- point 3

Precautions:
- point 1
- point 2
- point 3

Red flags:
- point 1
- point 2

When to see a doctor:
- point 1
- point 2
"""
    else:
        system_prompt = """
You are a helpful assistant.
Answer clearly and briefly.
Keep the answer concise and easy to understand.
"""

    try:
        client = genai.Client(api_key=GEMINI_API_KEY)
        full_prompt = f"{system_prompt}\n\nUser question: {question}"

        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=full_prompt
        )

        return {
            "success": True,
            "answer": response.text.strip()
        }

    except Exception as e:
        return {
            "success": False,
            "answer": f"Gemini API error: {str(e)}"
        }