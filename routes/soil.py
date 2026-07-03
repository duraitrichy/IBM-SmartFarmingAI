"""soil.py — Soil health page route."""
from flask import Blueprint, render_template
soil_bp = Blueprint("soil", __name__)

@soil_bp.route("/")
def soil_page():
    return render_template("soil.html")
