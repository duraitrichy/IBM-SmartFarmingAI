"""
orchestrator.py — Master Orchestrator Agent.

Understands user intent, routes to the correct specialist agent,
combines outputs, and maintains conversation memory.
"""

import re
from typing import Any, Dict, List, Optional
from loguru import logger
from .base_agent import BaseAgent
from .crop_agent import CropAdvisoryAgent
from .weather_agent import WeatherIrrigationAgent
from .soil_agent import SoilHealthAgent
from .pest_agent import PestDiseaseAgent
from .market_agent import MarketIntelligenceAgent


INTENT_CLASSIFICATION_PROMPT = """You are an agricultural AI assistant. Classify the farmer's query into EXACTLY ONE category.

Categories:
- CROP      : crop selection, seed, fertilizer, yield, harvest, farming plan
- WEATHER   : weather, rain, irrigation, temperature, humidity, watering
- SOIL      : soil test, NPK, pH, soil health, soil improvement
- PEST      : pest, disease, insect, fungus, yellow leaves, brown spots, image analysis
- MARKET    : price, sell, mandi, market, profit, income, storage
- GENERAL   : greeting, general farming question, scheme information, other

Query: {query}

Respond with ONLY ONE WORD from the list above. No explanation."""

SYNTHESIS_PROMPT = """You are a senior agricultural advisor summarising multiple AI agent reports.

Farmer's Question: {query}

Agent Reports:
{agent_reports}

Write a COHERENT, CONCISE summary that:
1. Directly answers the farmer's question in 2–3 sentences
2. Highlights the most important action items (numbered)
3. Notes any urgent risks or opportunities
4. Suggests next steps

Keep the language simple and practical. Farmer has {experience} years of experience."""


class ConversationMemory:
    """Simple sliding-window conversation memory."""

    def __init__(self, max_turns: int = 10):
        self.max_turns = max_turns
        self.history: List[Dict[str, str]] = []

    def add(self, role: str, content: str) -> None:
        self.history.append({"role": role, "content": content})
        if len(self.history) > self.max_turns * 2:
            self.history = self.history[-(self.max_turns * 2):]

    def format_history(self, last_n: int = 5) -> str:
        recent = self.history[-(last_n * 2):]
        return "\n".join(f"{m['role'].upper()}: {m['content'][:200]}" for m in recent)

    def clear(self) -> None:
        self.history.clear()


class MasterOrchestrator(BaseAgent):
    """Central orchestrator — intent detection, agent routing, and synthesis."""

    def __init__(self):
        super().__init__()
        self._crop_agent: Optional[CropAdvisoryAgent] = None
        self._weather_agent: Optional[WeatherIrrigationAgent] = None
        self._soil_agent: Optional[SoilHealthAgent] = None
        self._pest_agent: Optional[PestDiseaseAgent] = None
        self._market_agent: Optional[MarketIntelligenceAgent] = None
        self.memory = ConversationMemory()

    # ── Agent singletons (lazy) ───────────────────────────────────────────

    @property
    def crop_agent(self) -> CropAdvisoryAgent:
        if not self._crop_agent:
            self._crop_agent = CropAdvisoryAgent()
        return self._crop_agent

    @property
    def weather_agent(self) -> WeatherIrrigationAgent:
        if not self._weather_agent:
            self._weather_agent = WeatherIrrigationAgent()
        return self._weather_agent

    @property
    def soil_agent(self) -> SoilHealthAgent:
        if not self._soil_agent:
            self._soil_agent = SoilHealthAgent()
        return self._soil_agent

    @property
    def pest_agent(self) -> PestDiseaseAgent:
        if not self._pest_agent:
            self._pest_agent = PestDiseaseAgent()
        return self._pest_agent

    @property
    def market_agent(self) -> MarketIntelligenceAgent:
        if not self._market_agent:
            self._market_agent = MarketIntelligenceAgent()
        return self._market_agent

    # ── Main entry point ──────────────────────────────────────────────────

    def run(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        query = inputs.get("query", "").strip()
        if not query:
            return {"error": "Empty query provided."}

        logger.info(f"Orchestrator received: {query[:80]}")

        # Add user message to memory
        self.memory.add("user", query)

        # Classify intent
        intent = self._classify_intent(query)
        logger.info(f"Detected intent: {intent}")

        # Route to agent(s)
        agent_results: Dict[str, Any] = {}

        if intent == "CROP":
            agent_results["crop"] = self.crop_agent.run(inputs)
        elif intent == "WEATHER":
            agent_results["weather"] = self.weather_agent.run(inputs)
        elif intent == "SOIL":
            agent_results["soil"] = self.soil_agent.run(inputs)
        elif intent == "PEST":
            agent_results["pest"] = self.pest_agent.run(inputs)
        elif intent == "MARKET":
            agent_results["market"] = self.market_agent.run(inputs)
        else:
            # GENERAL — use crop agent as fallback with RAG context
            agent_results["general"] = self._handle_general(query, inputs)

        # Synthesise response
        synthesis = self._synthesise(query, agent_results, inputs.get("experience", 0))

        # Save assistant response to memory
        self.memory.add("assistant", synthesis)

        return {
            "intent": intent,
            "synthesis": synthesis,
            "agent_results": agent_results,
            "memory_turns": len(self.memory.history) // 2,
        }

    # ── Intent classification ─────────────────────────────────────────────

    def _classify_intent(self, query: str) -> str:
        # Rule-based fast path (covers common patterns without LLM call)
        q = query.lower()
        rules = [
            (["weather", "rain", "irrigation", "irrigate", "water", "humidity", "temperature"], "WEATHER"),
            (["soil", "npk", "nitrogen", "phosphorus", "potassium", "ph", "soil test"], "SOIL"),
            (["pest", "disease", "insect", "fungus", "yellow", "brown", "spots", "wilt", "blight"], "PEST"),
            (["price", "market", "sell", "mandi", "profit", "income", "storage", "rate"], "MARKET"),
            (["crop", "seed", "fertilizer", "yield", "harvest", "sow", "plant", "grow"], "CROP"),
        ]
        for keywords, intent in rules:
            if any(k in q for k in keywords):
                return intent

        # LLM fallback for ambiguous queries
        try:
            prompt = INTENT_CLASSIFICATION_PROMPT.format(query=query)
            result = self.generate(prompt).strip().upper()
            valid = {"CROP", "WEATHER", "SOIL", "PEST", "MARKET", "GENERAL"}
            return result if result in valid else "GENERAL"
        except Exception as exc:
            logger.warning(f"Intent classification failed: {exc}")
            return "GENERAL"

    # ── Synthesis ─────────────────────────────────────────────────────────

    def _synthesise(self, query: str, agent_results: Dict, experience: int) -> str:
        if not agent_results:
            return "I could not process your query. Please try again."

        # Flatten agent reports
        report_lines = []
        for agent_name, result in agent_results.items():
            if isinstance(result, dict):
                analysis = result.get("analysis", result.get("synthesis", str(result)))
                report_lines.append(f"[{agent_name.upper()} AGENT]\n{analysis[:600]}")

        if not report_lines:
            first = next(iter(agent_results.values()))
            return first.get("analysis", str(first))

        prompt = SYNTHESIS_PROMPT.format(
            query=query,
            agent_reports="\n\n".join(report_lines),
            experience=experience,
        )
        try:
            return self.generate(prompt)
        except Exception as exc:
            logger.warning(f"Synthesis failed: {exc}")
            return report_lines[0]

    # ── General handler ───────────────────────────────────────────────────

    def _handle_general(self, query: str, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Handle general queries with a direct Granite prompt."""
        history = self.memory.format_history()
        prompt = f"""You are a helpful agricultural AI assistant.

Conversation History:
{history}

Farmer's Question: {query}

Provide a helpful, accurate, and practical response about farming, agriculture, or government schemes.
Keep it concise and relevant to Indian farming context."""
        response = self.generate(prompt)
        return {
            "analysis": response,
            "problem_summary": query,
            "confidence_score": 0.80,
            "risk_level": "Low",
        }
