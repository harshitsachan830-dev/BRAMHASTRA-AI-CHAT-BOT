from flask import Blueprint, request, jsonify
from backend.services.food_image_detector import detect_food_from_image

food_bp = Blueprint("food", __name__)

@food_bp.route("/detect-food-image", methods=["POST"])
def detect_food_image():
    data = request.get_json()
    image_data = data.get("image", "")

    if not image_data:
        return jsonify({"error": "No image provided"}), 400

    result = detect_food_from_image(image_data)
    return jsonify(result)