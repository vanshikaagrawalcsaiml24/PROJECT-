"""
Requirements Agent.

Responsible for:
- Extracting functional and non-functional requirements
- Identifying target user personas
- Discovering core modules
- Generating a detailed feature list
"""

import json
import logging

from app.prompts.requirements_prompt import (
    REQUIREMENTS_SYSTEM_MESSAGE,
    build_requirements_prompt,
)
from app.services.llm_provider import LLMProvider, LLMProviderError

logger = logging.getLogger(__name__)


class RequirementsAgent:
    """
    Extracts structured requirements from a raw project idea.

    Uses an injected ``LLMProvider`` — no hard dependency on any
    specific model or vendor.
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

    async def run(self, project_idea: str) -> dict:
        """
        Analyse a project idea and return structured requirements.

        Parameters
        ----------
        project_idea:
            The raw project idea string from the user.

        Returns
        -------
        dict
            Parsed JSON dict with keys: target_users, problem_being_solved,
            core_modules, key_features, non_functional_requirements, assumptions.

        Raises
        ------
        ValueError
            If the LLM response cannot be parsed as valid JSON.
        LLMProviderError
            If the LLM call fails.
        """
        logger.info("RequirementsAgent | processing idea: %.80s...", project_idea)

        prompt = build_requirements_prompt(project_idea)

        try:
            raw = await self._llm.generate(
                prompt,
                system_message=REQUIREMENTS_SYSTEM_MESSAGE,
                temperature=0.5,  # lower temp for structured extraction
            )
        except LLMProviderError:
            logger.exception("RequirementsAgent | LLM call failed")
            raise

        result = self._parse_json(raw, context="RequirementsAgent")
        logger.info(
            "RequirementsAgent | extracted %d features, %d modules",
            len(result.get("key_features", [])),
            len(result.get("core_modules", [])),
        )
        return result

    # ── helpers ───────────────────────────────────────────────────────────────

    @staticmethod
    def _parse_json(raw: str, context: str) -> dict:
        """
        Safely parse a JSON string, stripping markdown fences if present.

        Parameters
        ----------
        raw:
            Raw string from the LLM.
        context:
            Caller name for error messages.

        Returns
        -------
        dict
            Parsed JSON object.

        Raises
        ------
        ValueError
            If parsing fails after cleanup attempts.
        """
        cleaned = raw.strip()
        # Strip markdown code fences if the model wrapped the JSON
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
