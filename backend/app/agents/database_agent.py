"""
Database Design Agent.

Responsible for:
- Analysing project requirements
- Generating normalised database tables with columns and types
- Defining table relationships
- Producing SQL DDL schema
- Recommending indexes and sample queries
"""

import json
import logging

from app.prompts.database_prompt import (
    DATABASE_SYSTEM_MESSAGE,
    build_database_prompt,
)
from app.services.llm_provider import LLMProvider, LLMProviderError

logger = logging.getLogger(__name__)


class DatabaseAgent:
    """
    Designs the database schema for a project.

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

    async def run(self, project_idea: str, requirements: dict) -> dict:
        """
        Generate a full database design for the project.

        Parameters
        ----------
        project_idea:
            The original user-provided project idea.
        requirements:
            Structured dict returned by the RequirementsAgent.

        Returns
        -------
        dict
            Parsed JSON dict with keys: recommended_database, tables,
            relationships, sql_schema, indexes, sample_queries.

        Raises
        ------
        ValueError
            If the LLM response cannot be parsed as valid JSON.
        LLMProviderError
            If the LLM call fails.
        """
        logger.info("[Database Agent] Started")

        requirements_summary = json.dumps(requirements, indent=2)
        prompt = build_database_prompt(project_idea, requirements_summary)

        try:
            raw = await self._llm.generate(
                prompt,
                system_message=DATABASE_SYSTEM_MESSAGE,
                temperature=0.4,
                max_tokens=5000,
            )
        except LLMProviderError:
            logger.exception("[Database Agent] LLM call failed")
            raise

        result = self._parse_json(raw, context="DatabaseAgent")
        logger.info(
            "[Database Agent] Completed | tables=%d | relationships=%d",
            len(result.get("tables", [])),
            len(result.get("relationships", [])),
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
