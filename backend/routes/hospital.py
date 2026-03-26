from flask import Blueprint, request, jsonify

hospital_bp = Blueprint("hospital", __name__)


@hospital_bp.route("/nearby-hospitals", methods=["POST"])
def nearby_hospitals():
    data = request.get_json() or {}
    lat = data.get("lat")
    lng = data.get("lng")

    # Demo fallback hospitals
    hospitals = [
        {
            "name": "City Care Hospital",
            "distance": "1.2 km",
            "speciality": "Emergency / General"
        },
        {
            "name": "Metro Multispeciality Hospital",
            "distance": "2.8 km",
            "speciality": "Cardiology / Emergency"
        },
        {
            "name": "Sunrise Clinic",
            "distance": "3.5 km",
            "speciality": "General Physician"
        }
    ]

    return jsonify({
        "success": True,
        "lat": lat,
        "lng": lng,
        "hospitals": hospitals
    })