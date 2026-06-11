"""
Tech Stack Agent.

Responsible for:
- Recommending frontend, backend, database, and deployment technologies
- Providing rationale for each technology choice
- Generating a phased development roadmap
- Defining future scope enhancements
"""

import json
import logging

from app.prompts.techstack_prompt import (
    TECHSTACK_SYSTEM_MESSAGE,
    build_techstack_prompt,
)
from app.services.llm_provider import LLMProvider, LLMProviderError

logger = logging.getLogger(__name__)


class TechStackAgent:
    """
    Recommends technology stack and generates the development roadmap.

    Uses requirements and architecture output from upstream agents to
    produce informed, project-specific technology recommendations.
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

    async def run(
        self,
        project_idea: str,
        requirements: dict,
        architecture: dict,
    ) -> dict:
        """
        Generate tech stack recommendations and development roadmap.

        Parameters
        ----------
        project_idea:
            The original user-provided project idea.
        requirements:
            Structured dict returned by the RequirementsAgent.
        architecture:
            Structured dict returned by the ArchitectureAgent.

        Returns
        -------
        dict
            Parsed JSON dict with keys: tech_stack, tech_stack_rationale,
            development_roadmap, future_scope, estimated_timeline.

        Raises
        ------
        ValueError
            If the LLM response cannot be parsed as valid JSON.
        LLMProviderError
            If the LLM call fails.
        """
        logger.info("TechStackAgent | recommending technologies and roadmap...")

        requirements_summary = json.dumps(requirements, indent=2)
        architecture_summary = json.dumps(architecture, indent=2)

        prompt = build_techstack_prompt(
            project_idea, requirements_summary, architecture_summary
        )

        try:
            raw = await self._llm.generate(
                prompt,
                system_message=TECHSTACK_SYSTEM_MESSAGE,
                temperature=0.6,
                max_tokens=6000,
            )
        except LLMProviderError:
            logger.exception("TechStackAgent | LLM call failed")
            raise

        result = self._parse_json(raw, context="TechStackAgent")
        logger.info(
            "TechStackAgent | generated %d roadmap phases, %d future scope items",
            len(result.get("development_roadmap", [])),
            len(result.get("future_scope", [])),
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
