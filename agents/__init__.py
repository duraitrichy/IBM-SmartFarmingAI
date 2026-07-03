"""Agents package — multi-agent AI architecture for SmartFarmingAI."""

from .crop_agent import CropAdvisoryAgent
from .weather_agent import WeatherIrrigationAgent
from .soil_agent import SoilHealthAgent
from .pest_agent import PestDiseaseAgent
from .market_agent import MarketIntelligenceAgent
from .orchestrator import MasterOrchestrator

__all__ = [
    "CropAdvisoryAgent",
    "WeatherIrrigationAgent",
    "SoilHealthAgent",
    "PestDiseaseAgent",
    "MarketIntelligenceAgent",
    "MasterOrchestrator",
]
