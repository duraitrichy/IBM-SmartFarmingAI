"""Database package — exposes the shared SQLAlchemy instance and all models."""

from .db import db, init_db
from .models import (
    Farmer,
    WeatherRecord,
    SoilRecord,
    Recommendation,
    Disease,
    MarketPrice,
    ChatHistory,
    UploadedImage,
    Report,
    GovernmentScheme,
)

__all__ = [
    "db",
    "init_db",
    "Farmer",
    "WeatherRecord",
    "SoilRecord",
    "Recommendation",
    "Disease",
    "MarketPrice",
    "ChatHistory",
    "UploadedImage",
    "Report",
    "GovernmentScheme",
]
