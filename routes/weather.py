"""weather.py — Weather page route."""
from flask import Blueprint, render_template
weather_bp = Blueprint("weather", __name__)

@weather_bp.route("/")
def weather_page():
    return render_template("weather.html")
