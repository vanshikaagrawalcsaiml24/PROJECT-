"""
Prompt templates for the Diagram Agent.

Generates valid Mermaid.js diagrams including system architecture,
data flow, and entity relationship diagrams.
"""


def build_diagram_prompt(project_idea: str, architecture_summary: str, database_summary: str) -> str:
    """
    Build the prompt for generating Mermaid diagrams.

    Parameters
    ----------
    project_idea:
        The original user-provided project idea.
    architecture_summary:
        JSON string output from the Architecture Agent.
    database_summary:
        JSON string output from the Database Agent.

    Returns
    -------
    str
        Formatted prompt ready to send to an LLM.
    """
    return f"""You are a software architect and technical documentation expert. Generate valid Mermaid.js diagrams for the following project.

PROJECT IDEA: {project_idea}

ARCHITECTURE:
{architecture_summary}

DATABASE:
{database_summary}

Produce a structured JSON object with EXACTLY these keys:

{{
  "architecture_diagram": {{
    "type": "flowchart",
    "title": "System Architecture",
    "mermaid": "<valid Mermaid flowchart TD diagram showing system components and their connections>"
  }},
  "data_flow_diagram": {{
    "type": "flowchart",
    "title": "Data Flow",
    "mermaid": "<valid Mermaid flowchart LR diagram showing how data flows through the system>"
  }},
  "er_diagram": {{
    "type": "erDiagram",
    "title": "Entity Relationship Diagram",
    "mermaid": "<valid Mermaid erDiagram showing database tables and their relationships>"
  }},
  "sequence_diagram": {{
    "type": "sequenceDiagram",
    "title": "User Authentication Flow",
    "mermaid": "<valid Mermaid sequenceDiagram showing the login/auth sequence>"
  }},
  "mermaid": "<the main architecture flowchart mermaid code — same as architecture_diagram.mermaid>"
}}

CRITICAL Mermaid syntax rules you MUST follow:
1. Use only alphanumeric characters and underscores in node IDs (no spaces, no special chars in IDs).
2. Node labels can have spaces if wrapped in square brackets: User[User Browser]
3. Arrow syntax: A --> B or A -- label --> B
4. For flowchart: start with 'graph TD' or 'flowchart TD'
5. For erDiagram: use ||--o{{ and }}o--|| for relationships
6. For sequenceDiagram: use participant keyword and ->> for messages
7. NO semicolons inside diagram code
8. Each diagram must be self-contained (no cross-references)
9. Keep diagrams simple enough to render without errors

Example valid flowchart:
graph TD
    User[User] --> Frontend[React Frontend]
    Frontend --> API[FastAPI Backend]
    API --> DB[(Database)]
    API --> Cache[Redis Cache]

Output ONLY valid JSON. No markdown fences around the JSON. Mermaid code goes inside the JSON string values.
"""


DIAGRAM_SYSTEM_MESSAGE = (
    "You are a technical documentation expert specializing in software architecture diagrams. "
    "You generate syntactically valid Mermaid.js diagrams that render without errors. "
    "You always respond with valid JSON only — never wrap your response in markdown code fences."
)
