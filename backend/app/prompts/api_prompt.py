"""
Prompt templates for the API Design Agent.

Generates detailed REST API endpoint specifications including
methods, paths, request/response bodies, and status codes.
"""


def build_api_prompt(project_idea: str, requirements_summary: str) -> str:
    """
    Build the prompt for generating REST API design.

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
    return f"""You are a senior API architect. Design a complete, RESTful API specification for the following project.

PROJECT IDEA: {project_idea}

REQUIREMENTS:
{requirements_summary}

IMPORTANT RULE: If this is a student or beginner project, keep the API design simple, well-documented, and easy to implement. Avoid overly complex patterns like HATEOAS or GraphQL unless clearly needed.

Produce a structured JSON object with EXACTLY these keys:

{{
  "base_url": "/api/v1",
  "authentication": "<e.g. JWT Bearer Token | Session Cookie | API Key>",
  "apis": [
    {{
      "method": "<GET|POST|PUT|DELETE|PATCH>",
      "endpoint": "<e.g. /users/login>",
      "description": "<clear description of what this endpoint does>",
      "auth_required": true,
      "request_body": {{
        "<field_name>": "<type and description>"
      }},
      "response_body": {{
        "<field_name>": "<type and description>"
      }},
      "status_codes": {{
        "200": "<success description>",
        "400": "<bad request description>",
        "401": "<unauthorized description>"
      }}
    }}
  ],
  "api_groups": [
    {{
      "group": "<e.g. Authentication>",
      "endpoints": ["<method> <endpoint>", ...]
    }}
  ],
  "error_response_format": {{
    "error": "string",
    "message": "string",
    "status_code": "integer"
  }}
}}

Rules:
- Output ONLY valid JSON. No markdown fences, no explanations.
- apis must have at least 10 endpoints covering authentication, CRUD operations, and core business logic.
- Every endpoint must have a clear description, request_body, and response_body.
- Group related endpoints logically in api_groups.
- Use RESTful naming conventions (plural nouns, lowercase, hyphens).
"""


API_SYSTEM_MESSAGE = (
    "You are a senior API architect and backend engineer specializing in RESTful API design. "
    "You design clean, intuitive, and well-documented APIs following REST best practices. "
    "For student projects, you keep designs simple and learnable. "
    "You always respond with valid JSON only."
)
