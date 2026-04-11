"""
utils/vertex_ai.py

Helper class for Vertex AI (Gemini) used by @Analyst.

Supports:
  - Text generation via the ``generate_text`` method (uses the
    Vertex AI Generative AI SDK).

Required environment variables:
  - VERTEX_AI_PROJECT   – GCP project ID
  - VERTEX_AI_LOCATION  – e.g. "us-central1"
  - VERTEX_AI_MODEL     – e.g. "gemini-1.5-pro" (default)
"""

import logging
import os
from typing import Any

import vertexai
from vertexai.generative_models import GenerativeModel, GenerationConfig

logger = logging.getLogger(__name__)

_DEFAULT_MODEL = "gemini-1.5-pro"


class VertexAIHelper:
    """
    Thin wrapper around the Vertex AI Generative Models API.

    All methods are synchronous and intended to be run via
    ``asyncio.to_thread`` in the async agents.
    """

    def __init__(
        self,
        project: str | None = None,
        location: str | None = None,
        model_name: str | None = None,
    ) -> None:
        self.project = project or os.environ.get("VERTEX_AI_PROJECT")
        self.location = location or os.environ.get("VERTEX_AI_LOCATION", "us-central1")
        self.model_name = (
            model_name
            or os.environ.get("VERTEX_AI_MODEL")
            or _DEFAULT_MODEL
        )

        if not self.project:
            raise ValueError(
                "GCP project must be provided via the VERTEX_AI_PROJECT "
                "environment variable or the project constructor argument."
            )

        vertexai.init(project=self.project, location=self.location)
        self._model = GenerativeModel(self.model_name)
        logger.info(
            "[VertexAI] Initialized model %s in %s/%s",
            self.model_name,
            self.project,
            self.location,
        )

    # ------------------------------------------------------------------
    # Generation
    # ------------------------------------------------------------------

    def generate_text(
        self,
        prompt: str,
        max_output_tokens: int = 1024,
        temperature: float = 0.4,
    ) -> str:
        """
        Send *prompt* to the configured Gemini model and return the
        generated text as a string.
        """
        generation_config = GenerationConfig(
            max_output_tokens=max_output_tokens,
            temperature=temperature,
        )
        logger.info("[VertexAI] Generating text (prompt length=%d)", len(prompt))
        response = self._model.generate_content(
            prompt,
            generation_config=generation_config,
        )
        text: str = response.text
        logger.info("[VertexAI] Generation complete (response length=%d)", len(text))
        return text

    def summarize(self, text: str) -> str:
        """Convenience wrapper: summarize *text* in a few sentences."""
        return self.generate_text(
            prompt=f"Summarize the following text concisely in 3-5 sentences:\n\n{text}",
            max_output_tokens=512,
            temperature=0.2,
        )

    def analyze(self, data_description: str) -> dict[str, Any]:
        """
        Ask the model to analyze *data_description* and return a structured
        dict with ``insight`` and ``recommendations`` keys.
        """
        prompt = (
            "You are a business analyst. Given the following data description, "
            "provide:\n1. Key insight (2-3 sentences)\n2. Top 3 actionable "
            f"recommendations\n\nData:\n{data_description}\n\n"
            "Respond in this exact format:\n"
            "INSIGHT: <your insight>\n"
            "RECOMMENDATIONS:\n- <rec 1>\n- <rec 2>\n- <rec 3>"
        )
        raw = self.generate_text(prompt=prompt, max_output_tokens=512, temperature=0.3)
        result: dict[str, Any] = {"raw": raw, "insight": "", "recommendations": []}
        for line in raw.splitlines():
            if line.startswith("INSIGHT:"):
                result["insight"] = line.removeprefix("INSIGHT:").strip()
            elif line.startswith("- "):
                result["recommendations"].append(line.removeprefix("- ").strip())
        return result
