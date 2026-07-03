"""
api.py — JSON REST API blueprint for all AI agent endpoints.
All endpoints return application/json.
"""

import uuid
from flask import Blueprint, request, jsonify, session
from loguru import logger
from sqlalchemy import select
from agents import (
    CropAdvisoryAgent, WeatherIrrigationAgent, SoilHealthAgent,
    PestDiseaseAgent, MarketIntelligenceAgent, MasterOrchestrator,
)
from tools import WeatherAPI, SoilAnalysisTool, MarketAPI, GovernmentSchemesTool
from tools.image_classifier import ImageClassifier
from database import db, Recommendation, ChatHistory, Disease, WeatherRecord, SoilRecord, MarketPrice

api_bp = Blueprint("api", __name__)

# ── Singletons (created on first request) ────────────────────────────────
_orchestrator: MasterOrchestrator | None = None


def get_orchestrator() -> MasterOrchestrator:
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = MasterOrchestrator()
    return _orchestrator


# ── /api/chat ──────────────────────────────────────────────────────────────

@api_bp.route("/chat", methods=["POST"])
def chat():
    data = request.get_json(force=True)
    query = (data.get("query") or "").strip()
    if not query:
        return jsonify({"error": "Query is required."}), 400

    if "session_id" not in session:
        session["session_id"] = uuid.uuid4().hex

    farmer_profile = {
        "query": query,
        "crop": data.get("crop", session.get("crop", "")),
        "location": data.get("location", session.get("location", "India")),
        "experience": data.get("experience", session.get("experience", 0)),
        "season": data.get("season", "Kharif"),
        "soil_type": data.get("soil_type", ""),
        "farm_size": data.get("farm_size", 1),
    }

    try:
        result = get_orchestrator().run(farmer_profile)
    except Exception as exc:
        logger.error(f"Orchestrator error: {exc}")
        return jsonify({"error": str(exc)}), 500

    # Persist conversation
    farmer_id = session.get("farmer_id")
    sid = session["session_id"]
    db.session.add(ChatHistory(session_id=sid, farmer_id=farmer_id, role="user", message=query, agent_used=result.get("intent", "")))
    db.session.add(ChatHistory(session_id=sid, farmer_id=farmer_id, role="assistant", message=result.get("synthesis", ""), agent_used=result.get("intent", "")))
    db.session.commit()

    return jsonify(result)


# ── /api/crop ──────────────────────────────────────────────────────────────

@api_bp.route("/crop", methods=["POST"])
def crop_advice():
    data = request.get_json(force=True)
    try:
        result = CropAdvisoryAgent().run(data)
        _save_recommendation("crop", data.get("query", "Crop advisory"), result)
        return jsonify(result)
    except Exception as exc:
        logger.error(f"Crop agent error: {exc}")
        return jsonify({"error": str(exc)}), 500


# ── /api/weather ───────────────────────────────────────────────────────────

@api_bp.route("/weather", methods=["GET", "POST"])
def weather():
    city = request.args.get("city") or (request.get_json(force=True) or {}).get("city", "Delhi")
    weather_api = WeatherAPI()
    current = weather_api.get_current(city)
    forecast = weather_api.get_forecast(city)

    # Enrich with irrigation advice
    inputs = {**current, "forecast": forecast,
              "crop": (request.get_json(force=True) or {}).get("crop", "Rice"),
              "season": "Kharif", "farm_size": 1, "soil_moisture": 50}
    agent_result = WeatherIrrigationAgent().run(inputs)

    record = WeatherRecord(
        farmer_id=session.get("farmer_id"),
        location=city,
        temperature=current.get("temperature"),
        humidity=current.get("humidity"),
        wind_speed=current.get("wind_speed"),
        rainfall=current.get("rainfall"),
        weather_condition=current.get("weather_condition"),
        irrigation_advice=agent_result.get("recommended_action", ""),
    )
    db.session.add(record)
    db.session.commit()

    return jsonify({"current": current, "forecast": forecast, "agent": agent_result})


# ── /api/soil ──────────────────────────────────────────────────────────────

@api_bp.route("/soil", methods=["POST"])
def soil():
    data = request.get_json(force=True)
    # Rule-based quick analysis
    tool_result = SoilAnalysisTool().analyse(data)
    # AI deep analysis
    ai_result = SoilHealthAgent().run(data)

    record = SoilRecord(
        farmer_id=session.get("farmer_id"),
        soil_type=data.get("soil_type"),
        ph=data.get("ph"),
        nitrogen=data.get("nitrogen"),
        phosphorus=data.get("phosphorus"),
        potassium=data.get("potassium"),
        moisture=data.get("moisture"),
        recommended_crops=str(tool_result.get("suitable_crops")),
        fertilizer_advice=ai_result.get("recommended_action", ""),
    )
    db.session.add(record)
    db.session.commit()

    return jsonify({"tool_analysis": tool_result, "ai_analysis": ai_result})


# ── /api/pest ──────────────────────────────────────────────────────────────

@api_bp.route("/pest", methods=["POST"])
def pest():
    classifier = ImageClassifier()
    file = request.files.get("image")
    data = request.form

    inputs = {
        "crop": data.get("crop", "Unknown"),
        "location": data.get("location", "India"),
        "symptoms": data.get("symptoms", ""),
        "affected_area": data.get("affected_area", 10),
        "duration": data.get("duration", "Unknown"),
        "weather": data.get("weather", "Normal"),
    }

    if file:
        save_result = classifier.validate_and_save(file)
        if not save_result.get("success"):
            return jsonify({"error": save_result.get("error")}), 400
        inputs["image_path"] = save_result["path"]

    try:
        result = PestDiseaseAgent().run(inputs)
        disease = Disease(
            farmer_id=session.get("farmer_id"),
            image_path=inputs.get("image_path"),
            disease_name=result.get("problem_summary", ""),
            confidence_score=result.get("confidence_score"),
            treatment=result.get("recommended_action"),
            organic_solution=result.get("alternative_option"),
            raw_analysis=result.get("analysis"),
        )
        db.session.add(disease)
        db.session.commit()
        return jsonify(result)
    except Exception as exc:
        logger.error(f"Pest agent error: {exc}")
        return jsonify({"error": str(exc)}), 500


# ── /api/market ────────────────────────────────────────────────────────────

@api_bp.route("/market", methods=["POST"])
def market():
    data = request.get_json(force=True)
    crop = data.get("crop", "tomato")
    market_data = MarketAPI().get_prices(crop, data.get("state", "All"))
    inputs = {**data, "market_data": market_data}
    try:
        result = MarketIntelligenceAgent().run(inputs)
        return jsonify({"prices": market_data, "agent": result})
    except Exception as exc:
        logger.error(f"Market agent error: {exc}")
        return jsonify({"error": str(exc)}), 500


# ── /api/schemes ───────────────────────────────────────────────────────────

@api_bp.route("/schemes", methods=["GET"])
def schemes():
    query = request.args.get("q", "")
    tool = GovernmentSchemesTool()
    results = tool.search(query) if query else tool.get_all()
    return jsonify(results)


# ── /api/rag ───────────────────────────────────────────────────────────────

@api_bp.route("/rag", methods=["POST"])
def rag_query():
    data = request.get_json(force=True)
    from rag import RAGGenerator
    try:
        result = RAGGenerator().run(data)
        return jsonify(result)
    except Exception as exc:
        logger.error(f"RAG error: {exc}")
        return jsonify({"error": str(exc)}), 500


# ── /api/history ───────────────────────────────────────────────────────────

@api_bp.route("/history", methods=["GET"])
def history():
    sid = session.get("session_id")
    rows = db.session.scalars(select(ChatHistory).where(ChatHistory.session_id == sid).order_by(ChatHistory.created_at)).all()
    return jsonify([
        {"role": r.role, "message": r.message, "timestamp": r.created_at.isoformat()}
        for r in rows
    ])


# ── Helper ─────────────────────────────────────────────────────────────────

def _save_recommendation(agent_type: str, query: str, result: dict) -> None:
    try:
        rec = Recommendation(
            farmer_id=session.get("farmer_id"),
            agent_type=agent_type,
            query=query,
            recommendation=result.get("analysis", ""),
            problem_summary=result.get("problem_summary", ""),
            recommended_action=result.get("recommended_action", ""),
            risk_level=result.get("risk_level", "Low"),
            confidence_score=result.get("confidence_score", 0.0),
        )
        db.session.add(rec)
        db.session.commit()
    except Exception as exc:
        logger.warning(f"Failed to save recommendation: {exc}")
