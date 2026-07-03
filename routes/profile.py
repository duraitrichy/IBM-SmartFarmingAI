"""
profile.py — Farmer profile GET and POST routes.
"""

from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from sqlalchemy import select
from database import db, Farmer

profile_bp = Blueprint("profile", __name__)


@profile_bp.route("/", methods=["GET"])
def profile_page():
    farmer_id = session.get("farmer_id")
    farmer = db.session.get(Farmer, farmer_id) if farmer_id else None
    return render_template("profile.html", farmer=farmer)


@profile_bp.route("/save", methods=["POST"])
def save_profile():
    data = request.form
    farmer_id = session.get("farmer_id")
    farmer = db.session.get(Farmer, farmer_id) if farmer_id else Farmer()

    farmer.name = data.get("name", "")
    farmer.age = int(data.get("age") or 0)
    farmer.village = data.get("village", "")
    farmer.district = data.get("district", "")
    farmer.state = data.get("state", "")
    farmer.country = data.get("country", "India")
    farmer.farm_size = float(data.get("farm_size") or 0)
    farmer.crop = data.get("crop", "")
    farmer.season = data.get("season", "")
    farmer.budget = float(data.get("budget") or 0)
    farmer.experience_years = int(data.get("experience_years") or 0)
    farmer.water_source = data.get("water_source", "")
    farmer.soil_type = data.get("soil_type", "")
    farmer.soil_ph = float(data.get("soil_ph") or 7.0)
    farmer.nitrogen = float(data.get("nitrogen") or 0)
    farmer.phosphorus = float(data.get("phosphorus") or 0)
    farmer.potassium = float(data.get("potassium") or 0)
    farmer.previous_yield = float(data.get("previous_yield") or 0)
    farmer.preferred_language = data.get("preferred_language", "English")
    farmer.email = data.get("email", "")
    farmer.phone = data.get("phone", "")

    if not farmer_id:
        db.session.add(farmer)
    db.session.commit()

    session["farmer_id"] = farmer.id
    session["crop"] = farmer.crop
    session["location"] = f"{farmer.district}, {farmer.state}"
    session["experience"] = farmer.experience_years

    flash("Profile saved successfully!", "success")
    return redirect(url_for("profile.profile_page"))
