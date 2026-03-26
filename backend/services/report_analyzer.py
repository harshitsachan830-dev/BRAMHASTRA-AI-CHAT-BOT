from io import BytesIO
from pypdf import PdfReader
from backend.services.llm_engine import ask_ai


def extract_text_from_pdf(file) -> str:
    pdf_bytes = file.read()
    pdf_stream = BytesIO(pdf_bytes)
    reader = PdfReader(pdf_stream)

    text = []
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text.append(page_text)

    return "\n".join(text).strip()


def analyze_uploaded_report(file) -> dict:
    try:
        filename = (file.filename or "").lower()

        # TXT support
        if filename.endswith(".txt"):
            content = file.read().decode("utf-8", errors="ignore").strip()

        # PDF support
        elif filename.endswith(".pdf"):
            content = extract_text_from_pdf(file)

        else:
            return {
                "type": "report",
                "title": "Medical Report Analyzer",
                "answer": "This file type is not supported yet. Please upload a TXT or PDF report.",
                "risk_level": "Moderate",
                "health_score": 60,
                "explanation": "Report upload worked, but parser for this file type is not enabled yet.",
                "next_steps": [
                    "Upload a .txt or .pdf report.",
                    "Image OCR can be added in the next upgrade."
                ],
                "doctor_recommendation": {
                    "specialist": "General Physician",
                    "urgency": "Moderate",
                    "action": "Share the report with a doctor for full interpretation."
                }
            }

        if not content:
            return {
                "type": "report",
                "title": "Medical Report Analyzer",
                "answer": "Could not extract readable text from the uploaded report.",
                "risk_level": "Unknown",
                "health_score": 50,
                "explanation": "The file was uploaded, but no usable report text was found.",
                "next_steps": [
                    "Try another clearer PDF or TXT file.",
                    "If this is a scanned image PDF, OCR support is needed."
                ],
                "doctor_recommendation": {
                    "specialist": "General Physician",
                    "urgency": "Moderate",
                    "action": "Use a text-based report or add OCR support for scanned PDFs."
                }
            }

        prompt = f"""
Analyze this medical report text.

Return in this exact format:

Summary:
- short summary

Important Findings:
- point 1
- point 2

Abnormal Values / Concerns:
- point 1
- point 2

Risk Level:
- Low / Moderate / High

Recommended Next Steps:
- point 1
- point 2

When to See Doctor:
- point 1
- point 2

Medical report text:
{content}
"""

        ai_result = ask_ai(prompt, mode="health")

        if ai_result.get("success"):
            answer = ai_result["answer"]
            answer_lower = answer.lower()

            risk_level = "Moderate"
            health_score = 65

            if "high" in answer_lower or "critical" in answer_lower or "urgent" in answer_lower:
                risk_level = "High"
                health_score = 35
            elif "low" in answer_lower and "moderate" not in answer_lower:
                risk_level = "Low"
                health_score = 85

            return {
                "type": "report",
                "title": "Medical Report Analysis",
                "answer": answer,
                "risk_level": risk_level,
                "health_score": health_score,
                "explanation": "AI-generated structured analysis of uploaded medical report.",
                "next_steps": [
                    "Review highlighted findings carefully.",
                    "Consult a doctor for confirmation and treatment advice."
                ],
                "doctor_recommendation": {
                    "specialist": "General Physician" if risk_level != "High" else "Specialist / Physician",
                    "urgency": "Low" if risk_level == "Low" else ("Moderate" if risk_level == "Moderate" else "High"),
                    "action": "Show this report to a qualified doctor, especially if symptoms are present."
                }
            }

        return {
            "type": "report",
            "title": "Medical Report Analysis",
            "answer": "AI could not analyze the report properly.",
            "risk_level": "Unknown",
            "health_score": 50,
            "explanation": "Analysis failed.",
            "next_steps": [
                "Try again with cleaner report text.",
                "Consult a doctor directly if the report has abnormal values."
            ],
            "doctor_recommendation": {
                "specialist": "General Physician",
                "urgency": "Moderate",
                "action": "Consult a doctor for proper interpretation."
            }
        }

    except Exception as e:
        return {
            "type": "report",
            "title": "Medical Report Analysis",
            "answer": "Error while analyzing report.",
            "risk_level": "Unknown",
            "health_score": 50,
            "explanation": str(e),
            "next_steps": [
                "Try again with a clearer file.",
                "Use a text-based report if the PDF is image-only."
            ],
            "doctor_recommendation": {
                "specialist": "General Physician",
                "urgency": "Moderate",
                "action": "Retry with a better quality report file."
            }
        }