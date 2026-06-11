"""
OpenRouter LLM provider.

Uses the OpenAI-compatible chat completions API via HTTPX (async).
Implements the LLMProvider interface — agents call ``llm.generate(prompt)``
without any awareness of OpenRouter specifics.
"""

import logging

import httpx

from app.config import get_settings
from app.services.llm_provider import LLMProvider, LLMProviderError

logger = logging.getLogger(__name__)


class OpenRouterProvider(LLMProvider):
    """
    Concrete LLM provider for OpenRouter.

    OpenRouter exposes an OpenAI-compatible endpoint so the implementation
    is nearly identical to DeepSeekProvider — both are kept separate so
    each can evolve independently (headers, retry logic, model defaults, etc.).
    """

    def __init__(self) -> None:
        settings = get_settings()
        self._api_key = settings.openrouter_api_key
        self._base_url = settings.openrouter_base_url.rstrip("/")
        self._model = settings.openrouter_model
        self._default_temperature = settings.llm_temperature
        self._default_max_tokens = settings.llm_max_tokens
        self._timeout = settings.llm_timeout_seconds

        if not self._api_key:
            logger.warning(
                "OPENROUTER_API_KEY is not set — API calls will fail at runtime."
            )

    def provider_name(self) -> str:
        return "openrouter"

    async def generate(
        self,
        prompt: str,
        *,
        temperature: float | None = None,
        max_tokens: int | None = None,
        system_message: str | None = None,
    ) -> str:
        """
        Send a chat completion request to the OpenRouter API.

        Returns
        -------
        str
            Decoded text content from the first completion choice.

        Raises
        ------
        LLMProviderError
            On HTTP errors, timeouts, or unexpected response shapes.
        """
        messages: list[dict] = []
        if system_message:
            messages.append({"role": "system", "content": system_message})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": self._model,
            "messages": messages,
            "temperature": temperature if temperature is not None else self._default_temperature,
            "max_tokens": max_tokens if max_tokens is not None else self._default_max_tokens,
        }

        # OpenRouter requires HTTP-Referer & X-Title for ranking (optional but recommended)
        settings = get_settings()
        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://projectmentor.ai",
            "X-Title": settings.app_name,
        }

        url = f"{self._base_url}/chat/completions"
        logger.debug(
            "OpenRouter request | model=%s | prompt_len=%d", self._model, len(prompt)
        )

        try:
            async with httpx.AsyncClient(timeout=self._timeout) as client:
                response = await client.post(url, json=payload, headers=headers)
                response.raise_for_status()
        except httpx.TimeoutException as exc:
            raise LLMProviderError(
                "openrouter", f"Request timed out after {self._timeout}s"
            ) from exc
        except httpx.HTTPStatusError as exc:
            raise LLMProviderError(
                "openrouter",
                f"HTTP {exc.response.status_code}: {exc.response.text[:500]}",
                status_code=exc.response.status_code,
            ) from exc
        except httpx.RequestError as exc:
            raise LLMProviderError("openrouter", f"Network error: {exc}") from exc

        try:
            data = response.json()
            content: str = data["choices"][0]["message"]["content"]
        except (KeyError, IndexError, ValueError) as exc:
            raise LLMProviderError(
                "openrouter", f"Unexpected response shape: {response.text[:300]}"
            ) from exc

        logger.debug(
            "OpenRouter response | tokens=%s", data.get("usage", {}).get("total_tokens")
        )
        return content
