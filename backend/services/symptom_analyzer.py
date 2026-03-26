from backend.services.openfda_service import get_drug_info


def detect_query_type(message: str) -> str:
    msg = message.lower()

    medicine_keywords = [
    "medicine", "tablet", "capsule", "paracetamol", "acetaminophen",
    "dolo", "crocin", "calpol", "ibuprofen", "aspirin", "cetirizine",
    "tylenol", "drug", "side effect", "uses of", "dose", "syrup",
    "can i take", "should i take", "safe to take"
    ]



    symptom_keywords = [
        "symptom", "pain", "fever", "cough", "weight loss", "fatigue",
        "lump", "bleeding", "weakness", "tired", "vomiting", "rash",
        "cancer", "tumor", "swelling", "headache", "cold", "sore throat"
    ]

    health_keywords = [
        "diabetes", "bp", "blood pressure", "thyroid", "infection", "disease",
        "health", "doctor", "treatment", "precaution", "prevention"
    ]

    words = msg.split()

    if any(keyword in msg for keyword in medicine_keywords):
        return "medicine"

    known_medicine_names = {
        "paracetamol", "acetaminophen", "dolo", "crocin",
        "calpol", "ibuprofen", "aspirin", "cetirizine", "tylenol"
    }

    if any(word in known_medicine_names for word in words):
        return "medicine"

    if any(word in msg for word in symptom_keywords):
        return "symptom"

    if any(word in msg for word in health_keywords):
        return "health"

    return "general"


def get_general_answer(message: str) -> dict:
    msg = message.lower()

    general_knowledge = {
        "what is python": "Python is a high-level programming language used for web development, AI, automation, data science, and more.",
        "what is ai": "AI stands for Artificial Intelligence. It enables machines to simulate human intelligence such as learning, reasoning, and problem-solving.",
        "what is machine learning": "Machine learning is a branch of AI where systems learn patterns from data and make predictions.",
        "what is india capital": "The capital of India is New Delhi."
    }

    for key, value in general_knowledge.items():
        if key in msg:
            return {
                "type": "general",
                "title": "General Answer",
                "answer": value,
                "risk_level": "None",
                "health_score": 100,
                "explanation": "This is a general knowledge response.",
                "next_steps": []
            }

    return {
        "type": "general",
        "title": "General Assistant",
        "answer": (
            "I can answer general and health-related questions. "
            "For health questions, I provide educational guidance, not a final diagnosis."
        ),
        "risk_level": "None",
        "health_score": 100,
        "explanation": "No specific health risk detected.",
        "next_steps": []
    }


def get_health_answer(message: str) -> dict:
    msg = message.lower()

    if "diabetes" in msg:
        return {
            "type": "health",
            "title": "Diabetes Information",
            "answer": (
                "Diabetes is a condition where blood sugar levels become too high. "
                "Common symptoms include increased thirst, frequent urination, fatigue, and blurred vision."
            ),
            "risk_level": "Moderate",
            "health_score": 65,
            "explanation": "Diabetes requires medical monitoring and lifestyle control.",
            "next_steps": [
                "Check blood sugar regularly.",
                "Reduce sugar intake.",
                "Consult a doctor for proper diagnosis."
            ]
        }

    if "blood pressure" in msg or "bp" in msg:
        return {
            "type": "health",
            "title": "Blood Pressure Information",
            "answer": (
                "High blood pressure can increase the risk of heart disease and stroke. "
                "It may not always show symptoms, so regular monitoring is important."
            ),
            "risk_level": "Moderate",
            "health_score": 70,
            "explanation": "Blood pressure problems often require monitoring and medical advice.",
            "next_steps": [
                "Reduce salt intake.",
                "Exercise regularly.",
                "Monitor BP levels.",
                "Consult a physician."
            ]
        }

    return {
        "type": "health",
        "title": "Health Guidance",
        "answer": (
            "This appears to be a health-related query. I can help explain symptoms, "
            "possible causes, precautions, and when to seek medical care."
        ),
        "risk_level": "Low",
        "health_score": 80,
        "explanation": "General health guidance provided.",
        "next_steps": [
            "Monitor symptoms.",
            "Stay hydrated.",
            "Consult a doctor if symptoms persist."
        ]
    }


def get_medicine_info(message: str) -> dict:
    msg = message.lower()
    words = [w.strip(".,!?") for w in msg.split() if len(w) > 2]

    medicine_aliases = {
        "paracetamol": "acetaminophen",
        "dolo": "acetaminophen",
        "crocin": "acetaminophen",
        "calpol": "acetaminophen",
        "combiflam": "ibuprofen",
    }

    for word in words:
        search_term = medicine_aliases.get(word, word)
        result = get_drug_info(search_term)

        if result["success"]:
            return {
                "type": "medicine",
                "title": f"{word.title()} Information (FDA)",
                "answer": (
                    f"Use: {result['use']}\n\n"
                    f"Side Effects: {result['side_effects']}\n\n"
                    f"Warnings: {result['warnings']}"
                ),
                "risk_level": "Verified Data",
                "health_score": 75,
                "explanation": f"Information retrieved from official FDA database using search term '{search_term}'.",
                "next_steps": [
                    "Consult a doctor before taking medication.",
                    "Avoid overdose.",
                    "Do not self-medicate in serious conditions."
                ]
            }

    return {
        "type": "medicine",
        "title": "Medicine Info",
        "answer": "Medicine not found in FDA database.",
        "risk_level": "Unknown",
        "health_score": 70,
        "explanation": "No verified data available.",
        "next_steps": [
            "Check spelling of medicine.",
            "Try generic or brand name.",
            "Consult a doctor."
        ]
    }


def analyze_symptoms(message: str) -> dict:
    msg = message.lower()

    score = 100
    reasons = []
    next_steps = []
    answer = ""

    if "fever" in msg:
        score -= 25
        reasons.append("fever")
    if "headache" in msg:
        score -= 10
        reasons.append("headache")
    if "cold" in msg:
        score -= 10
        reasons.append("cold symptoms")
    if "cough" in msg:
        score -= 15
        reasons.append("cough")
    if "sore throat" in msg:
        score -= 10
        reasons.append("sore throat")
    if "vomiting" in msg:
        score -= 20
        reasons.append("vomiting")
    if "fatigue" in msg or "weakness" in msg:
        score -= 15
        reasons.append("fatigue/weakness")
    if "weight loss" in msg:
        score -= 20
        reasons.append("unexplained weight loss")
    if "pain" in msg:
        score -= 10
        reasons.append("pain")
    if "lump" in msg:
        score -= 25
        reasons.append("presence of lump")
    if "bleeding" in msg:
        score -= 25
        reasons.append("unusual bleeding")
    if "smoking" in msg:
        score -= 15
        reasons.append("smoking history")
    if "skin lesion" in msg or "mole" in msg:
        score -= 20
        reasons.append("skin lesion change")

    if score < 10:
        score = 10

    if "fever" in msg and score >= 70:
        risk = "Moderate"
        answer = (
            "Fever is usually a sign that your body is fighting an infection. "
            "It may be due to viral infection, flu, or another illness. "
            "Monitor temperature, take rest, and stay hydrated."
        )
        next_steps = [
            "Drink plenty of fluids.",
            "Take proper rest.",
            "Monitor body temperature.",
            "Consult a doctor if fever lasts more than 2–3 days or becomes very high."
        ]
    elif score >= 80:
        risk = "Low"
        answer = (
            "Based on the entered symptoms, the immediate risk appears low, "
            "but symptoms should still be monitored."
        )
        next_steps = [
            "Monitor symptoms for a few days.",
            "Maintain hydration and healthy diet.",
            "Consult a doctor if symptoms persist."
        ]
    elif score >= 55:
        risk = "Moderate"
        answer = (
            "Your symptoms indicate a moderate concern level. "
            "Medical consultation is recommended if symptoms continue or worsen."
        )
        next_steps = [
            "Consult a doctor soon.",
            "Do not ignore persistent symptoms.",
            "Take rest and monitor changes carefully."
        ]
    else:
        risk = "High"
        answer = (
            "Your symptoms suggest a high concern level and need timely medical evaluation. "
            "This is not a diagnosis, but screening or clinical consultation is strongly recommended."
        )
        next_steps = [
            "Consult a specialist urgently.",
            "Do not delay medical screening.",
            "Avoid self-medication for serious symptoms."
        ]

    explanation = "Risk factors detected: " + (", ".join(reasons) if reasons else "general symptom query")

    return {
        "type": "symptom",
        "title": "Symptom Analysis",
        "answer": answer,
        "risk_level": risk,
        "health_score": score,
        "explanation": explanation,
        "next_steps": next_steps
    }


def is_ai_health_query(message: str) -> bool:
    msg = message.lower()

    health_words = [
        "fever", "cough", "cold", "headache", "vomiting", "nausea",
        "pain", "weakness", "fatigue", "infection", "diabetes",
        "bp", "blood pressure", "thyroid", "doctor", "medicine",
        "treatment", "symptoms", "disease", "weight loss"
    ]

    return any(word in msg for word in health_words)

def detect_query_components(message: str) -> dict:
    msg = message.lower()

    medicine_keywords = [
        "medicine", "tablet", "capsule", "paracetamol", "acetaminophen",
        "dolo", "crocin", "calpol", "ibuprofen", "aspirin", "cetirizine",
        "tylenol", "drug", "side effect", "uses of", "dose", "syrup",
        "can i take", "should i take", "safe to take"
    ]

    symptom_keywords = [
        "symptom", "pain", "fever", "cough", "weight loss", "fatigue",
        "lump", "bleeding", "weakness", "tired", "vomiting", "rash",
        "cancer", "tumor", "swelling", "headache", "cold", "sore throat"
    ]

    has_medicine = any(keyword in msg for keyword in medicine_keywords)
    has_symptom = any(keyword in msg for keyword in symptom_keywords)

    return {
        "has_medicine": has_medicine,
        "has_symptom": has_symptom
    }