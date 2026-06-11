"""
Project blueprint routes.

Defines:
    POST /generate-blueprint  — Generate a complete project blueprint
"""

import logging

from fastapi import APIRouter, HTTPException, Request, status

from app.models.schemas import ProjectBlueprintResponse, ProjectIdeaRequest
from app.services.llm_provider import LLMProviderError
from app.services.orchestrator import Orchestrator

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="",
    tags=["Blueprint"],
)


@router.post(
    "/generate-blueprint",
    response_model=ProjectBlueprintResponse,
    status_code=status.HTTP_200_OK,
    summary="Generate a complete project blueprint",
    description=(
        "Accepts a project idea and runs it through a four-stage AI pipeline "
        "(Requirements → Documentation → Architecture → Tech Stack) to produce "
        "a comprehensive project blueprint."
    ),
    responses={
        200: {"description": "Blueprint generated successfully"},
        422: {"description": "Validation error — check request body"},
        500: {"description": "Internal server error during generation"},
        502: {"description": "LLM provider error"},
    },
)
async def generate_blueprint(
    payload: ProjectIdeaRequest,
    request: Request,
) -> ProjectBlueprintResponse:
    """
    Generate a complete project blueprint from a project idea.

    The endpoint orchestrates four specialized AI agents in sequence.
    Typical response time: 30–90 seconds depending on idea complexity.

    Parameters
    ----------
    payload:
        ``ProjectIdeaRequest`` with a ``project_idea`` string.
    request:
        FastAPI request object (used for tracing / logging).

    Returns
    -------
    ProjectBlueprintResponse
        Fully merged blueprint with all sections populated.
    """
    client_host = request.client.host if request.client else "unknown"
    logger.info(
        "POST /generate-blueprint | client=%s | idea=%.80s...",
        client_host,
        payload.project_idea,
    )

    try:
        orchestrator = Orchestrator()
        blueprint = await orchestrator.generate_blueprint(payload.project_idea)
    except LLMProviderError as exc:
        logger.error("LLM provider error: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"LLM provider error: {exc}",
        ) from exc
    except ValueError as exc:
        logger.error("Agent output parsing error: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to parse agent output: {exc}",
        ) from exc
    except Exception as exc:
        logger.exception("Unexpected error in /generate-blueprint")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error: {exc}",
        ) from exc

    logger.info(
        "POST /generate-blueprint | complete | features=%d | roadmap_phases=%d",
        len(blueprint.features),
        len(blueprint.development_roadmap),
    )
    return blueprint
