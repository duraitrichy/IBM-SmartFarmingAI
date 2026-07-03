"""main.py — Home, Dashboard, and Knowledge Base routes."""

from flask import Blueprint, render_template, session
from sqlalchemy import select, func
from database import db, Recommendation, ChatHistory, WeatherRecord, MarketPrice

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def index():
    return render_template("index.html")


@main_bp.route("/dashboard")
def dashboard():
    farmer_id = session.get("farmer_id")
    stats = {
        "total_recommendations": db.session.scalar(select(func.count()).select_from(Recommendation).where(Recommendation.farmer_id == farmer_id)),
        "total_chats": db.session.scalar(select(func.count()).select_from(ChatHistory).where(ChatHistory.farmer_id == farmer_id)),
        "weather_checks": db.session.scalar(select(func.count()).select_from(WeatherRecord).where(WeatherRecord.farmer_id == farmer_id)),
        "market_checks": db.session.scalar(select(func.count()).select_from(MarketPrice)),
    }
    recent_recs = db.session.scalars(
        select(Recommendation)
        .where(Recommendation.farmer_id == farmer_id)
        .order_by(Recommendation.created_at.desc())
        .limit(5)
    ).all()
    return render_template("dashboard.html", stats=stats, recent_recs=recent_recs)


@main_bp.route("/knowledge-base")
def knowledge_base():
    from tools.government_schemes import GovernmentSchemesTool
    schemes = GovernmentSchemesTool().get_all()
    return render_template("knowledge_base.html", schemes=schemes)
