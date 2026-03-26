import os
import uuid
from flask import Blueprint, request, jsonify, send_file, current_app
from backend.utils.pdf_generator import create_pdf_report

report_bp = Blueprint("report", __name__)

@report_bp.route("/generate-report", methods=["POST"])
def generate_report():
    data = request.get_json()

    report_folder = os.path.join(current_app.static_folder, "reports")
    os.makedirs(report_folder, exist_ok=True)

    report_id = str(uuid.uuid4())[:8]
    file_path = os.path.join(report_folder, f"health_report_{report_id}.pdf")

    create_pdf_report(file_path, data)

    return jsonify({
        "message": "Report generated successfully",
        "report_url": f"/download-report/{report_id}"
    })

@report_bp.route("/download-report/<report_id>")
def download_report(report_id):
    report_folder = os.path.join(current_app.static_folder, "reports")
    file_path = os.path.join(report_folder, f"health_report_{report_id}.pdf")

    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True)

    return "Report not found", 404