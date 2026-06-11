"""
Prompt templates for the Tech Stack Agent.

Recommends specific technologies per layer and generates the
development roadmap and future scope.
"""


def build_techstack_prompt(project_idea: str, requirements_summary: str, architecture_summary: str) -> str:
    """
    Build the prompt for tech stack recommendations and roadmap generation.

    Parameters
    ----------
    project_idea:
        The original user-provided project idea.
    requirements_summary:
        JSON string output from the Requirements Agent.
    architecture_summary:
        JSON string output from the Architecture Agent.

    Returns
    -------
    str
        Formatted prompt ready to send to an LLM.
    """
    return f"""You are a senior full-stack engineer and technology strategist. Recommend the optimal technology stack and development roadmap for this project.

PROJECT IDEA: {project_idea}

REQUIREMENTS:
{requirements_summary}

ARCHITECTURE:
{architecture_summary}

Produce a structured JSON object with EXACTLY these keys:

{{
  "tech_stack": {{
    "frontend": ["<technology 1>", "<technology 2>", ...],
    "backend": ["<technology 1>", "<technology 2>", ...],
    "database": ["<technology 1>", ...],
    "deployment": ["<technology 1>", ...],
    "ai_ml": ["<technology 1>", ...],
    "devtools": ["<CI/CD tool>", "<testing tool>", "<monitoring tool>", ...]
  }},
  "tech_stack_rationale": {{
    "frontend": "<why these frontend technologies>",
    "backend": "<why these backend technologies>",
    "database": "<why these databases>",
    "ai_ml": "<why these AI/ML tools>"
  }},
  "development_roadmap": [
    {{
      "phase": "Phase 1: <Phase Name>",
      "duration": "<e.g. 2 weeks>",
      "tasks": [
        "<concrete task 1>",
        "<concrete task 2>",
        ...
      ]
    }},
    ...
  ],
  "future_scope": [
    "<future feature or enhancement 1>",
    "<future feature or enhancement 2>",
    ...
  ],
  "estimated_timeline": "<total estimated project duration>"
}}

Rules:
- Output ONLY valid JSON. No markdown, no code fences, no extra text.
- tech_stack.frontend must list at least 3 technologies with versions where relevant.
- tech_stack.backend must list at least 3 technologies.
- development_roadmap must have at least 4 phases, covering setup → MVP → launch → iteration.
- Each roadmap phase must have at least 4 concrete tasks.
- future_scope must have at least 6 meaningful future enhancements.
- Recommend modern, production-proven, and widely-adopted technologies.
- IMPORTANT RULE: If this is a student or beginner project, recommend practical, beginner-friendly technologies (e.g., SQLite, PostgreSQL, MySQL, Flask, FastAPI, Express, React, simple hosting like Vercel or Render) instead of enterprise-scale cloud architectures (e.g., Kubernetes, multi-region AWS services, complex serverless orchestration, microservices).
"""


TECHSTACK_SYSTEM_MESSAGE = (
    "You are a senior full-stack engineer and CTO with expertise in selecting technology stacks. "
    "If the project is a student project, you recommend practical, beginner-friendly technologies "
    "instead of enterprise-scale cloud architectures. "
    "You always respond with valid JSON only."
)
