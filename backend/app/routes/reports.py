"""
Report and export routes.

Defines:
    POST /generate-report  — Generate full pipeline then return PDF download
    POST /export-json      — Generate full pipeline then return JSON download
"""

import json
import logging
from datetime import datetime

from fastapi import APIRouter, HTTPException, Request, status
from fastapi.responses import Response, StreamingResponse
import io

from app.models.schemas import ProjectIdeaRequest, ReportRequest
from app.services.llm_provider import LLMProviderError
from app.services.orchestrator import Orchestrator
from app.services.pdf_service import generate_pdf

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="",
    tags=["Reports & Export"],
)


@router.post(
    "/generate-report",
    status_code=status.HTTP_200_OK,
    summary="Generate a complete project blueprint and download as PDF",
    description=(
        "Runs the full eight-agent AI pipeline for the given project idea and "
        "returns a professionally formatted, downloadable PDF report containing "
        "all blueprint sections: problem statement, objectives, features, tech stack, "
        "architecture, database design, API design, roadmap, and future scope."
    ),
    response_description="PDF file download",
    responses={
        200: {
            "description": "PDF report generated successfully",
            "content": {"application/pdf": {}},
        },
        422: {"description": "Validation error"},
        500: {"description": "Internal server error"},
        502: {"description": "LLM provider error"},
    },
)
async def generate_report(
    payload: ReportRequest,
    request: Request,
) -> Response:
    """
    Generate a project blueprint and return it as a downloadable PDF.

    Parameters
    ----------
    payload:
        ``ReportRequest`` with a ``project_idea`` string.
    request:
        FastAPI request object for logging.

    Returns
    -------
    Response
        A ``application/pdf`` response with Content-Disposition header
        set to trigger a file download.
    """
    client_host = request.client.host if request.client else "unknown"
    logger.info(
        "POST /generate-report | client=%s | idea=%.80s...",
        client_host,
        payload.project_idea,
    )

    try:
        orchestrator = Orchestrator()
        blueprint = await orchestrator.generate_blueprint(payload.project_idea)
    except LLMProviderError as exc:
        logger.error("LLM provider error in /generate-report: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"LLM provider error: {exc}",
        ) from exc
    except ValueError as exc:
        logger.error("Agent output parsing error in /generate-report: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to parse agent output: {exc}",
        ) from exc
    except Exception as exc:
        logger.exception("Unexpected error in /generate-report")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error: {exc}",
        ) from exc

    # Generate PDF bytes
    try:
        pdf_bytes = generate_pdf(blueprint)
    except Exception as exc:
        logger.exception("PDF generation failed")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"PDF generation failed: {exc}",
        ) from exc

    # Build a clean filename from the project idea
    safe_name = "".join(
        c if c.isalnum() or c in (" ", "-") else ""
        for c in payload.project_idea[:40]
    ).strip().replace(" ", "_")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"ProjectBlueprint_{safe_name}_{timestamp}.pdf"

    logger.info(
        "POST /generate-report | complete | pdf_size=%d bytes | filename=%s",
        len(pdf_bytes),
        filename,
    )

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
            "Content-Length": str(len(pdf_bytes)),
        },
    )


@router.post(
    "/export-json",
    status_code=status.HTTP_200_OK,
    summary="Generate a complete project blueprint and download as JSON",
    description=(
        "Runs the full eight-agent AI pipeline for the given project idea and "
        "returns the complete blueprint as a downloadable JSON file. "
        "Useful for integrating the blueprint into other tools or storing it for later use."
    ),
    response_description="JSON file download",
    responses={
        200: {
            "description": "JSON export generated successfully",
            "content": {"application/json": {}},
        },
        422: {"description": "Validation error"},
        500: {"description": "Internal server error"},
        502: {"description": "LLM provider error"},
    },
)
async def export_json(
    payload: ProjectIdeaRequest,
    request: Request,
) -> Response:
    """
    Generate a project blueprint and return it as a downloadable JSON file.

    Parameters
    ----------
    payload:
        ``ProjectIdeaRequest`` with a ``project_idea`` string.
    request:
        FastAPI request object for logging.

    Returns
    -------
    Response
        An ``application/json`` response with Content-Disposition header
        set to trigger a file download.
    """
    client_host = request.client.host if request.client else "unknown"
    logger.info(
        "POST /export-json | client=%s | idea=%.80s...",
        client_host,
        payload.project_idea,
    )

    try:
        orchestrator = Orchestrator()
        blueprint = await orchestrator.generate_blueprint(payload.project_idea)
    except LLMProviderError as exc:
        logger.error("LLM provider error in /export-json: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"LLM provider error: {exc}",
        ) from exc
    except ValueError as exc:
        logger.error("Agent output parsing error in /export-json: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to parse agent output: {exc}",
        ) from exc
    except Exception as exc:
        logger.exception("Unexpected error in /export-json")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error: {exc}",
        ) from exc

    # Serialise to JSON with indentation for readability
    json_content = blueprint.model_dump_json(indent=2)

    # Build a clean filename
    safe_name = "".join(
        c if c.isalnum() or c in (" ", "-") else ""
        for c in payload.project_idea[:40]
    ).strip().replace(" ", "_")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"ProjectBlueprint_{safe_name}_{timestamp}.json"

    logger.info(
        "POST /export-json | complete | json_size=%d bytes | filename=%s",
        len(json_content),
        filename,
    )

    return Response(
        content=json_content,
        media_type="application/json",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
            "Content-Length": str(len(json_content.encode())),
        },
    )
