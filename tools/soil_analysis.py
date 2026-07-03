"""
soil_analysis.py — Soil analysis tool with rule-based expert system
plus IBM Granite augmented recommendations.
"""

from typing import Any, Dict, List
from loguru import logger


class SoilAnalysisTool:
    """
    Rule-based soil analysis engine.
    Computes soil health scores and basic crop suitability
    without consuming an LLM call. The SoilHealthAgent handles
    the full AI-powered analysis.
    """

    # Crop suitability table: (min_pH, max_pH, min_N, min_P, min_K)
    CROP_SUITABILITY = {
        "Rice":        (5.5, 6.5, 200, 10, 100),
        "Wheat":       (6.0, 7.5, 250, 15, 120),
        "Maize":       (5.8, 7.0, 220, 12, 110),
        "Sugarcane":   (6.0, 7.5, 280, 18, 200),
        "Cotton":      (6.0, 7.5, 200, 15, 150),
        "Groundnut":   (5.5, 7.0, 100, 20, 120),
        "Soybean":     (6.0, 7.0, 150, 15, 100),
        "Tomato":      (5.5, 7.0, 250, 25, 200),
        "Potato":      (5.0, 6.5, 220, 20, 180),
        "Onion":       (6.0, 7.5, 200, 18, 150),
        "Chilli":      (5.5, 7.0, 220, 20, 180),
        "Banana":      (5.5, 7.0, 280, 22, 250),
        "Mango":       (5.5, 7.5, 150, 12, 100),
        "Coconut":     (5.5, 7.5, 200, 15, 200),
        "Turmeric":    (5.0, 7.5, 200, 18, 150),
    }

    def analyse(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Return quick soil health metrics and suitable crops."""
        ph = float(inputs.get("ph", 7.0))
        n = float(inputs.get("nitrogen", 200))
        p = float(inputs.get("phosphorus", 10))
        k = float(inputs.get("potassium", 100))
        moisture = float(inputs.get("moisture", 50))
        organic = float(inputs.get("organic_matter", 1.5))

        suitable = self._get_suitable_crops(ph, n, p, k)
        deficiencies = self._check_deficiencies(ph, n, p, k, moisture, organic)
        recommendations = self._get_fertilizer_dose(n, p, k)
        score = self._compute_health_score(ph, n, p, k, moisture, organic)

        return {
            "soil_health_score": score,
            "suitable_crops": suitable,
            "deficiencies": deficiencies,
            "fertilizer_recommendations": recommendations,
            "ph_status": self._ph_status(ph),
            "fertility_class": "High" if score >= 70 else "Medium" if score >= 40 else "Low",
        }

    def _get_suitable_crops(self, ph, n, p, k) -> List[str]:
        suited = []
        for crop, (min_ph, max_ph, min_n, min_p, min_k) in self.CROP_SUITABILITY.items():
            if min_ph <= ph <= max_ph and n >= min_n and p >= min_p and k >= min_k:
                suited.append(crop)
        return suited[:8]

    def _check_deficiencies(self, ph, n, p, k, moisture, organic) -> List[str]:
        issues = []
        if n < 150:    issues.append("Severe Nitrogen deficiency — pale yellow leaves expected")
        elif n < 250:  issues.append("Moderate Nitrogen deficiency — yellowing of older leaves")
        if p < 10:     issues.append("Severe Phosphorus deficiency — poor root development")
        elif p < 15:   issues.append("Moderate Phosphorus deficiency — delayed maturity")
        if k < 80:     issues.append("Severe Potassium deficiency — weak stems, tip burn")
        elif k < 110:  issues.append("Moderate Potassium deficiency — reduced disease resistance")
        if ph < 5.5:   issues.append("Acidic soil — aluminium/manganese toxicity risk")
        elif ph > 7.5: issues.append("Alkaline soil — micronutrient lock-up risk")
        if moisture < 30: issues.append("Low soil moisture — stress irrigation required")
        if organic < 1.0: issues.append("Low organic matter — poor water retention and microbial activity")
        return issues

    def _get_fertilizer_dose(self, n, p, k) -> Dict[str, str]:
        urea_needed = max(0, round((250 - n) / 0.46, 1))     # Urea 46% N
        dap_needed = max(0, round((20 - p) / 0.46, 1))       # DAP 46% P2O5
        mop_needed = max(0, round((120 - k) / 0.6, 1))       # MOP 60% K2O
        return {
            "Urea (kg/acre)": str(urea_needed),
            "DAP (kg/acre)": str(dap_needed),
            "MOP/SOP (kg/acre)": str(mop_needed),
            "Organic compost (tonnes/acre)": "2–3",
            "Note": "Apply basal dose at sowing, top-dress nitrogen in 2 splits.",
        }

    def _compute_health_score(self, ph, n, p, k, moisture, organic) -> int:
        score = 0
        if 6.0 <= ph <= 7.5:    score += 20
        elif 5.5 <= ph < 6.0 or 7.5 < ph <= 8.0: score += 10
        score += min(20, int(n / 280 * 20))
        score += min(15, int(p / 20 * 15))
        score += min(15, int(k / 200 * 15))
        if 40 <= moisture <= 70: score += 15
        elif 30 <= moisture < 40 or 70 < moisture <= 80: score += 8
        if organic >= 2.0: score += 15
        elif organic >= 1.0: score += 8
        return min(score, 100)

    def _ph_status(self, ph: float) -> str:
        if ph < 5.5:   return "Strongly Acidic"
        if ph < 6.0:   return "Moderately Acidic"
        if ph <= 7.0:  return "Neutral (Ideal)"
        if ph <= 7.5:  return "Mildly Alkaline"
        if ph <= 8.0:  return "Moderately Alkaline"
        return "Strongly Alkaline"
