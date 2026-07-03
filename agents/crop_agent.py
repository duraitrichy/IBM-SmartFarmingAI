"""
crop_agent.py — Crop Advisory Agent (Agent 1).

Responsibilities:
  • Crop recommendation based on soil, weather, and budget
  • Seed recommendation
  • Fertilizer suggestions
  • Yield improvement advice
  • Harvest prediction timeline
"""

from typing import Any, Dict
from loguru import logger
from .base_agent import BaseAgent


CROP_ADVISORY_PROMPT = """You are an expert agricultural advisor specialised in Indian farming.

Farmer Profile:
- Crop of Interest: {crop}
- Soil Type: {soil_type}
- Soil pH: {soil_ph}
- Nitrogen (N): {nitrogen} kg/ha
- Phosphorus (P): {phosphorus} kg/ha
- Potassium (K): {potassium} kg/ha
- Location: {location}
- Season: {season}
- Farm Size: {farm_size} acres
- Budget: ₹{budget}
- Water Source: {water_source}
- Previous Yield: {previous_yield} quintals/acre
- Farmer Experience: {experience} years

Based on the above profile, provide a COMPLETE FARMING PLAN covering:

1. CROP RECOMMENDATION — Top 3 crops ranked by suitability with reasons.
2. SEED VARIETIES — Best seed varieties, certified sources, and quantity per acre.
3. FERTILIZER SCHEDULE — Month-by-month schedule (chemical + organic).
4. YIELD IMPROVEMENT — 5 specific techniques to increase yield.
5. HARVEST PREDICTION — Expected timeline, indicators of readiness, post-harvest handling.
6. IRRIGATION PLAN — Schedule and water requirement per stage.
7. ESTIMATED INCOME — Projected income, cost breakdown, and profit margin.
8. RISK FACTORS — Key risks and mitigation strategies.
9. GOVERNMENT SCHEMES — Relevant schemes (PM-KISAN, crop insurance, seed subsidies).
10. CONFIDENCE SCORE — Rate your recommendation (0.0 to 1.0).

Respond in a clear, structured format suitable for a farmer with {experience} years of experience."""


class CropAdvisoryAgent(BaseAgent):
    """Agent 1: Comprehensive crop advisory using IBM Granite."""

    def run(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        logger.info("CropAdvisoryAgent.run() invoked")

        prompt = CROP_ADVISORY_PROMPT.format(
            crop=inputs.get("crop", "Not specified"),
            soil_type=inputs.get("soil_type", "Unknown"),
            soil_ph=inputs.get("soil_ph", 7.0),
            nitrogen=inputs.get("nitrogen", 0),
            phosphorus=inputs.get("phosphorus", 0),
            potassium=inputs.get("potassium", 0),
            location=inputs.get("location", "India"),
            season=inputs.get("season", "Kharif"),
            farm_size=inputs.get("farm_size", 1),
            budget=inputs.get("budget", 10000),
            water_source=inputs.get("water_source", "Rain-fed"),
            previous_yield=inputs.get("previous_yield", 0),
            experience=inputs.get("experience", 0),
        )

        raw_response = self.generate(prompt)

        return self._structured_response(
            problem_summary=f"Crop advisory for {inputs.get('crop', 'unspecified crop')} on {inputs.get('farm_size', 1)} acres",
            analysis=raw_response,
            recommended_action=self._extract_section(raw_response, "CROP RECOMMENDATION"),
            alternative_option=self._extract_section(raw_response, "ALTERNATIVE"),
            risk_level=self._extract_risk_level(raw_response),
            estimated_cost=self._extract_section(raw_response, "ESTIMATED INCOME"),
            expected_benefits=self._extract_section(raw_response, "YIELD IMPROVEMENT"),
            government_support=self._extract_section(raw_response, "GOVERNMENT SCHEMES"),
            confidence_score=self._extract_confidence(raw_response),
        )

    # ── Extraction helpers ────────────────────────────────────────────────

    def _extract_section(self, text: str, section_key: str) -> str:
        lines = text.split("\n")
        capturing = False
        result = []
        for line in lines:
            if section_key.lower() in line.lower():
                capturing = True
                continue
            if capturing:
                if any(f"{i}." in line or line.startswith("#") for i in range(1, 11)):
                    if result:
                        break
                result.append(line)
        return "\n".join(result).strip() or text[:300]

    def _extract_risk_level(self, text: str) -> str:
        text_lower = text.lower()
        if "high risk" in text_lower:
            return "High"
        if "medium risk" in text_lower or "moderate risk" in text_lower:
            return "Medium"
        return "Low"

    def _extract_confidence(self, text: str) -> float:
        import re
        matches = re.findall(r"confidence[^\d]*([0-9]\.[0-9]+)", text, re.IGNORECASE)
        if matches:
            try:
                return min(float(matches[0]), 1.0)
            except ValueError:
                pass
        return 0.82
