from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from datetime import datetime


def create_pdf_report(file_path, data):
    c = canvas.Canvas(file_path, pagesize=A4)
    width, height = A4

    # Header
    c.setFillColor(colors.HexColor("#0f172a"))
    c.rect(0, height - 80, width, 80, fill=1, stroke=0)

    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 22)
    c.drawString(40, height - 45, "SwasthyaAI Ultra")

    c.setFont("Helvetica", 10)
    c.drawString(40, height - 62, "AI Health Intelligence Platform Report")

    y = height - 110

    # Metadata
    c.setFillColor(colors.black)
    c.setFont("Helvetica", 11)
    c.drawString(40, y, f"Generated on: {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}")
    y -= 30

    # Main sections
    c.setFont("Helvetica-Bold", 14)
    c.drawString(40, y, "Assessment Summary")
    y -= 22

    c.setFont("Helvetica", 11)
    fields = [
        ("Title", data.get("title", "N/A")),
        ("Risk Level", data.get("risk_level", "N/A")),
        ("Health Score", str(data.get("health_score", "N/A"))),
        ("Explanation", data.get("explanation", "N/A")),
    ]

    for label, value in fields:
        c.setFont("Helvetica-Bold", 11)
        c.drawString(40, y, f"{label}:")
        c.setFont("Helvetica", 11)
        c.drawString(140, y, str(value)[:90])
        y -= 22

    # Answer box
    y -= 8
    c.setFont("Helvetica-Bold", 14)
    c.drawString(40, y, "AI Guidance")
    y -= 22

    c.setFont("Helvetica", 11)
    answer = data.get("answer", "N/A")
    lines = answer.split("\n")
    for line in lines[:12]:
        c.drawString(50, y, line[:95])
        y -= 16
        if y < 120:
            c.showPage()
            y = height - 50

    # Next steps
    y -= 10
    c.setFont("Helvetica-Bold", 14)
    c.drawString(40, y, "Next Steps")
    y -= 22

    c.setFont("Helvetica", 11)
    next_steps = data.get("next_steps", [])
    if next_steps:
        for step in next_steps[:6]:
            c.drawString(50, y, f"- {step[:90]}")
            y -= 18
    else:
        c.drawString(50, y, "- No next steps available.")
        y -= 18

    # Doctor recommendation
    doctor = data.get("doctor_recommendation", {})
    y -= 10
    c.setFont("Helvetica-Bold", 14)
    c.drawString(40, y, "Doctor Recommendation")
    y -= 22

    c.setFont("Helvetica", 11)
    c.drawString(50, y, f"Specialist: {doctor.get('specialist', 'N/A')}")
    y -= 18
    c.drawString(50, y, f"Urgency: {doctor.get('urgency', 'N/A')}")
    y -= 18
    c.drawString(50, y, f"Action: {doctor.get('action', 'N/A')[:90]}")
    y -= 24

    # Footer
    c.setStrokeColor(colors.grey)
    c.line(40, 60, width - 40, 60)

    c.setFont("Helvetica-Oblique", 9)
    c.drawString(40, 45, "Disclaimer: This report is for educational support only and not a substitute for medical diagnosis.")
    c.drawString(40, 30, "Powered by AI + FDA data + risk-based doctor recommendation.")

    c.save()