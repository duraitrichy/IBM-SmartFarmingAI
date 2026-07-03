"""
soil_agent.py — Soil Health Agent (Agent 3).

Analyses NPK, pH, moisture and generates improvement plans.
"""

from typing import Any, Dict
from loguru import logger
from .base_agent import BaseAgent


SOIL_HEALTH_PROMPT = """You are a certified soil scientist and agricultural chemist.

Soil Test Results:
- Soil Type: {soil_type}
- pH: {ph}
- Nitrogen (N): {nitrogen} kg/ha
- Phosphorus (P): {phosphorus} kg/ha
- Potassium (K): {potassium} kg/ha
- Moisture: {moisture}%
- Organic Matter: {organic_matter}%
- Location: {location}
- Climate Zone: {climate_zone}
- Target Crop: {crop}

Interpret the above soil analysis and provide a COMPLETE SOIL HEALTH REPORT:

1. SOIL HEALTH SCORE — Rate 0–100 and explain each parameter's status.
2. DEFICIENCY ANALYSIS — Identify all deficiencies and their impact on crops.
3. SUITABLE CROPS — List top 5 crops best suited for this soil profile.
4. FERTILIZER RECOMMENDATIONS — Specific quantities (kg/acre) of NPK fertilizers.
5. ORGANIC MANURE PLAN — Compost, vermicompost, green manure quantities and schedule.
6. SOIL IMPROVEMENT PLAN — 12-month step-by-step soil rehabilitation schedule.
7. PH CORRECTION — If pH is outside 6.0–7.5, provide lime/sulfur application guide.
8. IRRIGATION ADVICE — Based on soil moisture retention capacity.
9. ORGANIC FARMING PATHWAY — Steps to transition to organic farming.
10. GOVERNMENT SOIL SCHEMES — Relevant soil health card schemes.
11. CONFIDENCE SCORE — Rate your recommendation (0.0 to 1.0).

Present results with specific measurements, timelines, and costs in INR."""


class SoilHealthAgent(BaseAgent):
    """Agent 3: Soil analysis and improvement planning."""

    # Optimal ranges for quick deficiency flagging
    OPTIMAL = {
        "ph": (6.0, 7.5),
        "nitrogen": (280, 560),
        "phosphorus": (11, 22),
        "potassium": (110, 280),
        "moisture": (40, 70),
        "organic_matter": (1.0, 3.0),
    }

    def run(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        logger.info("SoilHealthAgent.run() invoked")

        soil_score = self._compute_score(inputs)

        prompt = SOIL_HEALTH_PROMPT.format(
            soil_type=inputs.get("soil_type", "Loamy"),
            ph=inputs.get("ph", 7.0),
            nitrogen=inputs.get("nitrogen", 200),
            phosphorus=inputs.get("phosphorus", 10),
            potassium=inputs.get("potassium", 100),
            moisture=inputs.get("moisture", 50),
            organic_matter=inputs.get("organic_matter", 1.5),
            location=inputs.get("location", "India"),
            climate_zone=inputs.get("climate_zone", "Tropical"),
            crop=inputs.get("crop", "Not specified"),
        )

        raw_response = self.generate(prompt)

        return {
            **self._structured_response(
                problem_summary=f"Soil health analysis — computed score: {soil_score}/100",
                analysis=raw_response,
                recommended_action=self._extract_section(raw_response, "FERTILIZER"),
                alternative_option=self._extract_section(raw_response, "ORGANIC MANURE"),
                risk_level="High" if soil_score < 40 else ("Medium" if soil_score < 70 else "Low"),
                estimated_cost="₹2,000–₹8,000/acre for soil amendments (varies by deficiency)",
                expected_benefits="Improved soil fertility, 20–40% higher yield, reduced input cost over 3 years.",
                government_support="Soil Health Card Scheme (NMoSHC) — free soil testing every 2 years.",
                confidence_score=0.85,
            ),
            "soil_score": soil_score,
            "deficiencies": self._identify_deficiencies(inputs),
        }

    def _compute_score(self, inputs: Dict[str, Any]) -> int:
        """Simple weighted soil score 0–100."""
        score = 0
        weights = {"ph": 20, "nitrogen": 20, "phosphorus": 15, "potassium": 15, "moisture": 15, "organic_matter": 15}
        for param, weight in weights.items():
            val = inputs.get(param)
            if val is None:
                continue
            lo, hi = self.OPTIMAL[param]
            if lo <= val <= hi:
                score += weight
            elif val < lo:
                score += int(weight * val / lo)
            else:
                score += int(weight * hi / val)
        return min(score, 100)

    def _identify_deficiencies(self, inputs: Dict[str, Any]) -> list:
        issues = []
        for param, (lo, hi) in self.OPTIMAL.items():
            val = inputs.get(param)
            if val is None:
                continue
            if val < lo:
                issues.append(f"Low {param}: {val} (optimal {lo}–{hi})")
            elif val > hi:
                issues.append(f"High {param}: {val} (optimal {lo}–{hi})")
        return issues

    def _extract_section(self, text: str, keyword: str) -> str:
        lines = text.split("\n")
        capturing, result = False, []
        for line in lines:
            if keyword.lower() in line.lower():
                capturing = True
                continue
            if capturing:
                if any(str(i) + "." in line for i in range(1, 12)) and result:
                    break
                result.append(line)
        return "\n".join(result).strip() or text[:300]
