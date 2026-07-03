"""
weather_agent.py — Weather & Irrigation Agent (Agent 2).

Responsibilities:
  • Interpret current weather data
  • Analyse 7-day forecast
  • Generate irrigation schedule
  • Water-saving recommendations
"""

from typing import Any, Dict
from loguru import logger
from .base_agent import BaseAgent


WEATHER_IRRIGATION_PROMPT = """You are an expert agro-meteorologist and irrigation engineer.

Current Weather Data:
- Location: {location}
- Temperature: {temperature}°C
- Humidity: {humidity}%
- Wind Speed: {wind_speed} km/h
- Rainfall (last 24h): {rainfall} mm
- Weather Condition: {weather_condition}
- UV Index: {uv_index}
- Season: {season}
- Crop: {crop}
- Soil Moisture: {soil_moisture}%
- Farm Size: {farm_size} acres

7-Day Forecast Summary:
{forecast_summary}

Based on the above data, provide:

1. WEATHER ANALYSIS — Impact of current weather on the mentioned crop.
2. RAINFALL PREDICTION — Expected rainfall and soil moisture implications.
3. TEMPERATURE ANALYSIS — Heat/cold stress risk for the crop.
4. IRRIGATION SCHEDULE — Exact schedule for the next 7 days (date, time, duration, water volume).
5. WATER-SAVING TIPS — 5 practical techniques (drip, mulching, etc.).
6. PEST & DISEASE WEATHER RISK — Conditions that may trigger disease outbreaks.
7. ADVISORY ALERTS — Critical weather alerts the farmer must act on NOW.
8. CONFIDENCE SCORE — Rate your recommendation (0.0 to 1.0).

Use simple language suitable for a field farmer."""


class WeatherIrrigationAgent(BaseAgent):
    """Agent 2: Weather analysis and smart irrigation scheduling."""

    def run(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        logger.info("WeatherIrrigationAgent.run() invoked")

        forecast_lines = []
        for day in inputs.get("forecast", []):
            forecast_lines.append(
                f"  {day.get('date','')}: {day.get('condition','')} | "
                f"Max {day.get('max_temp','-')}°C | Min {day.get('min_temp','-')}°C | "
                f"Rain {day.get('rain_prob',0)}%"
            )
        forecast_summary = "\n".join(forecast_lines) or "Forecast data unavailable."

        prompt = WEATHER_IRRIGATION_PROMPT.format(
            location=inputs.get("location", "India"),
            temperature=inputs.get("temperature", 30),
            humidity=inputs.get("humidity", 60),
            wind_speed=inputs.get("wind_speed", 10),
            rainfall=inputs.get("rainfall", 0),
            weather_condition=inputs.get("weather_condition", "Clear"),
            uv_index=inputs.get("uv_index", 5),
            season=inputs.get("season", "Kharif"),
            crop=inputs.get("crop", "Rice"),
            soil_moisture=inputs.get("soil_moisture", 50),
            farm_size=inputs.get("farm_size", 1),
            forecast_summary=forecast_summary,
        )

        raw_response = self.generate(prompt)

        return self._structured_response(
            problem_summary=f"Weather & irrigation advisory for {inputs.get('location', 'your farm')}",
            analysis=raw_response,
            recommended_action=self._extract_section(raw_response, "IRRIGATION SCHEDULE"),
            alternative_option=self._extract_section(raw_response, "WATER-SAVING TIPS"),
            risk_level=self._extract_risk_level(raw_response),
            estimated_cost="Water cost depends on irrigation method and local rates.",
            expected_benefits="Optimal water use, reduced electricity cost, improved yield.",
            government_support="PM Krishi Sinchai Yojana — check eligibility for drip/sprinkler subsidies.",
            confidence_score=0.88,
        )

    def _extract_section(self, text: str, keyword: str) -> str:
        lines = text.split("\n")
        capturing, result = False, []
        for line in lines:
            if keyword.lower() in line.lower():
                capturing = True
                continue
            if capturing:
                if any(str(i) + "." in line for i in range(1, 9)) and result:
                    break
                result.append(line)
        return "\n".join(result).strip() or text[:300]

    def _extract_risk_level(self, text: str) -> str:
        tl = text.lower()
        if any(k in tl for k in ["severe", "extreme", "critical", "high risk"]):
            return "High"
        if any(k in tl for k in ["moderate", "medium", "caution"]):
            return "Medium"
        return "Low"
