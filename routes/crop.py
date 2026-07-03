"""crop.py — Crop advisory page route."""
from flask import Blueprint, render_template
crop_bp = Blueprint("crop", __name__)

@crop_bp.route("/")
def crop_page():
    return render_template("crop.html")
