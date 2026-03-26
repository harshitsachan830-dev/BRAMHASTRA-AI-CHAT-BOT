from flask import Blueprint, request, jsonify
from backend.services.symptom_analyzer import (
    detect_query_type,
    detect_query_components,
    get_general_answer,
    get_health_answer,
    get_medicine_info,
    analyze_symptoms,
)
from backend.services.emergency_detector import detect_emergency
from backend.services.llm_engine import ask_ai
from backend.services.doctor_recommender import get_doctor_recommendation

chat_bp = Blueprint("chat", __name__)


@chat_bp.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_message = data.get("message", "").strip()

    if not user_message:
        return jsonify({"error": "Empty message"}), 400

    emergency = detect_emergency(user_message)
    if emergency["is_emergency"]:
        doctor_info = get_doctor_recommendation("Emergency", user_message)

        return jsonify({
            "type": "emergency",
            "title": "Emergency Alert",
            "answer": emergency["message"],
            "risk_level": "Emergency",
            "health_score": 20,
            "explanation": "This query contains red-flag symptoms requiring immediate medical attention.",
            "next_steps": [
                "Go to the nearest hospital immediately.",
                "Do not rely only on chatbot advice.",
                "Call emergency help or contact a doctor right now."
            ],
            "doctor_recommendation": doctor_info
        })

    query_type = detect_query_type(user_message)
    components = detect_query_components(user_message)

    if components["has_medicine"] and components["has_symptom"]:
        med_response = get_medicine_info(user_message)
        symptom_response = analyze_symptoms(user_message)
        ai_result = ask_ai(user_message, mode="health")

        if ai_result["success"]:
            combined_answer = (
                f"{ai_result['answer']}\n\n"
                f"Medicine Information:\n{med_response['answer']}"
            )
        else:
            combined_answer = (
                f"{symptom_response['answer']}\n\n"
                f"Medicine Information:\n{med_response['answer']}"
            )

        return jsonify({
            "type": "ai_combined",
            "title": "AI + Symptom + Medicine Analysis",
            "answer": combined_answer,
            "risk_level": symptom_response["risk_level"],
            "health_score": symptom_response["health_score"],
            "explanation": symptom_response["explanation"] + " + combined medicine check",
            "next_steps": symptom_response["next_steps"],
            "doctor_recommendation": get_doctor_recommendation(symptom_response["risk_level"], user_message)
        })

    if query_type == "medicine":
        med_response = get_medicine_info(user_message)
        ai_result = ask_ai(user_message, mode="health")

        if ai_result["success"]:
            combined_answer = (
                f"{ai_result['answer']}\n\n"
                f"Medicine Information:\n{med_response['answer']}"
            )

            return jsonify({
                "type": "ai_medicine",
                "title": "AI + Medicine Guidance",
                "answer": combined_answer,
                "risk_level": med_response["risk_level"],
                "health_score": med_response["health_score"],
                "explanation": "Combined AI guidance with verified FDA medicine data.",
                "next_steps": med_response["next_steps"],
                "doctor_recommendation": get_doctor_recommendation(med_response["risk_level"], user_message)
            })

        med_response["title"] = "Medicine Info (AI Fallback)"
        med_response["doctor_recommendation"] = get_doctor_recommendation(med_response["risk_level"], user_message)
        return jsonify(med_response)

    if query_type == "symptom":
        base = analyze_symptoms(user_message)
        ai_result = ask_ai(user_message, mode="health")

        if ai_result["success"]:
            return jsonify({
                "type": "ai_symptom",
                "title": "AI Symptom Analysis",
                "answer": ai_result["answer"],
                "risk_level": base["risk_level"],
                "health_score": base["health_score"],
                "explanation": base["explanation"] + " + AI analysis",
                "next_steps": base["next_steps"],
                "doctor_recommendation": get_doctor_recommendation(base["risk_level"], user_message)
            })

        base["title"] = "Symptom Analysis (AI Fallback)"
        base["explanation"] = base["explanation"] + f" | AI error: {ai_result['answer']}"
        base["doctor_recommendation"] = get_doctor_recommendation(base["risk_level"], user_message)
        return jsonify(base)

    if query_type == "health":
        base_response = get_health_answer(user_message)
        ai_result = ask_ai(user_message, mode="health")

        if ai_result["success"]:
            return jsonify({
                "type": "ai_health",
                "title": "AI Health Guidance",
                "answer": ai_result["answer"],
                "risk_level": base_response["risk_level"],
                "health_score": base_response["health_score"],
                "explanation": "Generated using AI with health-safety guidance.",
                "next_steps": base_response["next_steps"],
                "doctor_recommendation": get_doctor_recommendation(base_response["risk_level"], user_message)
            })

        base_response["title"] = "Health Guidance (AI Fallback)"
        base_response["explanation"] = f"AI error: {ai_result['answer']}"
        base_response["doctor_recommendation"] = get_doctor_recommendation(base_response["risk_level"], user_message)
        return jsonify(base_response)

    ai_result = ask_ai(user_message, mode="general")

    if ai_result["success"]:
        return jsonify({
            "type": "ai_general",
            "title": "AI General Answer",
            "answer": ai_result["answer"],
            "risk_level": "None",
            "health_score": 100,
            "explanation": "Generated using AI.",
            "next_steps": [],
            "doctor_recommendation": get_doctor_recommendation("Low", user_message)
        })

    fallback = get_general_answer(user_message)
    fallback["title"] = "General Assistant (AI Fallback)"
    fallback["explanation"] = f"AI error: {ai_result['answer']}"
    fallback["doctor_recommendation"] = get_doctor_recommendation("Low", user_message)
    return jsonify(fallback)