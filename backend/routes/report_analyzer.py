from flask import Blueprint, request, jsonify
from backend.services.report_analyzer import analyze_uploaded_report

report_analyzer_bp = Blueprint("report_analyzer", __name__)

@report_analyzer_bp.route("/analyze-report", methods=["POST"])
def analyze_report():
    if "report" not in request.files:
        return jsonify({"error": "No report file uploaded"}), 400

    file = request.files["report"]
    result = analyze_uploaded_report(file)
    return jsonify(result)