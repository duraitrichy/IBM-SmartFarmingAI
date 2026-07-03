"""
models.py — All SQLAlchemy ORM models for SmartFarmingAI.
"""

from datetime import datetime
from .db import db


class Farmer(db.Model):
    __tablename__ = "farmers"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer)
    village = db.Column(db.String(100))
    district = db.Column(db.String(100))
    state = db.Column(db.String(100))
    country = db.Column(db.String(100), default="India")
    farm_size = db.Column(db.Float)          # in acres
    crop = db.Column(db.String(100))
    season = db.Column(db.String(50))
    budget = db.Column(db.Float)
    experience_years = db.Column(db.Integer)
    water_source = db.Column(db.String(100))
    soil_type = db.Column(db.String(100))
    soil_ph = db.Column(db.Float)
    nitrogen = db.Column(db.Float)
    phosphorus = db.Column(db.Float)
    potassium = db.Column(db.Float)
    previous_yield = db.Column(db.Float)
    preferred_language = db.Column(db.String(20), default="English")
    email = db.Column(db.String(150))
    phone = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class WeatherRecord(db.Model):
    __tablename__ = "weather"

    id = db.Column(db.Integer, primary_key=True)
    farmer_id = db.Column(db.Integer, db.ForeignKey("farmers.id"))
    location = db.Column(db.String(200))
    temperature = db.Column(db.Float)
    humidity = db.Column(db.Float)
    wind_speed = db.Column(db.Float)
    rainfall = db.Column(db.Float)
    uv_index = db.Column(db.Float)
    weather_condition = db.Column(db.String(100))
    forecast_json = db.Column(db.Text)          # 7-day JSON
    irrigation_advice = db.Column(db.Text)
    recorded_at = db.Column(db.DateTime, default=datetime.utcnow)


class SoilRecord(db.Model):
    __tablename__ = "soil"

    id = db.Column(db.Integer, primary_key=True)
    farmer_id = db.Column(db.Integer, db.ForeignKey("farmers.id"))
    soil_type = db.Column(db.String(100))
    ph = db.Column(db.Float)
    nitrogen = db.Column(db.Float)
    phosphorus = db.Column(db.Float)
    potassium = db.Column(db.Float)
    moisture = db.Column(db.Float)
    organic_matter = db.Column(db.Float)
    recommended_crops = db.Column(db.Text)
    fertilizer_advice = db.Column(db.Text)
    manure_advice = db.Column(db.Text)
    improvement_plan = db.Column(db.Text)
    recorded_at = db.Column(db.DateTime, default=datetime.utcnow)


class Recommendation(db.Model):
    __tablename__ = "recommendations"

    id = db.Column(db.Integer, primary_key=True)
    farmer_id = db.Column(db.Integer, db.ForeignKey("farmers.id"))
    agent_type = db.Column(db.String(50))     # crop / weather / soil / pest / market
    query = db.Column(db.Text)
    recommendation = db.Column(db.Text)
    problem_summary = db.Column(db.Text)
    recommended_action = db.Column(db.Text)
    alternative_option = db.Column(db.Text)
    risk_level = db.Column(db.String(20))
    estimated_cost = db.Column(db.String(100))
    expected_benefits = db.Column(db.Text)
    confidence_score = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Disease(db.Model):
    __tablename__ = "diseases"

    id = db.Column(db.Integer, primary_key=True)
    farmer_id = db.Column(db.Integer, db.ForeignKey("farmers.id"))
    image_path = db.Column(db.String(300))
    disease_name = db.Column(db.String(200))
    pest_type = db.Column(db.String(100))
    confidence_score = db.Column(db.Float)
    treatment = db.Column(db.Text)
    organic_solution = db.Column(db.Text)
    chemical_solution = db.Column(db.Text)
    prevention = db.Column(db.Text)
    raw_analysis = db.Column(db.Text)
    detected_at = db.Column(db.DateTime, default=datetime.utcnow)


class MarketPrice(db.Model):
    __tablename__ = "market_prices"

    id = db.Column(db.Integer, primary_key=True)
    crop_name = db.Column(db.String(100))
    market_name = db.Column(db.String(200))
    state = db.Column(db.String(100))
    min_price = db.Column(db.Float)
    max_price = db.Column(db.Float)
    modal_price = db.Column(db.Float)
    price_trend = db.Column(db.String(20))    # up / down / stable
    demand_level = db.Column(db.String(20))   # high / medium / low
    best_sell_time = db.Column(db.String(100))
    storage_advice = db.Column(db.Text)
    profit_estimate = db.Column(db.Float)
    recorded_at = db.Column(db.DateTime, default=datetime.utcnow)


class ChatHistory(db.Model):
    __tablename__ = "chat_history"

    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(100))
    farmer_id = db.Column(db.Integer, db.ForeignKey("farmers.id"))
    role = db.Column(db.String(20))           # user / assistant
    message = db.Column(db.Text)
    agent_used = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class UploadedImage(db.Model):
    __tablename__ = "uploaded_images"

    id = db.Column(db.Integer, primary_key=True)
    farmer_id = db.Column(db.Integer, db.ForeignKey("farmers.id"))
    filename = db.Column(db.String(300))
    original_name = db.Column(db.String(300))
    file_size = db.Column(db.Integer)
    image_type = db.Column(db.String(50))     # pest / disease / soil
    analysis_result = db.Column(db.Text)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)


class Report(db.Model):
    __tablename__ = "reports"

    id = db.Column(db.Integer, primary_key=True)
    farmer_id = db.Column(db.Integer, db.ForeignKey("farmers.id"))
    report_type = db.Column(db.String(50))    # pdf / csv / excel
    report_name = db.Column(db.String(200))
    file_path = db.Column(db.String(300))
    content_summary = db.Column(db.Text)
    generated_at = db.Column(db.DateTime, default=datetime.utcnow)


class GovernmentScheme(db.Model):
    __tablename__ = "government_schemes"

    id = db.Column(db.Integer, primary_key=True)
    scheme_name = db.Column(db.String(200))
    description = db.Column(db.Text)
    eligibility = db.Column(db.Text)
    benefits = db.Column(db.Text)
    application_process = db.Column(db.Text)
    state = db.Column(db.String(100), default="All India")
    category = db.Column(db.String(100))    # insurance / subsidy / credit etc.
    website = db.Column(db.String(300))
    is_active = db.Column(db.Boolean, default=True)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)
