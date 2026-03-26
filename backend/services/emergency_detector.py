def detect_emergency(message: str) -> dict:
    msg = message.lower()

    red_flags = [
        "chest pain",
        "shortness of breath",
        "difficulty breathing",
        "fainting",
        "unconscious",
        "vomiting blood",
        "seizure",
        "stroke",
        "severe bleeding",
        "blood in cough",
        "cannot breathe"
    ]

    for flag in red_flags:
        if flag in msg:
            return {
                "is_emergency": True,
                "message": (
                    "Your symptoms may indicate a medical emergency. "
                    "Please seek immediate medical care or go to the nearest hospital now."
                )
            }

    return {"is_emergency": False, "message": ""}