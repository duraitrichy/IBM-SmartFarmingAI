"""market.py — Market intelligence page route."""
from flask import Blueprint, render_template
market_bp = Blueprint("market", __name__)

@market_bp.route("/")
def market_page():
    return render_template("market.html")
