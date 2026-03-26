def get_doctor_recommendation(risk_level: str, message: str = "") -> dict:
    risk = (risk_level or "").lower()
    msg = (message or "").lower()

    specialist = "General Physician"
    action = "Consult a doctor if symptoms persist."
    urgency = "Normal"

    if risk == "low":
        specialist = "Home Care / General Physician if needed"
        action = "Rest, hydration, monitor symptoms, and visit a general physician if symptoms continue."
        urgency = "Low"

    elif risk == "moderate":
        specialist = "General Physician"
        action = "Book an appointment with a general physician soon for proper evaluation."
        urgency = "Moderate"

    elif risk == "high":
        specialist = "Specialist"
        action = "Seek timely specialist evaluation. Do not delay medical consultation."
        urgency = "High"

        if any(word in msg for word in ["cough", "breathing", "lungs", "smoking"]):
            specialist = "Pulmonologist / Chest Specialist"
        elif any(word in msg for word in ["lump", "bleeding", "cancer", "tumor"]):
            specialist = "Oncologist / Specialist Physician"
        elif any(word in msg for word in ["skin lesion", "mole", "rash", "skin"]):
            specialist = "Dermatologist"
        elif any(word in msg for word in ["headache", "seizure", "stroke"]):
            specialist = "Neurologist"

    elif risk == "emergency":
        specialist = "Emergency Department / Hospital"
        action = "Go to the nearest hospital immediately or call emergency help now."
        urgency = "Emergency"

    return {
        "specialist": specialist,
        "action": action,
        "urgency": urgency
    }