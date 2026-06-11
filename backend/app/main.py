"""
ProjectMentor AI — FastAPI application entry point.

Registers:
  - CORS middleware
  - Structured logging (stdout + logs/projectmentor.log)
  - GET  /health
  - POST /generate-blueprint
  - POST /generate-report    (PDF download)
  - POST /export-json        (JSON download)
  - Swagger UI at /docs
  - ReDoc at /redoc
  - OpenAPI JSON at /openapi.json
"""

import logging
import logging.handlers
import os
import sys
import time

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import get_settings
from app.models.schemas import ErrorResponse, HealthResponse
from app.routes.project import router as project_router
from app.routes.reports import router as reports_router

# ── Logging setup ─────────────────────────────────────────────────────────────
settings = get_settings()

_LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
_LOG_DATE = "%Y-%m-%dT%H:%M:%S"
_LOG_LEVEL = getattr(logging, settings.log_level.upper(), logging.INFO)

# Ensure logs/ directory exists
os.makedirs("logs", exist_ok=True)

# Root logger: stdout handler
_stdout_handler = logging.StreamHandler(sys.stdout)
_stdout_handler.setFormatter(logging.Formatter(_LOG_FORMAT, datefmt=_LOG_DATE))

# Root logger: rotating file handler → logs/projectmentor.log
_file_handler = logging.handlers.RotatingFileHandler(
    filename=os.path.join("logs", "projectmentor.log"),
    maxBytes=10 * 1024 * 1024,  # 10 MB per file
    backupCount=5,
    encoding="utf-8",
)
_file_handler.setFormatter(logging.Formatter(_LOG_FORMAT, datefmt=_LOG_DATE))

logging.basicConfig(
    level=_LOG_LEVEL,
    handlers=[_stdout_handler, _file_handler],
)
logger = logging.getLogger(__name__)

# ── FastAPI application ────────────────────────────────────────────────────────
app = FastAPI(
    title=settings.app_name,
    description=(
        "**ProjectMentor AI** converts a project idea into a complete, production-ready project blueprint.\n\n"
        "## Eight-Agent Pipeline\n"
        "1. **Requirements Agent** — features, modules, target users\n"
        "2. **Documentation Agent** — problem statement, objectives, overview\n"
        "3. **Architecture Agent** — system design & components\n"
        "4. **TechStack Agent** — technology recommendations\n"
        "5. **Database Agent** — normalised schema, SQL DDL, relationships\n"
        "6. **API Agent** — complete REST API specification\n"
        "7. **Roadmap Agent** — week-by-week development timeline\n"
        "8. **Diagram Agent** — Mermaid architecture & ER diagrams\n\n"
        "## Endpoints\n"
        "- `POST /generate-blueprint` — Returns full blueprint as JSON\n"
        "- `POST /generate-report` — Returns complete blueprint as downloadable PDF\n"
        "- `POST /export-json` — Returns complete blueprint as downloadable JSON file\n"
        "- `GET  /health` — Service health check\n"
    ),
    version=settings.app_version,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    contact={
        "name": "ProjectMentor AI",
        "url": "https://github.com/projectmentor-ai",
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT",
    },
)

# ── CORS middleware ────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Request logging middleware ─────────────────────────────────────────────────
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log every incoming request and its processing time."""
    start = time.perf_counter()
    logger.info("→ %s %s", request.method, request.url.path)

    response = await call_next(request)

    duration_ms = (time.perf_counter() - start) * 1000
    logger.info(
        "← %s %s | status=%d | %.1fms",
        request.method,
        request.url.path,
        response.status_code,
        duration_ms,
    )
    return response


# ── Global exception handler ──────────────────────────────────────────────────
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Catch-all handler for unhandled exceptions."""
    logger.exception("Unhandled exception on %s %s", request.method, request.url.path)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ErrorResponse(
            error="Internal Server Error",
            detail=str(exc),
            code=500,
        ).model_dump(),
    )


# ── Lifecycle events ──────────────────────────────────────────────────────────
@app.on_event("startup")
async def on_startup() -> None:
    """Log startup information."""
    logger.info(
        "[STARTUP] %s v%s starting | provider=%s | debug=%s",
        settings.app_name,
        settings.app_version,
        settings.llm_provider,
        settings.debug,
    )


@app.on_event("shutdown")
async def on_shutdown() -> None:
    """Cleanup on shutdown."""
    logger.info("[SHUTDOWN] %s shutting down", settings.app_name)


# ── Health endpoint ───────────────────────────────────────────────────────────
@app.get(
    "/health",
    response_model=HealthResponse,
    status_code=status.HTTP_200_OK,
    tags=["Meta"],
    summary="Health check",
    description="Returns the service status, version, and active LLM provider.",
)
async def health_check() -> HealthResponse:
    """
    Lightweight health check endpoint.

    Returns
    -------
    HealthResponse
        Service status, version, and active LLM provider name.
    """
    return HealthResponse(
        status="ok",
        version=settings.app_version,
        provider=settings.llm_provider,
    )


# ── Root redirect ─────────────────────────────────────────────────────────────
@app.get(
    "/",
    tags=["Meta"],
    summary="API root",
    include_in_schema=False,
)
async def root():
    """Redirect hint for the API root."""
    return {
        "message": f"Welcome to {settings.app_name}",
        "docs": "/docs",
        "health": "/health",
    }


# ── Register routers ──────────────────────────────────────────────────────────
app.include_router(project_router)
app.include_router(reports_router)
