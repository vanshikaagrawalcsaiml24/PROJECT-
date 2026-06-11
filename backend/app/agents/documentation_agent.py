"""
Documentation Agent.

Responsible for:
- Generating a formal problem statement
- Writing measurable objectives
- Producing a project overview / executive summary
- Defining scope boundaries
"""

import json
import logging

from app.prompts.documentation_prompt import (
    DOCUMENTATION_SYSTEM_MESSAGE,
    build_documentation_prompt,
)
from app.services.llm_provider import LLMProvider, LLMProviderError

logger = logging.getLogger(__name__)


class DocumentationAgent:
    """
    Generates formal project documentation from extracted requirements.

    Produces problem statement, objectives, project overview, and scope.
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
        Generate documentation artifacts for the project.

        Parameters
        ----------
        project_idea:
            The original user-provided project idea.
        requirements:
            Structured dict returned by the RequirementsAgent.

        Returns
        -------
        dict
            Parsed JSON dict with keys: problem_statement, project_overview,
            objectives, success_metrics, scope.

        Raises
        ------
        ValueError
            If the LLM response cannot be parsed as valid JSON.
        LLMProviderError
            If the LLM call fails.
        """
        logger.info("DocumentationAgent | generating documentation...")

        requirements_summary = json.dumps(requirements, indent=2)
        prompt = build_documentation_prompt(project_idea, requirements_summary)

        try:
            raw = await self._llm.generate(
                prompt,
                system_message=DOCUMENTATION_SYSTEM_MESSAGE,
                temperature=0.6,
            )
        except LLMProviderError:
            logger.exception("DocumentationAgent | LLM call failed")
            raise

        result = self._parse_json(raw, context="DocumentationAgent")
        logger.info(
            "DocumentationAgent | generated %d objectives",
            len(result.get("objectives", [])),
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
