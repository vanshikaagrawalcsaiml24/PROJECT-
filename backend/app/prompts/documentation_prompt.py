"""
Prompt templates for the Documentation Agent.

Produces the problem statement, objectives, and project overview
based on extracted requirements.
"""


def build_documentation_prompt(project_idea: str, requirements_summary: str) -> str:
    """
    Build the prompt for generating project documentation.

    Parameters
    ----------
    project_idea:
        The original user-provided project idea.
    requirements_summary:
        JSON string output from the Requirements Agent.

    Returns
    -------
    str
        Formatted prompt ready to send to an LLM.
    """
    return f"""You are a senior technical writer and product manager. Based on the project idea and extracted requirements below, write formal project documentation.

PROJECT IDEA: {project_idea}

EXTRACTED REQUIREMENTS:
{requirements_summary}

Produce a structured JSON object with EXACTLY these keys:

{{
  "problem_statement": "<2–4 sentence formal problem statement explaining the pain point, who faces it, and why existing solutions fall short>",
  "project_overview": "<3–5 sentence executive summary of what this project is, what it does, and its value proposition>",
  "objectives": [
    "<SMART objective 1 — Specific, Measurable, Achievable, Relevant, Time-bound>",
    "<SMART objective 2>",
    "<SMART objective 3>",
    ...
  ],
  "success_metrics": [
    "<measurable KPI 1>",
    "<measurable KPI 2>",
    ...
  ],
  "scope": {{
    "in_scope": ["<item 1>", ...],
    "out_of_scope": ["<item 1>", ...]
  }}
}}

Rules:
- Output ONLY valid JSON. No markdown, no extra text, no code fences.
- objectives must have at least 5 items, each starting with an action verb.
- problem_statement must be formal, concise, and compelling.
- success_metrics must be quantifiable wherever possible.
"""


DOCUMENTATION_SYSTEM_MESSAGE = (
    "You are a senior technical writer specializing in software project documentation. "
    "You write clear, professional, and structured documents. "
    "You always respond with valid JSON only."
)
