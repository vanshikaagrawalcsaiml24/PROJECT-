"""
Architecture Agent.

Responsible for:
- Defining system architecture style and description
- Generating component breakdown with interaction graphs
- Recommending database design
- Suggesting API endpoints
- Outlining deployment and security considerations
"""

import json
import logging

from app.prompts.architecture_prompt import (
    ARCHITECTURE_SYSTEM_MESSAGE,
    build_architecture_prompt,
)
from app.services.llm_provider import LLMProvider, LLMProviderError

logger = logging.getLogger(__name__)


class ArchitectureAgent:
    """
    Designs the high-level system architecture for a project.

    Produces components, database recommendations, API suggestions,
    and deployment strategy.
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
        Generate the system architecture for the project.

        Parameters
        ----------
        project_idea:
            The original user-provided project idea.
        requirements:
            Structured dict returned by the RequirementsAgent.

        Returns
        -------
        dict
            Parsed JSON dict with keys: architecture_style, architecture_description,
            components, database_suggestions, api_suggestions,
            deployment_strategy, security_considerations.

        Raises
        ------
        ValueError
            If the LLM response cannot be parsed as valid JSON.
        LLMProviderError
            If the LLM call fails.
        """
        logger.info("ArchitectureAgent | designing system architecture...")

        requirements_summary = json.dumps(requirements, indent=2)
        prompt = build_architecture_prompt(project_idea, requirements_summary)

        try:
            raw = await self._llm.generate(
                prompt,
                system_message=ARCHITECTURE_SYSTEM_MESSAGE,
                temperature=0.5,
                max_tokens=6000,  # Architecture responses can be long
            )
        except LLMProviderError:
            logger.exception("ArchitectureAgent | LLM call failed")
            raise

        result = self._parse_json(raw, context="ArchitectureAgent")
        logger.info(
            "ArchitectureAgent | designed %d components, %d API endpoints",
            len(result.get("components", [])),
            len(result.get("api_suggestions", [])),
        )
        return result

    # ── helpers ───────────────────────────────────────────────────────────────

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
