"""
Prompt templates for the Roadmap Agent.

Generates a week-by-week development timeline with concrete tasks,
milestones, and deliverables.
"""


def build_roadmap_prompt(project_idea: str, requirements_summary: str, techstack_summary: str) -> str:
    """
    Build the prompt for generating a detailed development roadmap.

    Parameters
    ----------
    project_idea:
        The original user-provided project idea.
    requirements_summary:
        JSON string output from the Requirements Agent.
    techstack_summary:
        JSON string output from the TechStack Agent.

    Returns
    -------
    str
        Formatted prompt ready to send to an LLM.
    """
    return f"""You are a senior project manager and software development lead. Create a detailed, realistic week-by-week development roadmap for the following project.

PROJECT IDEA: {project_idea}

REQUIREMENTS:
{requirements_summary}

TECH STACK:
{techstack_summary}

IMPORTANT RULE: If this is a student or academic project, create a practical timeline suitable for a student team (2–4 people) working part-time. Focus on learning milestones, not just deliverables. Keep scope realistic.

Produce a structured JSON object with EXACTLY these keys:

{{
  "total_duration": "<e.g. 8 weeks | 3 months>",
  "team_size": "<recommended team size e.g. 2-3 developers>",
  "methodology": "<e.g. Agile Scrum | Kanban | Waterfall>",
  "roadmap": [
    {{
      "week": 1,
      "theme": "<week focus e.g. Project Setup & Planning>",
      "tasks": [
        "<specific, actionable task 1>",
        "<specific, actionable task 2>",
        "<specific, actionable task 3>"
      ],
      "deliverables": ["<deliverable 1>", ...],
      "milestone": "<key milestone if any, else null>"
    }}
  ],
  "phases": [
    {{
      "phase_name": "<e.g. Phase 1: Foundation>",
      "weeks": "1-2",
      "goal": "<what is achieved by end of this phase>"
    }}
  ],
  "risk_factors": [
    "<potential risk 1>",
    "<potential risk 2>"
  ],
  "success_criteria": [
    "<measurable success criterion 1>",
    "<measurable success criterion 2>"
  ]
}}

Rules:
- Output ONLY valid JSON. No markdown fences, no explanations.
- roadmap must have at least 6 weeks of detailed planning.
- Each week must have at least 3 concrete, actionable tasks.
- tasks should be specific enough for a developer to immediately act on.
- phases should group related weeks into logical development phases.
"""


ROADMAP_SYSTEM_MESSAGE = (
    "You are a senior project manager specializing in software development planning. "
    "You create realistic, actionable roadmaps that teams can actually follow. "
    "For student projects, you tailor timelines to academic constraints and learning goals. "
    "You always respond with valid JSON only."
)
