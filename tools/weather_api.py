"""
weather_api.py — OpenWeatherMap integration for real-time weather data.
"""

from typing import Any, Dict, List, Optional
import requests
from loguru import logger
from config import ActiveConfig


class WeatherAPI:
    """Fetches current weather and 7-day forecasts from OpenWeatherMap."""

    BASE = ActiveConfig.WEATHER_BASE_URL
    API_KEY = ActiveConfig.WEATHER_API_KEY

    def get_current(self, city: str) -> Dict[str, Any]:
        """Get current weather for a city."""
        if not self.API_KEY:
            logger.warning("WEATHER_API_KEY not set — returning mock data.")
            return self._mock_current(city)

        try:
            resp = requests.get(
                f"{self.BASE}/weather",
                params={"q": city, "appid": self.API_KEY, "units": "metric"},
                timeout=10,
            )
            resp.raise_for_status()
            data = resp.json()
            return {
                "location": city,
                "temperature": data["main"]["temp"],
                "feels_like": data["main"]["feels_like"],
                "humidity": data["main"]["humidity"],
                "wind_speed": data["wind"]["speed"] * 3.6,  # m/s → km/h
                "rainfall": data.get("rain", {}).get("1h", 0),
                "weather_condition": data["weather"][0]["description"].title(),
                "uv_index": 5,  # Requires separate UV endpoint
                "visibility": data.get("visibility", 10000) / 1000,  # m → km
                "pressure": data["main"]["pressure"],
                "icon": data["weather"][0]["icon"],
            }
        except requests.RequestException as exc:
            logger.error(f"Weather API error for {city}: {exc}")
            return self._mock_current(city)

    def get_forecast(self, city: str, days: int = 7) -> List[Dict[str, Any]]:
        """Get daily forecast for up to 7 days."""
        if not self.API_KEY:
            return self._mock_forecast(days)

        try:
            resp = requests.get(
                f"{self.BASE}/forecast",
                params={"q": city, "appid": self.API_KEY, "units": "metric", "cnt": days * 8},
                timeout=10,
            )
            resp.raise_for_status()
            raw = resp.json()["list"]

            # Aggregate by date
            daily: Dict[str, Dict] = {}
            for item in raw:
                date = item["dt_txt"].split(" ")[0]
                if date not in daily:
                    daily[date] = {
                        "date": date,
                        "temps": [],
                        "rain_prob": 0,
                        "condition": item["weather"][0]["description"].title(),
                    }
                daily[date]["temps"].append(item["main"]["temp"])
                daily[date]["rain_prob"] = max(
                    daily[date]["rain_prob"],
                    int(item.get("pop", 0) * 100),
                )

            forecast = []
            for d in list(daily.values())[:days]:
                forecast.append({
                    "date": d["date"],
                    "max_temp": round(max(d["temps"]), 1),
                    "min_temp": round(min(d["temps"]), 1),
                    "rain_prob": d["rain_prob"],
                    "condition": d["condition"],
                })
            return forecast
        except requests.RequestException as exc:
            logger.error(f"Forecast API error for {city}: {exc}")
            return self._mock_forecast(days)

    # ── Mock fallback data ────────────────────────────────────────────────

    def _mock_current(self, city: str) -> Dict[str, Any]:
        return {
            "location": city,
            "temperature": 30.5,
            "feels_like": 33.0,
            "humidity": 65,
            "wind_speed": 12.5,
            "rainfall": 0,
            "weather_condition": "Partly Cloudy",
            "uv_index": 6,
            "visibility": 10,
            "pressure": 1013,
            "icon": "02d",
        }

    def _mock_forecast(self, days: int) -> List[Dict[str, Any]]:
        from datetime import date, timedelta
        import random
        base = date.today()
        return [
            {
                "date": str(base + timedelta(days=i)),
                "max_temp": round(30 + random.uniform(-3, 5), 1),
                "min_temp": round(22 + random.uniform(-2, 3), 1),
                "rain_prob": random.randint(10, 70),
                "condition": random.choice(["Sunny", "Partly Cloudy", "Thunderstorm", "Light Rain"]),
            }
            for i in range(days)
        ]
