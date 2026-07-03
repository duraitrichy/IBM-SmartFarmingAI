"""pest.py — Pest & disease detection page route."""
from flask import Blueprint, render_template
pest_bp = Blueprint("pest", __name__)

@pest_bp.route("/")
def pest_page():
    return render_template("pest.html")
