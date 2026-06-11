"""
Prompt templates for the Requirements Agent.

All prompts are pure functions that receive runtime data and return
fully-formed strings — no logic or LLM calls happen here.
"""


def build_requirements_prompt(project_idea: str) -> str:
    """
    Build the prompt that extracts functional requirements from a project idea.

    Parameters
    ----------
    project_idea:
        The raw project idea provided by the user.

    Returns
    -------
    str
        Formatted prompt ready to send to an LLM.
    """
    return f"""You are an expert software project analyst. Analyze the following project idea and extract its core requirements.

PROJECT IDEA: {project_idea}

Your task is to produce a structured JSON object with EXACTLY these keys:

{{
  "target_users": ["<persona 1>", "<persona 2>", ...],
  "problem_being_solved": "<one clear sentence>",
  "core_modules": ["<module 1>", "<module 2>", ...],
  "key_features": [
    "<feature 1 — specific and actionable>",
    "<feature 2>",
    ...
  ],
  "non_functional_requirements": [
    "<e.g. system must handle 1000 concurrent users>",
    ...
  ],
  "assumptions": ["<assumption 1>", ...]
}}

Rules:
- Output ONLY valid JSON. No markdown fences, no explanations, no extra keys.
- key_features must have at least 8 items, each a concrete feature description.
- target_users must have at least 3 distinct user personas.
- core_modules must list the main functional areas (e.g. "User Authentication", "Dashboard", "API Gateway").
- Every string must be professional, specific, and implementation-ready.
"""


REQUIREMENTS_SYSTEM_MESSAGE = (
    "You are a senior business analyst and software architect. "
    "You extract precise, implementation-ready requirements from project ideas. "
    "You always respond with valid JSON only."
)
