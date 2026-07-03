"""
base_agent.py — Abstract base class for all SmartFarmingAI agents.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict
from loguru import logger
from ibm_watsonx_ai import APIClient, Credentials
from ibm_watsonx_ai.foundation_models import ModelInference
from ibm_watsonx_ai.foundation_models.utils.enums import DecodingMethods
from config import ActiveConfig


class BaseAgent(ABC):
    """Shared IBM Granite + watsonx.ai plumbing used by every agent."""

    def __init__(self):
        self.config = ActiveConfig
        self._llm: ModelInference | None = None
        logger.info(f"{self.__class__.__name__} initialised.")

    @property
    def llm(self) -> ModelInference:
        if self._llm is None:
            self._llm = self._build_llm()
        return self._llm

    def _build_llm(self) -> ModelInference:
        credentials = Credentials(
            url=self.config.IBM_WATSONX_URL,
            api_key=self.config.IBM_API_KEY,
        )
        client = APIClient(credentials=credentials, project_id=self.config.IBM_PROJECT_ID)
        return ModelInference(
            model_id=self.config.GRANITE_INSTRUCT_MODEL,
            api_client=client,
            project_id=self.config.IBM_PROJECT_ID,
            validate=False,
            params={
                "decoding_method": DecodingMethods.SAMPLE,
                "max_new_tokens": self.config.GRANITE_MAX_TOKENS,
                "temperature": self.config.GRANITE_TEMPERATURE,
                "top_p": self.config.GRANITE_TOP_P,
            },
        )

    def generate(self, prompt: str) -> str:
        """Send *prompt* to IBM Granite and return the text response."""
        try:
            response = self.llm.generate_text(prompt=prompt)
            return response.strip() if isinstance(response, str) else str(response)
        except Exception as exc:
            logger.error(f"{self.__class__.__name__} generation error: {exc}")
            return f"Error generating response: {exc}"

    def _structured_response(
        self,
        problem_summary: str,
        analysis: str,
        recommended_action: str,
        alternative_option: str,
        risk_level: str,
        estimated_cost: str,
        expected_benefits: str,
        government_support: str,
        confidence_score: float,
    ) -> Dict[str, Any]:
        """Build the standardised response envelope required by the spec."""
        return {
            "problem_summary": problem_summary,
            "analysis": analysis,
            "recommended_action": recommended_action,
            "alternative_option": alternative_option,
            "risk_level": risk_level,
            "estimated_cost": estimated_cost,
            "expected_benefits": expected_benefits,
            "government_support": government_support,
            "confidence_score": round(confidence_score, 2),
        }

    @abstractmethod
    def run(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the agent's main task and return a structured response."""
