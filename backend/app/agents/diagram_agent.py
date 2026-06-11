"""
Diagram Agent.

Responsible for:
- Generating valid Mermaid.js architecture diagrams
- Generating data flow diagrams
- Generating entity relationship (ER) diagrams
- Generating sequence diagrams for key flows
"""

import json
import logging

from app.prompts.diagram_prompt import (
    DIAGRAM_SYSTEM_MESSAGE,
    build_diagram_prompt,
)
from app.services.llm_provider import LLMProvider, LLMProviderError

logger = logging.getLogger(__name__)


class DiagramAgent:
    """
    Generates Mermaid.js diagrams for a project.

    Produces architecture, data flow, ER, and sequence diagrams
    that can be rendered directly in any Mermaid-compatible viewer.
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

    async def run(self, project_idea: str, architecture: dict, database: dict) -> dict:
        """
        Generate Mermaid diagrams for the project.

        Parameters
        ----------
        project_idea:
            The original user-provided project idea.
        architecture:
            Structured dict returned by the ArchitectureAgent.
        database:
            Structured dict returned by the DatabaseAgent.

        Returns
        -------
        dict
            Parsed JSON dict with keys: architecture_diagram,
            data_flow_diagram, er_diagram, sequence_diagram, mermaid.

        Raises
        ------
        ValueError
            If the LLM response cannot be parsed as valid JSON.
        LLMProviderError
            If the LLM call fails.
        """
        logger.info("[Diagram Agent] Started")

        architecture_summary = json.dumps(architecture, indent=2)
        database_summary = json.dumps(database, indent=2)
        prompt = build_diagram_prompt(project_idea, architecture_summary, database_summary)

        try:
            raw = await self._llm.generate(
                prompt,
                system_message=DIAGRAM_SYSTEM_MESSAGE,
                temperature=0.3,  # low temp for deterministic, valid syntax
                max_tokens=4000,
            )
        except LLMProviderError:
            logger.exception("[Diagram Agent] LLM call failed")
            raise

        result = self._parse_json(raw, context="DiagramAgent")

        # Ensure top-level 'mermaid' key is always present for backward compat
        if "mermaid" not in result and "architecture_diagram" in result:
            result["mermaid"] = result["architecture_diagram"].get("mermaid", "")

        logger.info(
            "[Diagram Agent] Completed | diagram_types=%d",
            sum(1 for k in ["architecture_diagram", "data_flow_diagram", "er_diagram", "sequence_diagram"] if k in result),
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
