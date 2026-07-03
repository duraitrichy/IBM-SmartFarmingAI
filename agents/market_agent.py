"""
market_agent.py — Market Intelligence Agent (Agent 5).

Provides current prices, forecasts, nearby markets,
storage advice, and profit estimation.
"""

from typing import Any, Dict, List
from loguru import logger
from .base_agent import BaseAgent


MARKET_INTELLIGENCE_PROMPT = """You are an agricultural market analyst and commodity trading expert.

Farmer Query:
- Crop: {crop}
- Quantity Available: {quantity} quintals
- Quality Grade: {quality_grade}
- Current Location: {location}
- Storage Facility: {storage}
- Harvest Date: {harvest_date}
- Transportation Available: {transport}
- Market Data: {market_data}

Provide a COMPLETE MARKET INTELLIGENCE REPORT:

1. CURRENT MARKET PRICES — Present prices in top 5 nearby mandis (₹/quintal).
2. PRICE ANALYSIS — Minimum, maximum, and modal price with trend (up/down/stable).
3. DEMAND FORECAST — Demand level and 30-day price outlook.
4. BEST SELLING TIME — Optimal date/week to sell (price vs. storage cost analysis).
5. NEARBY MARKETS — Ranked list with distance, commission charges, and transport cost.
6. STORAGE ADVICE — If price is expected to rise: storage duration, cost, and risk.
7. PROFIT ESTIMATION — Net profit after all deductions per quintal and total.
8. MARKET ENTRY STRATEGY — Direct sale vs. FPO vs. e-NAM platform comparison.
9. VALUE ADDITION — Processing/grading options to increase selling price.
10. GOVERNMENT SUPPORT — MSP rates, PM-AASHA scheme, e-NAM registration benefits.
11. CONFIDENCE SCORE — Rate your market prediction (0.0 to 1.0).

Provide concrete numbers and actionable advice."""


class MarketIntelligenceAgent(BaseAgent):
    """Agent 5: Real-time market intelligence and profit optimisation."""

    # Fallback MSP data (2024-25) — will be overridden by live API data
    MSP_2024 = {
        "rice": 2300, "wheat": 2275, "maize": 2090, "sorghum": 3371,
        "bajra": 2625, "cotton": 7521, "groundnut": 6783, "sunflower": 7280,
        "soybean": 4892, "sugarcane": 340, "tomato": 1000, "onion": 800,
        "potato": 600, "chilli": 5000, "turmeric": 9000,
    }

    def run(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        logger.info("MarketIntelligenceAgent.run() invoked")

        crop_lower = inputs.get("crop", "").lower()
        msp = self.MSP_2024.get(crop_lower, "Contact local mandi for MSP")
        market_data_str = self._format_market_data(inputs.get("market_data", []), msp)

        prompt = MARKET_INTELLIGENCE_PROMPT.format(
            crop=inputs.get("crop", "Unknown"),
            quantity=inputs.get("quantity", 0),
            quality_grade=inputs.get("quality_grade", "A"),
            location=inputs.get("location", "India"),
            storage=inputs.get("storage", "None"),
            harvest_date=inputs.get("harvest_date", "Recent"),
            transport=inputs.get("transport", "Available"),
            market_data=market_data_str,
        )

        raw_response = self.generate(prompt)

        return {
            **self._structured_response(
                problem_summary=f"Market intelligence for {inputs.get('quantity', 0)} quintals of {inputs.get('crop', 'crop')}",
                analysis=raw_response,
                recommended_action=self._extract_section(raw_response, "BEST SELLING TIME"),
                alternative_option=self._extract_section(raw_response, "VALUE ADDITION"),
                risk_level=self._extract_risk_level(raw_response),
                estimated_cost="Transport + commission: typically ₹50–₹150/quintal",
                expected_benefits=self._extract_section(raw_response, "PROFIT ESTIMATION"),
                government_support=self._extract_section(raw_response, "GOVERNMENT SUPPORT"),
                confidence_score=self._extract_confidence(raw_response),
            ),
            "msp": msp,
        }

    def _format_market_data(self, market_data: List[Dict], msp) -> str:
        if not market_data:
            return f"MSP (government support price): ₹{msp}/quintal. Live mandi data not available."
        lines = [f"MSP: ₹{msp}/quintal"]
        for m in market_data:
            lines.append(
                f"  {m.get('market', 'Unknown Market')} — Min: ₹{m.get('min_price', '-')}, "
                f"Max: ₹{m.get('max_price', '-')}, Modal: ₹{m.get('modal_price', '-')}/quintal"
            )
        return "\n".join(lines)

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

    def _extract_risk_level(self, text: str) -> str:
        tl = text.lower()
        if any(k in tl for k in ["price crash", "oversupply", "high risk"]):
            return "High"
        if any(k in tl for k in ["price drop", "moderate risk", "caution"]):
            return "Medium"
        return "Low"

    def _extract_confidence(self, text: str) -> float:
        import re
        m = re.findall(r"confidence[^\d]*([0-9]\.[0-9]+)", text, re.IGNORECASE)
        if m:
            try:
                return min(float(m[0]), 1.0)
            except ValueError:
                pass
        return 0.75
