"""
pest_agent.py — Pest & Disease Detection Agent (Agent 4).

Uses IBM Granite Vision for image-based disease/pest identification.
Also handles text-based symptom descriptions via Granite Instruct.
"""

import base64
from pathlib import Path
from typing import Any, Dict
from loguru import logger
from ibm_watsonx_ai import Credentials
from ibm_watsonx_ai.foundation_models import ModelInference
from .base_agent import BaseAgent
from config import ActiveConfig


SYMPTOM_PROMPT = """You are a plant pathologist and pest management expert.

Farmer's Description:
- Crop: {crop}
- Symptoms: {symptoms}
- Affected Area: {affected_area}% of field
- Duration: {duration}
- Weather Conditions: {weather}
- Location: {location}

Provide a COMPLETE PEST & DISEASE DIAGNOSIS:

1. DISEASE/PEST IDENTIFICATION — Most likely disease or pest (top 3 with probability %).
2. CAUSE — Pathogen/pest type, causal organism.
3. CONFIDENCE SCORE — 0.0 to 1.0 for your diagnosis.
4. TREATMENT PLAN — Immediate action steps (within 24 hours).
5. ORGANIC SOLUTION — Neem oil, trichoderma, bio-pesticide options with doses.
6. CHEMICAL SOLUTION — Fungicide/insecticide with trade name, dose (ml/L), and safety precautions.
7. PREVENTION METHODS — 5 preventive measures for next season.
8. SPREAD RISK — Risk of spreading to neighbouring crops.
9. ESTIMATED CROP LOSS — % yield loss if untreated vs. treated.
10. GOVERNMENT ADVISORY — Any state/central pest outbreak alerts.

Use simple, actionable language the farmer can implement immediately."""

VISION_PROMPT = """Analyse this plant/crop image as an expert plant pathologist.

Crop: {crop}
Location: {location}

Identify:
1. Disease/Pest Name (most likely)
2. Confidence Score (0.0–1.0)
3. Visual Symptoms Observed
4. Immediate Treatment Required
5. Organic Treatment Option
6. Chemical Treatment Option (with safety precautions)
7. Prevention for future seasons

Be specific, practical, and mention exact product names and dosages where possible."""


class PestDiseaseAgent(BaseAgent):
    """Agent 4: Pest and disease detection via image or symptom description."""

    def __init__(self):
        super().__init__()
        self._vision_llm: ModelInference | None = None

    @property
    def vision_llm(self) -> ModelInference:
        if self._vision_llm is None:
            credentials = Credentials(
                url=self.config.IBM_WATSONX_URL,
                api_key=self.config.IBM_API_KEY,
            )
            from ibm_watsonx_ai.foundation_models.utils.enums import DecodingMethods
            self._vision_llm = ModelInference(
                model_id=self.config.GRANITE_VISION_MODEL,
                credentials=credentials,
                project_id=self.config.IBM_PROJECT_ID,
                params={
                    "decoding_method": DecodingMethods.SAMPLE,
                    "max_new_tokens": 800,
                    "temperature": 0.5,
                },
            )
        return self._vision_llm

    def run(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        logger.info("PestDiseaseAgent.run() invoked")

        image_path = inputs.get("image_path")
        if image_path and Path(image_path).exists():
            return self._analyse_image(image_path, inputs)
        return self._analyse_symptoms(inputs)

    # ── Image-based analysis ──────────────────────────────────────────────

    def _analyse_image(self, image_path: str, inputs: Dict[str, Any]) -> Dict[str, Any]:
        logger.info(f"Analysing image: {image_path}")
        try:
            encoded = self._encode_image(image_path)
            prompt = VISION_PROMPT.format(
                crop=inputs.get("crop", "Unknown crop"),
                location=inputs.get("location", "India"),
            )
            # IBM Granite Vision multimodal call
            response = self.vision_llm.generate_text(
                prompt=prompt,
                images=[{"data": encoded, "media_type": "image/jpeg"}],
            )
            raw = response.strip() if isinstance(response, str) else str(response)
        except Exception as exc:
            logger.warning(f"Vision model failed, falling back to symptom analysis: {exc}")
            return self._analyse_symptoms(inputs)

        confidence = self._extract_confidence(raw)
        return self._structured_response(
            problem_summary=f"Image-based pest/disease analysis for {inputs.get('crop', 'crop')}",
            analysis=raw,
            recommended_action=self._extract_section(raw, "Treatment Required"),
            alternative_option=self._extract_section(raw, "Organic"),
            risk_level="High" if confidence < 0.6 else "Medium",
            estimated_cost="₹500–₹2,000 for treatment (varies by area and product)",
            expected_benefits="Prevent crop loss, protect neighbouring crops.",
            government_support="Contact State Agriculture Department for pest outbreak compensation.",
            confidence_score=confidence,
        )

    # ── Text/symptom-based analysis ────────────────────────────────────────

    def _analyse_symptoms(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        prompt = SYMPTOM_PROMPT.format(
            crop=inputs.get("crop", "Unknown"),
            symptoms=inputs.get("symptoms", "Not described"),
            affected_area=inputs.get("affected_area", 10),
            duration=inputs.get("duration", "Unknown"),
            weather=inputs.get("weather", "Normal"),
            location=inputs.get("location", "India"),
        )
        raw = self.generate(prompt)
        return self._structured_response(
            problem_summary=f"Symptom-based diagnosis: {inputs.get('symptoms', 'unspecified symptoms')}",
            analysis=raw,
            recommended_action=self._extract_section(raw, "TREATMENT PLAN"),
            alternative_option=self._extract_section(raw, "ORGANIC SOLUTION"),
            risk_level=self._extract_risk_level(raw),
            estimated_cost="₹300–₹1,500/acre treatment cost (varies by severity)",
            expected_benefits="Reduce yield loss from pest/disease damage.",
            government_support="PM Fasal Bima Yojana covers crop loss due to pest outbreaks.",
            confidence_score=self._extract_confidence(raw),
        )

    # ── Helpers ───────────────────────────────────────────────────────────

    def _encode_image(self, image_path: str) -> str:
        with open(image_path, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")

    def _extract_section(self, text: str, keyword: str) -> str:
        lines = text.split("\n")
        capturing, result = False, []
        for line in lines:
            if keyword.lower() in line.lower():
                capturing = True
                continue
            if capturing:
                if any(str(i) + "." in line for i in range(1, 11)) and result:
                    break
                result.append(line)
        return "\n".join(result).strip() or text[:300]

    def _extract_risk_level(self, text: str) -> str:
        tl = text.lower()
        if "severe" in tl or "critical" in tl:
            return "High"
        if "moderate" in tl:
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
        return 0.78
