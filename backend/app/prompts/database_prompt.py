"""
Prompt templates for the Database Design Agent.

Generates detailed database schema including tables, columns,
relationships, and SQL DDL suggestions.
"""


def build_database_prompt(project_idea: str, requirements_summary: str) -> str:
    """
    Build the prompt for generating database design.

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
    return f"""You are a senior database architect. Design a complete, normalized database schema for the following project.

PROJECT IDEA: {project_idea}

REQUIREMENTS:
{requirements_summary}

IMPORTANT RULE: If this is a student or beginner project, recommend simple, beginner-friendly databases (SQLite, MySQL, PostgreSQL with simple schemas) rather than enterprise-scale distributed databases. Keep the design practical and learnable.

Produce a structured JSON object with EXACTLY these keys:

{{
  "recommended_database": "<e.g. PostgreSQL | MySQL | SQLite | MongoDB>",
  "database_type": "<relational | document | key-value>",
  "design_rationale": "<why this database is ideal for this project>",
  "tables": [
    {{
      "name": "<TableName>",
      "description": "<what this table stores>",
      "columns": [
        {{
          "name": "<column_name>",
          "type": "<data type e.g. VARCHAR(255), INTEGER, BOOLEAN, TIMESTAMP>",
          "constraints": "<e.g. PRIMARY KEY, NOT NULL, UNIQUE, FOREIGN KEY>",
          "description": "<what this column stores>"
        }}
      ]
    }}
  ],
  "relationships": [
    "<Table A -> Table B (relationship type e.g. one-to-many, many-to-many)>"
  ],
  "sql_schema": "<complete SQL CREATE TABLE statements for all tables, properly formatted>",
  "indexes": [
    "<recommended index description e.g. INDEX on users.email for fast login lookup>"
  ],
  "sample_queries": [
    {{
      "description": "<what this query does>",
      "sql": "<SQL query>"
    }}
  ]
}}

Rules:
- Output ONLY valid JSON. No markdown fences, no explanations.
- tables must have at least 4 tables covering the core entities.
- Each table must have at least 4 columns including id, created_at.
- sql_schema must be complete, valid SQL DDL with proper data types and constraints.
- relationships must describe all foreign key links between tables.
- Keep it practical and appropriate for the project's scale.
"""


DATABASE_SYSTEM_MESSAGE = (
    "You are a senior database architect specializing in relational and NoSQL database design. "
    "You write clean, normalized, production-ready schemas with proper constraints and indexes. "
    "For student projects, you recommend practical, beginner-friendly solutions. "
    "You always respond with valid JSON only."
)
