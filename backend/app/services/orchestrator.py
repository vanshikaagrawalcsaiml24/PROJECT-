"""
Orchestrator service.

Wires together all eight specialized agents in sequence and merges
their outputs into a single ``ProjectBlueprintResponse``.

Orchestration flow:
    User Input
        ↓
    RequirementsAgent   — Extract features, modules, personas
        ↓
    DocumentationAgent  — Problem statement, objectives, overview
        ↓
    ArchitectureAgent   — System design, DB, API suggestions (legacy)
        ↓
    TechStackAgent      — Tech stack, roadmap (legacy), future scope
        ↓
    DatabaseAgent       — Detailed schema, SQL DDL, relationships
        ↓
    APIAgent            — Full REST API specification
        ↓
    RoadmapAgent        — Week-by-week development timeline
        ↓
    DiagramAgent        — Mermaid architecture / ER / flow diagrams
        ↓
    Merge & Validate
        ↓
    ProjectBlueprintResponse  (with ExecutionMetadata)
"""

import asyncio
import json
import logging
import time
from datetime import datetime, timezone

from app.agents.api_agent import APIAgent
from app.agents.architecture_agent import ArchitectureAgent
from app.agents.database_agent import DatabaseAgent
from app.agents.diagram_agent import DiagramAgent
from app.agents.documentation_agent import DocumentationAgent
from app.agents.requirements_agent import RequirementsAgent
from app.agents.roadmap_agent import RoadmapAgent
from app.agents.techstack_agent import TechStackAgent

from app.config import get_settings
from app.models.schemas import (
    APISuggestion,
    APIDesign,
    APIEndpoint,
    APIGroup,
    ArchitectureComponent,
    DatabaseColumn,
    DatabaseDesign,
    DatabaseSuggestion,
    DatabaseTable,
    DiagramSet,
    ExecutionMetadata,
    MermaidDiagram,
    ProjectBlueprintResponse,
    RoadmapPhase,
    RoadmapPhaseDetail,
    SampleQuery,
    TechStackCategory,
    WeeklyRoadmap,
    WeeklyTask,
)
from app.services.llm_provider import LLMProvider

logger = logging.getLogger(__name__)


def _get_llm_provider() -> LLMProvider:
    """
    Factory that returns the configured LLM provider.

    Reads ``LLM_PROVIDER`` from settings and instantiates the matching
    concrete class. Adding a new provider only requires updating this
    function — no agent code changes.
    """
    settings = get_settings()
    provider_name = settings.llm_provider.lower()

    if provider_name == "deepseek":
        from app.services.deepseek_service import DeepSeekProvider
        return DeepSeekProvider()

    if provider_name == "openrouter":
        from app.services.openrouter_service import OpenRouterProvider
        return OpenRouterProvider()

    if provider_name == "gemini":
        from app.services.gemini_service import GeminiProvider
        return GeminiProvider()

    if provider_name == "groq":
        from app.services.groq_service import GroqProvider
        return GroqProvider()

    raise ValueError(
        f"Unknown LLM provider: '{provider_name}'. "
        "Supported values: 'groq', 'deepseek', 'openrouter', 'gemini'."
    )


class Orchestrator:
    """
    Coordinates the full eight-agent pipeline to produce a project blueprint.

    Each agent is injected with the shared ``LLMProvider`` instance.
    Agents run sequentially — each agent's output feeds into the next.
    Execution time and agent list are tracked in ``ExecutionMetadata``.
    """

    def __init__(self) -> None:
        self._llm: LLMProvider = _get_llm_provider()
        settings = get_settings()
        self._provider_name = self._llm.provider_name()
        self._model_name = {
            "groq": settings.groq_model,
            "deepseek": settings.deepseek_model,
            "openrouter": settings.openrouter_model,
            "gemini": settings.gemini_model,
        }.get(self._provider_name, "unknown")
        logger.info(
            "Orchestrator initialised | provider=%s | model=%s",
            self._provider_name,
            self._model_name,
        )

    async def _rate_limit_delay(self) -> None:
        """Introduce a delay between agent runs if using a rate-limited API key."""
        if self._provider_name == "gemini":
            logger.info("Applying rate limit delay (2.0s)...")
            await asyncio.sleep(2.0)
        elif self._provider_name == "groq":
            logger.info("Applying rate limit delay (1.0s)...")
            await asyncio.sleep(1.0)

    async def generate_blueprint(self, project_idea: str) -> ProjectBlueprintResponse:
        """
        Run the full nine-agent pipeline and return a project blueprint.

        Parameters
        ----------
        project_idea:
            The raw project idea string from the user.

        Returns
        -------
        ProjectBlueprintResponse
            Fully merged and validated blueprint with execution metadata.
        """
        pipeline_start = time.perf_counter()
        agents_executed: list[str] = []
        logger.info("Orchestrator | starting pipeline for: %.80s...", project_idea)

        # ── Stage 1: Requirements ─────────────────────────────────────────────
        logger.info("[Requirements Agent] Started")
        requirements_agent = RequirementsAgent(llm=self._llm)
        requirements = await requirements_agent.run(project_idea)
        agents_executed.append("requirements")
        logger.info("[Requirements Agent] Completed")

        await self._rate_limit_delay()

        # ── Stage 2: Documentation ────────────────────────────────────────────
        logger.info("[Documentation Agent] Started")
        documentation_agent = DocumentationAgent(llm=self._llm)
        documentation = await documentation_agent.run(project_idea, requirements)
        agents_executed.append("documentation")
        logger.info("[Documentation Agent] Completed")

        await self._rate_limit_delay()

        # ── Stage 3: Architecture ─────────────────────────────────────────────
        logger.info("[Architecture Agent] Started")
        architecture_agent = ArchitectureAgent(llm=self._llm)
        architecture = await architecture_agent.run(project_idea, requirements)
        agents_executed.append("architecture")
        logger.info("[Architecture Agent] Completed")

        await self._rate_limit_delay()

        # ── Stage 4: Tech Stack ───────────────────────────────────────────────
        logger.info("[TechStack Agent] Started")
        techstack_agent = TechStackAgent(llm=self._llm)
        techstack = await techstack_agent.run(project_idea, requirements, architecture)
        agents_executed.append("techstack")
        logger.info("[TechStack Agent] Completed")

        await self._rate_limit_delay()

        # ── Stage 5: Database Design ──────────────────────────────────────────
        database: dict = {}
        try:
            database_agent = DatabaseAgent(llm=self._llm)
            database = await database_agent.run(project_idea, requirements)
            agents_executed.append("database")
        except Exception as exc:
            logger.warning("[Database Agent] Failed (non-fatal): %s", exc)

        await self._rate_limit_delay()

        # ── Stage 6: API Design ───────────────────────────────────────────────
        api_design: dict = {}
        try:
            api_agent = APIAgent(llm=self._llm)
            api_design = await api_agent.run(project_idea, requirements)
            agents_executed.append("api")
        except Exception as exc:
            logger.warning("[API Agent] Failed (non-fatal): %s", exc)

        await self._rate_limit_delay()

        # ── Stage 7: Roadmap ──────────────────────────────────────────────────
        roadmap_data: dict = {}
        try:
            roadmap_agent = RoadmapAgent(llm=self._llm)
            roadmap_data = await roadmap_agent.run(project_idea, requirements, techstack)
            agents_executed.append("roadmap")
        except Exception as exc:
            logger.warning("[Roadmap Agent] Failed (non-fatal): %s", exc)

        await self._rate_limit_delay()

        # ── Stage 8: Diagrams ─────────────────────────────────────────────────
        diagram_data: dict = {}
        try:
            diagram_agent = DiagramAgent(llm=self._llm)
            diagram_data = await diagram_agent.run(project_idea, architecture, database)
            agents_executed.append("diagram")
        except Exception as exc:
            logger.warning("[Diagram Agent] Failed (non-fatal): %s", exc)

        await self._rate_limit_delay()

        # ── Build metadata ────────────────────────────────────────────────────
        elapsed = round(time.perf_counter() - pipeline_start, 2)
        metadata = ExecutionMetadata(
            execution_time_seconds=elapsed,
            agents_executed=agents_executed,
            provider=self._provider_name,
            model=self._model_name,
            timestamp=datetime.now(timezone.utc).isoformat(),
        )

        # ── Merge all results ─────────────────────────────────────────────
        blueprint = self._merge_results(
            project_idea=project_idea,
            requirements=requirements,
            documentation=documentation,
            architecture=architecture,
            techstack=techstack,
            database=database,
            api_design=api_design,
            roadmap_data=roadmap_data,
            diagram_data=diagram_data,
            metadata=metadata,
        )

        logger.info(
            "Orchestrator | pipeline complete | agents=%d | time=%.2fs",
            len(agents_executed),
            elapsed,
        )
        return blueprint

    # ── Merge helper ──────────────────────────────────────────────────────────

    def _merge_results(
        self,
        *,
        project_idea: str,
        requirements: dict,
        documentation: dict,
        architecture: dict,
        techstack: dict,
        database: dict,
        api_design: dict,
        roadmap_data: dict,
        diagram_data: dict,
        metadata: ExecutionMetadata,
    ) -> ProjectBlueprintResponse:
        """
        Merge all nine agent outputs into a single validated response.

        Uses ``.get()`` with sensible defaults throughout so partial
        agent failures degrade gracefully rather than crashing.
        No viva agent — removed from pipeline.
        """
        # ── Tech Stack (legacy field) ─────────────────────────────────────────
        raw_ts = techstack.get("tech_stack", {})
        tech_stack_obj = TechStackCategory(
            frontend=raw_ts.get("frontend", []),
            backend=raw_ts.get("backend", []),
            database=raw_ts.get("database", []),
            deployment=raw_ts.get("deployment", []),
            ai_ml=raw_ts.get("ai_ml", []),
            devtools=raw_ts.get("devtools", []),
        )

        # ── Architecture Components (legacy) ──────────────────────────────────
        arch_components = [
            ArchitectureComponent(
                name=c.get("name", "Unknown"),
                role=c.get("role", ""),
                interactions=c.get("interactions", []),
            )
            for c in architecture.get("components", [])
        ]

        # ── Legacy DB suggestions ─────────────────────────────────────────────
        db_suggestions = [
            DatabaseSuggestion(
                database_type=db.get("database_type", ""),
                recommended_db=db.get("recommended_db", ""),
                tables_or_collections=db.get("tables_or_collections", []),
                rationale=db.get("rationale", ""),
            )
            for db in architecture.get("database_suggestions", [])
        ]

        # ── Legacy API suggestions ────────────────────────────────────────────
        api_suggestions = [
            APISuggestion(
                method=api.get("method", "GET"),
                endpoint=api.get("endpoint", "/"),
                description=api.get("description", ""),
                request_body=api.get("request_body"),
                response_body=api.get("response_body"),
            )
            for api in architecture.get("api_suggestions", [])
        ]

        # ── Legacy roadmap ────────────────────────────────────────────────────
        roadmap_legacy = [
            RoadmapPhase(
                phase=phase.get("phase", f"Phase {i + 1}"),
                duration=phase.get("duration", "TBD"),
                tasks=phase.get("tasks", []),
            )
            for i, phase in enumerate(techstack.get("development_roadmap", []))
        ]

        # ── Architecture description ───────────────────────────────────────────
        architecture_text = (
            architecture.get("architecture_description")
            or architecture.get("architecture_style")
            or "Architecture details not available."
        )

        # ── NEW: DatabaseDesign ───────────────────────────────────────────────
        database_obj: DatabaseDesign | None = None
        if database:
            tables = [
                DatabaseTable(
                    name=t.get("name", ""),
                    description=t.get("description", ""),
                    columns=[
                        DatabaseColumn(
                            name=col.get("name", ""),
                            type=col.get("type", ""),
                            constraints=col.get("constraints", ""),
                            description=col.get("description", ""),
                        )
                        for col in t.get("columns", [])
                    ],
                )
                for t in database.get("tables", [])
            ]
            sample_queries = [
                SampleQuery(
                    description=q.get("description", ""),
                    sql=q.get("sql", ""),
                )
                for q in database.get("sample_queries", [])
            ]
            database_obj = DatabaseDesign(
                recommended_database=database.get("recommended_database", ""),
                database_type=database.get("database_type", ""),
                design_rationale=database.get("design_rationale", ""),
                tables=tables,
                relationships=database.get("relationships", []),
                sql_schema=database.get("sql_schema", ""),
                indexes=database.get("indexes", []),
                sample_queries=sample_queries,
            )

        # ── NEW: APIDesign ────────────────────────────────────────────────────
        api_design_obj: APIDesign | None = None
        if api_design:
            endpoints = [
                APIEndpoint(
                    method=ep.get("method", "GET"),
                    endpoint=ep.get("endpoint", "/"),
                    description=ep.get("description", ""),
                    auth_required=ep.get("auth_required", True),
                    request_body=ep.get("request_body", {}),
                    response_body=ep.get("response_body", {}),
                    status_codes=ep.get("status_codes", {}),
                )
                for ep in api_design.get("apis", [])
            ]
            groups = [
                APIGroup(
                    group=g.get("group", ""),
                    endpoints=g.get("endpoints", []),
                )
                for g in api_design.get("api_groups", [])
            ]
            api_design_obj = APIDesign(
                base_url=api_design.get("base_url", "/api/v1"),
                authentication=api_design.get("authentication", "JWT"),
                apis=endpoints,
                api_groups=groups,
                error_response_format=api_design.get("error_response_format", {}),
            )

        # ── NEW: WeeklyRoadmap ────────────────────────────────────────────────
        roadmap_obj: WeeklyRoadmap | None = None
        if roadmap_data:
            weekly_tasks = [
                WeeklyTask(
                    week=w.get("week", i + 1),
                    theme=w.get("theme", ""),
                    tasks=w.get("tasks", []),
                    deliverables=w.get("deliverables", []),
                    milestone=w.get("milestone"),
                )
                for i, w in enumerate(roadmap_data.get("roadmap", []))
            ]
            phases = [
                RoadmapPhaseDetail(
                    phase_name=p.get("phase_name", ""),
                    weeks=p.get("weeks", ""),
                    goal=p.get("goal", ""),
                )
                for p in roadmap_data.get("phases", [])
            ]
            roadmap_obj = WeeklyRoadmap(
                total_duration=roadmap_data.get("total_duration", ""),
                team_size=roadmap_data.get("team_size", ""),
                methodology=roadmap_data.get("methodology", "Agile"),
                roadmap=weekly_tasks,
                phases=phases,
                risk_factors=roadmap_data.get("risk_factors", []),
                success_criteria=roadmap_data.get("success_criteria", []),
            )

        # ── NEW: DiagramSet ───────────────────────────────────────────────────
        diagram_obj: DiagramSet | None = None
        mermaid_main = ""
        if diagram_data:
            def _to_mermaid(raw: dict | None) -> MermaidDiagram | None:
                if not raw:
                    return None
                return MermaidDiagram(
                    type=raw.get("type", "flowchart"),
                    title=raw.get("title", ""),
                    mermaid=raw.get("mermaid", ""),
                )

            diagram_obj = DiagramSet(
                architecture_diagram=_to_mermaid(diagram_data.get("architecture_diagram")),
                data_flow_diagram=_to_mermaid(diagram_data.get("data_flow_diagram")),
                er_diagram=_to_mermaid(diagram_data.get("er_diagram")),
                sequence_diagram=_to_mermaid(diagram_data.get("sequence_diagram")),
                mermaid=diagram_data.get("mermaid", ""),
            )
            mermaid_main = diagram_data.get("mermaid", "")

        return ProjectBlueprintResponse(
            # ── Original fields ───────────────────────────────────────────────
            project_idea=project_idea,
            problem_statement=documentation.get("problem_statement", ""),
            project_overview=documentation.get("project_overview", ""),
            objectives=documentation.get("objectives", []),
            target_users=requirements.get("target_users", []),
            features=requirements.get("key_features", []),
            tech_stack=tech_stack_obj,
            architecture=architecture_text,
            architecture_components=arch_components,
            database_suggestions=db_suggestions,
            api_suggestions=api_suggestions,
            development_roadmap=roadmap_legacy,
            future_scope=techstack.get("future_scope", []),
            # ── New fields ────────────────────────────────────────────────────
            database=database_obj,
            apis=api_design_obj,
            roadmap=roadmap_obj,
            mermaid_diagram=mermaid_main,
            diagrams=diagram_obj,
            metadata=metadata,
        )
