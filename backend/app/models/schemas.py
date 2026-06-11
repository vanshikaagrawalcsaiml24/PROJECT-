"""
Pydantic schemas for request and response models.
All API contracts are defined here for strict type validation.
"""

from typing import Any

from pydantic import BaseModel, Field


# ── Request Models ────────────────────────────────────────────────────────────


class ProjectIdeaRequest(BaseModel):
    """Incoming request to generate a project blueprint."""

    project_idea: str = Field(
        ...,
        min_length=10,
        max_length=2000,
        description="The project idea to convert into a blueprint.",
        examples=["Build an AI Interview Preparation Platform"],
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "project_idea": "Build an AI Interview Preparation Platform"
            }
        }
    }


# ── Sub-Response Models ───────────────────────────────────────────────────────


class TechStackCategory(BaseModel):
    """Structured tech stack recommendation per category."""

    frontend: list[str] = Field(default_factory=list)
    backend: list[str] = Field(default_factory=list)
    database: list[str] = Field(default_factory=list)
    deployment: list[str] = Field(default_factory=list)
    ai_ml: list[str] = Field(default_factory=list, alias="ai_ml")
    devtools: list[str] = Field(default_factory=list)

    model_config = {"populate_by_name": True}


class ArchitectureComponent(BaseModel):
    """A single component in the system architecture."""

    name: str
    role: str
    interactions: list[str] = Field(default_factory=list)


class DatabaseSuggestion(BaseModel):
    """Database design suggestion (from ArchitectureAgent — legacy)."""

    database_type: str
    recommended_db: str
    tables_or_collections: list[str] = Field(default_factory=list)
    rationale: str = ""


class APISuggestion(BaseModel):
    """A suggested API endpoint (from ArchitectureAgent — legacy)."""

    method: str
    endpoint: str
    description: str
    request_body: Any | None = None
    response_body: Any | None = None


class RoadmapPhase(BaseModel):
    """A phase in the development roadmap (from TechStackAgent — legacy)."""

    phase: str
    duration: str
    tasks: list[str] = Field(default_factory=list)


# ── NEW: Database Design Agent Models ─────────────────────────────────────────


class DatabaseColumn(BaseModel):
    """A single column definition in a database table."""

    name: str = Field(..., description="Column name")
    type: str = Field(..., description="Data type e.g. VARCHAR(255), INTEGER")
    constraints: str = Field(default="", description="SQL constraints e.g. PRIMARY KEY, NOT NULL")
    description: str = Field(default="", description="What this column stores")


class DatabaseTable(BaseModel):
    """A database table with its columns."""

    name: str = Field(..., description="Table name")
    description: str = Field(default="", description="What this table stores")
    columns: list[DatabaseColumn] = Field(default_factory=list)


class SampleQuery(BaseModel):
    """A sample SQL query."""

    description: str
    sql: str


class DatabaseDesign(BaseModel):
    """Full database design from the DatabaseAgent."""

    recommended_database: str = Field(default="", description="e.g. PostgreSQL, MySQL, SQLite")
    database_type: str = Field(default="", description="relational | document | key-value")
    design_rationale: str = Field(default="")
    tables: list[DatabaseTable] = Field(default_factory=list)
    relationships: list[str] = Field(default_factory=list)
    sql_schema: str = Field(default="", description="Complete SQL DDL")
    indexes: list[str] = Field(default_factory=list)
    sample_queries: list[SampleQuery] = Field(default_factory=list)


# ── NEW: API Design Agent Models ──────────────────────────────────────────────


class APIEndpoint(BaseModel):
    """A REST API endpoint specification."""

    method: str = Field(..., description="HTTP method: GET, POST, PUT, DELETE, PATCH")
    endpoint: str = Field(..., description="URL path e.g. /api/v1/users")
    description: str = Field(..., description="What this endpoint does")
    auth_required: bool = Field(default=True)
    request_body: Any = Field(default=None)
    response_body: Any = Field(default=None)
    status_codes: dict[str, str] = Field(default_factory=dict)


class APIGroup(BaseModel):
    """A logical group of related API endpoints."""

    group: str = Field(..., description="Group name e.g. Authentication")
    endpoints: list[str] = Field(default_factory=list)


class APIDesign(BaseModel):
    """Full API design from the APIAgent."""

    base_url: str = Field(default="/api/v1")
    authentication: str = Field(default="JWT Bearer Token")
    apis: list[APIEndpoint] = Field(default_factory=list)
    api_groups: list[APIGroup] = Field(default_factory=list)
    error_response_format: Any = Field(default=None)


# ── NEW: Roadmap Agent Models ─────────────────────────────────────────────────


class WeeklyTask(BaseModel):
    """A single week in the development roadmap."""

    week: int = Field(..., description="Week number")
    theme: str = Field(default="", description="Week's main focus area")
    tasks: list[str] = Field(default_factory=list)
    deliverables: list[str] = Field(default_factory=list)
    milestone: str | None = Field(default=None)


class RoadmapPhaseDetail(BaseModel):
    """A high-level phase grouping multiple weeks."""

    phase_name: str
    weeks: str = Field(..., description="e.g. 1-2")
    goal: str = Field(default="")


class WeeklyRoadmap(BaseModel):
    """Full week-by-week roadmap from the RoadmapAgent."""

    total_duration: str = Field(default="")
    team_size: str = Field(default="")
    methodology: str = Field(default="Agile")
    roadmap: list[WeeklyTask] = Field(default_factory=list)
    phases: list[RoadmapPhaseDetail] = Field(default_factory=list)
    risk_factors: list[str] = Field(default_factory=list)
    success_criteria: list[str] = Field(default_factory=list)


# ── NEW: Diagram Agent Models ─────────────────────────────────────────────────


class MermaidDiagram(BaseModel):
    """A single Mermaid.js diagram."""

    type: str = Field(default="flowchart", description="Diagram type")
    title: str = Field(default="")
    mermaid: str = Field(..., description="Valid Mermaid diagram source code")


class DiagramSet(BaseModel):
    """Collection of Mermaid diagrams from the DiagramAgent."""

    architecture_diagram: MermaidDiagram | None = None
    data_flow_diagram: MermaidDiagram | None = None
    er_diagram: MermaidDiagram | None = None
    sequence_diagram: MermaidDiagram | None = None
    mermaid: str = Field(default="", description="Main architecture diagram source (shorthand)")


# ── NEW: Execution Metadata Model ─────────────────────────────────────────────


class ExecutionMetadata(BaseModel):
    """Metadata about the pipeline execution."""

    execution_time_seconds: float = Field(..., description="Total wall-clock time in seconds")
    agents_executed: list[str] = Field(
        default_factory=list,
        description="Names of agents that ran successfully",
    )
    provider: str = Field(default="", description="LLM provider used")
    model: str = Field(default="", description="LLM model used")
    timestamp: str = Field(default="", description="ISO 8601 completion timestamp")


# ── EXPANDED Master Response Model ────────────────────────────────────────────


class ProjectBlueprintResponse(BaseModel):
    """
    Complete project blueprint returned by POST /generate-blueprint.

    Expanded from v1 — includes database design, API design, weekly
    roadmap, Mermaid diagrams, and execution metadata.
    All new fields are optional with sensible defaults so the existing
    /generate-blueprint endpoint remains backward-compatible.
    """

    # ── Original fields (unchanged) ───────────────────────────────────────────
    project_idea: str = Field(..., description="Original project idea submitted by user")
    problem_statement: str = Field(..., description="Clear problem statement")
    objectives: list[str] = Field(
        ..., description="Measurable project objectives", min_length=1
    )
    target_users: list[str] = Field(default_factory=list, description="Target user personas")
    features: list[str] = Field(
        ..., description="Key features of the project", min_length=1
    )
    tech_stack: TechStackCategory = Field(..., description="Recommended technologies")
    architecture: str = Field(..., description="High-level system architecture description")
    architecture_components: list[ArchitectureComponent] = Field(
        default_factory=list, description="Breakdown of architecture components"
    )
    database_suggestions: list[DatabaseSuggestion] = Field(
        default_factory=list, description="Database design recommendations (legacy)"
    )
    api_suggestions: list[APISuggestion] = Field(
        default_factory=list, description="Suggested API endpoints (legacy)"
    )
    development_roadmap: list[RoadmapPhase] = Field(
        default_factory=list, description="Phased development roadmap (legacy)"
    )
    future_scope: list[str] = Field(
        ..., description="Potential future enhancements", min_length=1
    )
    project_overview: str = Field(default="", description="Executive summary of the project")

    # ── NEW: Extended fields ──────────────────────────────────────────────────
    database: DatabaseDesign | None = Field(
        default=None, description="Detailed database schema from DatabaseAgent"
    )
    apis: APIDesign | None = Field(
        default=None, description="Full REST API specification from APIAgent"
    )
    roadmap: WeeklyRoadmap | None = Field(
        default=None, description="Week-by-week development roadmap from RoadmapAgent"
    )
    mermaid_diagram: str = Field(
        default="", description="Main Mermaid.js architecture diagram source"
    )
    diagrams: DiagramSet | None = Field(
        default=None, description="Full set of Mermaid diagrams from DiagramAgent"
    )
    metadata: ExecutionMetadata | None = Field(
        default=None, description="Pipeline execution metadata"
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "project_idea": "AI Interview Preparation Platform",
                "problem_statement": "Job seekers lack personalized...",
                "objectives": ["Reduce interview anxiety", "Improve success rate"],
                "target_users": ["Fresh graduates", "Software engineers"],
                "features": ["Mock interviews", "AI feedback"],
                "tech_stack": {
                    "frontend": ["React", "TypeScript"],
                    "backend": ["FastAPI", "Python"],
                    "database": ["PostgreSQL"],
                    "deployment": ["Docker", "AWS"],
                    "ai_ml": ["Gemini API"],
                    "devtools": ["GitHub Actions"],
                },
                "architecture": "Microservices with API gateway...",
                "future_scope": ["Mobile app", "Resume builder"],
                "mermaid_diagram": "graph TD\n    User --> Frontend",
                "metadata": {
                    "execution_time_seconds": 45.3,
                    "agents_executed": ["requirements", "documentation", "architecture",
                                        "techstack", "database", "api", "roadmap", "diagram"],
                    "provider": "gemini",
                    "model": "gemini-2.5-flash",
                    "timestamp": "2026-06-05T14:00:00Z",
                },
            }
        }
    }


# ── Health & Meta ─────────────────────────────────────────────────────────────


class HealthResponse(BaseModel):
    """Health check response."""

    status: str = "ok"
    version: str
    provider: str


class ErrorResponse(BaseModel):
    """Standard error envelope."""

    error: str
    detail: str | None = None
    code: int


# ── PDF & Export Request Models ───────────────────────────────────────────────


class ReportRequest(BaseModel):
    """Request to generate a PDF report."""

    project_idea: str = Field(
        ...,
        min_length=10,
        max_length=2000,
        description="The project idea to generate a PDF report for.",
    )

    model_config = {
        "json_schema_extra": {
            "example": {"project_idea": "Build an AI Interview Preparation Platform"}
        }
    }
