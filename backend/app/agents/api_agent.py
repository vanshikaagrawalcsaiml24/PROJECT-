"""
API Design Agent.

Responsible for:
- Generating RESTful API endpoint specifications
- Defining request and response schemas
- Grouping endpoints by resource
- Specifying authentication requirements and status codes
"""

import json
import logging

from app.prompts.api_prompt import (
    API_SYSTEM_MESSAGE,
    build_api_prompt,
)
from app.services.llm_provider import LLMProvider, LLMProviderError

logger = logging.getLogger(__name__)


class APIAgent:
    """
    Designs a complete REST API specification for a project.

    Produces endpoint definitions, request/response schemas, and
    authentication strategy. Uses an injected ``LLMProvider``.
    """

    def __init__(self, llm: LLMProvider) -> None:
        """
        Initialise the agent.

        Parameters
        ----------
        llm:
            An LLMProvider instance used for all completions.
        """
        self._llm = llm

    async def run(self, project_idea: str, requirements: dict) -> dict:
        """
        Generate a full REST API specification for the project.

        Parameters
        ----------
        project_idea:
            The original user-provided project idea.
        requirements:
            Structured dict returned by the RequirementsAgent.

        Returns
        -------
        dict
            Parsed JSON dict with keys: base_url, authentication,
            apis, api_groups, error_response_format.

        Raises
        ------
        ValueError
            If the LLM response cannot be parsed as valid JSON.
        LLMProviderError
            If the LLM call fails.
        """
        logger.info("[API Agent] Started")

        requirements_summary = json.dumps(requirements, indent=2)
        prompt = build_api_prompt(project_idea, requirements_summary)

        try:
            raw = await self._llm.generate(
                prompt,
                system_message=API_SYSTEM_MESSAGE,
                temperature=0.4,
                max_tokens=5000,
            )
        except LLMProviderError:
            logger.exception("[API Agent] LLM call failed")
            raise

        result = self._parse_json(raw, context="APIAgent")
        logger.info(
            "[API Agent] Completed | endpoints=%d",
            len(result.get("apis", [])),
        )
        return result

    @staticmethod
    def _parse_json(raw: str, context: str) -> dict:
        """Safely parse a JSON string, stripping markdown fences if present."""
        cleaned = raw.strip()
        if cleaned.startswith("```"):
            lines = cleaned.split("\n")
            cleaned = "\n".join(lines[1:-1]) if len(lines) > 2 else cleaned

        try:
            return json.loads(cleaned)
        except json.JSONDecodeError as exc:
            logger.error("%s | JSON parse error: %s | raw=%.300s", context, exc, raw)
            raise ValueError(
                f"{context} returned invalid JSON: {exc}. Raw response: {raw[:200]}"
            ) from exc
