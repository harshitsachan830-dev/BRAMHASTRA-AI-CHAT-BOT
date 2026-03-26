from flask import Blueprint, request, jsonify
from backend.services.medicine_image_detector import detect_medicine_from_image

vision_bp = Blueprint("vision", __name__)

@vision_bp.route("/detect-medicine-image", methods=["POST"])
def detect_medicine_image():
    data = request.get_json()
    image_data = data.get("image", "")

    if not image_data:
        return jsonify({"error": "No image provided"}), 400

    result = detect_medicine_from_image(image_data)
    return jsonify(result)