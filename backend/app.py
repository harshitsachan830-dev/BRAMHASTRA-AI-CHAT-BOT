from flask import Flask, render_template
from backend.routes.hospital import hospital_bp
from backend.routes.chat import chat_bp
from backend.routes.report import report_bp
from backend.routes.vision import vision_bp
from backend.routes.food import food_bp
from backend.routes.report_analyzer import report_analyzer_bp

app = Flask(
    __name__,
    template_folder="../frontend/templates",
    static_folder="../frontend/static"
)

app.register_blueprint(chat_bp)
app.register_blueprint(report_bp)
app.register_blueprint(hospital_bp)
app.register_blueprint(vision_bp)
app.register_blueprint(food_bp)
app.register_blueprint(report_analyzer_bp)

@app.route("/")
def home():
    return render_template("index.html")