"""
Application configuration module.
Loads and validates all environment variables using pydantic-settings pattern.
"""

import logging
from functools import lru_cache
from typing import Literal

from dotenv import load_dotenv
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings

load_dotenv()

logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    """
    Central settings class loaded from environment variables.
    All fields are validated at startup — no runtime surprises.
    """

    # ── LLM Provider ─────────────────────────────────────────────────────────
    llm_provider: Literal["groq", "deepseek", "openrouter", "gemini"] = Field(
        default="groq",
        description="Active LLM provider (groq | deepseek | openrouter | gemini)",
    )

    # ── Gemini ────────────────────────────────────────────────────────────────
    gemini_api_key: str = Field(
        default="",
        description="Google Gemini API key",
    )
    gemini_model: str = Field(
        default="gemini-1.5-flash",
        description="Gemini model identifier",
    )

    # ── DeepSeek ─────────────────────────────────────────────────────────────
    deepseek_api_key: str = Field(
        default="",
        description="DeepSeek API key",
    )
    deepseek_base_url: str = Field(
        default="https://api.deepseek.com",
        description="DeepSeek base URL (OpenAI-compatible)",
    )
    deepseek_model: str = Field(
        default="deepseek-chat",
        description="DeepSeek model identifier",
    )

    # ── OpenRouter ────────────────────────────────────────────────────────────
    openrouter_api_key: str = Field(
        default="",
        description="OpenRouter API key",
    )
    openrouter_base_url: str = Field(
        default="https://openrouter.ai/api/v1",
        description="OpenRouter base URL",
    )
    openrouter_model: str = Field(
        default="deepseek/deepseek-chat",
        description="OpenRouter model identifier",
    )

    # ── Groq ──────────────────────────────────────────────────────────────────
    groq_api_key: str = Field(
        default="",
        description="Groq API key",
    )
    groq_base_url: str = Field(
        default="https://api.groq.com/openai/v1",
        description="Groq base URL",
    )
    groq_model: str = Field(
        default="llama-3.3-70b-versatile",
        description="Groq model identifier",
    )

    # ── Application ───────────────────────────────────────────────────────────
    app_name: str = Field(default="ProjectMentor AI", description="Application name")
    app_version: str = Field(default="1.0.0", description="Application version")
    debug: bool = Field(default=False, description="Enable debug mode")
    log_level: str = Field(default="INFO", description="Logging level")

    # ── CORS ──────────────────────────────────────────────────────────────────
    cors_origins: list[str] = Field(
        default=["*"],
        description="Allowed CORS origins",
    )

    # ── LLM Generation ────────────────────────────────────────────────────────
    llm_temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    llm_max_tokens: int = Field(default=4096, ge=256, le=32768)
    llm_timeout_seconds: int = Field(default=120, ge=10, le=600)

    @field_validator(
        "groq_api_key",
        "deepseek_api_key",
        "openrouter_api_key",
        "gemini_api_key",
        mode="before",
    )
    @classmethod
    def strip_whitespace(cls, v: str) -> str:
        return v.strip() if isinstance(v, str) else v

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
        "extra": "ignore",
    }


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return a cached singleton of application settings."""
    settings = Settings()

    active_model = {
        "groq": settings.groq_model,
        "deepseek": settings.deepseek_model,
        "openrouter": settings.openrouter_model,
        "gemini": settings.gemini_model,
    }.get(settings.llm_provider, "unknown")

    logger.info(
        "Settings loaded | provider=%s | model=%s",
        settings.llm_provider,
        active_model,
    )
    return settings
