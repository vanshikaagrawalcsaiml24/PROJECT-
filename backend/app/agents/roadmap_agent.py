"""
Roadmap Agent.

Responsible for:
- Generating a detailed week-by-week development timeline
- Defining phases, milestones, and deliverables
- Identifying risk factors
- Providing success criteria
"""

import json
import logging

from app.prompts.roadmap_prompt import (
    ROADMAP_SYSTEM_MESSAGE,
    build_roadmap_prompt,
)
from app.services.llm_provider import LLMProvider, LLMProviderError

logger = logging.getLogger(__name__)


class RoadmapAgent:
    """
    Generates a detailed, week-by-week development roadmap.

    Uses requirements and tech stack context from upstream agents
    to produce a realistic, actionable timeline.
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

    async def run(self, project_idea: str, requirements: dict, techstack: dict) -> dict:
        """
        Generate a week-by-week development roadmap.

        Parameters
        ----------
        project_idea:
            The original user-provided project idea.
        requirements:
            Structured dict returned by the RequirementsAgent.
        techstack:
            Structured dict returned by the TechStackAgent.

        Returns
        -------
        dict
            Parsed JSON dict with keys: total_duration, team_size,
            methodology, roadmap, phases, risk_factors, success_criteria.

        Raises
        ------
        ValueError
            If the LLM response cannot be parsed as valid JSON.
        LLMProviderError
            If the LLM call fails.
        """
        logger.info("[Roadmap Agent] Started")

        requirements_summary = json.dumps(requirements, indent=2)
        techstack_summary = json.dumps(techstack, indent=2)
        prompt = build_roadmap_prompt(project_idea, requirements_summary, techstack_summary)

        try:
            raw = await self._llm.generate(
                prompt,
                system_message=ROADMAP_SYSTEM_MESSAGE,
                temperature=0.5,
                max_tokens=5000,
            )
        except LLMProviderError:
            logger.exception("[Roadmap Agent] LLM call failed")
            raise

        result = self._parse_json(raw, context="RoadmapAgent")
        logger.info(
            "[Roadmap Agent] Completed | weeks=%d | phases=%d",
            len(result.get("roadmap", [])),
            len(result.get("phases", [])),
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
