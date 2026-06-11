"""
Google Gemini LLM provider.

Uses the Google Generative Language REST API (generateContent endpoint)
via HTTPX (async). Implements the LLMProvider interface so agents call
``llm.generate(prompt)`` with no awareness of Gemini specifics.

API Reference:
    https://ai.google.dev/api/generate-content
"""

import asyncio
import logging
import random
import re

import httpx

from app.config import get_settings
from app.services.llm_provider import LLMProvider, LLMProviderError

logger = logging.getLogger(__name__)

# Gemini REST endpoint template
_GEMINI_URL = (
    "https://generativelanguage.googleapis.com/v1beta/models"
    "/{model}:generateContent?key={api_key}"
)


class GeminiProvider(LLMProvider):
    """
    Concrete LLM provider for Google Gemini Flash.

    Wraps the ``generateContent`` REST endpoint using HTTPX (async).
    No SDK dependency — pure HTTP for maximum portability.
    """

    def __init__(self) -> None:
        settings = get_settings()
        self._api_key = settings.gemini_api_key
        self._model = settings.gemini_model
        self._default_temperature = settings.llm_temperature
        self._default_max_tokens = settings.llm_max_tokens
        self._timeout = settings.llm_timeout_seconds

        if not self._api_key:
            logger.warning(
                "GEMINI_API_KEY is not set — API calls will fail at runtime."
            )

    def provider_name(self) -> str:
        return "gemini"

    async def generate(
        self,
        prompt: str,
        *,
        temperature: float | None = None,
        max_tokens: int | None = None,
        system_message: str | None = None,
    ) -> str:
        """
        Send a content generation request to the Gemini API.

        Parameters
        ----------
        prompt:
            User prompt content.
        temperature:
            Override sampling temperature (uses settings default if None).
        max_tokens:
            Override max output tokens (uses settings default if None).
        system_message:
            Optional system instruction injected as a systemInstruction block.

        Returns
        -------
        str
            Decoded text content from the first candidate part.

        Raises
        ------
        LLMProviderError
            On HTTP errors, timeouts, or unexpected response shapes.
        """
        url = _GEMINI_URL.format(model=self._model, api_key=self._api_key)

        # ── Build request payload ─────────────────────────────────────────────
        payload: dict = {
            "contents": [
                {
                    "role": "user",
                    "parts": [{"text": prompt}],
                }
            ],
            "generationConfig": {
                "temperature": temperature
                if temperature is not None
                else self._default_temperature,
                "maxOutputTokens": max_tokens
                if max_tokens is not None
                else self._default_max_tokens,
                "responseMimeType": "text/plain",
            },
        }

        # Gemini supports a top-level systemInstruction block
        if system_message:
            payload["systemInstruction"] = {
                "parts": [{"text": system_message}]
            }

        logger.debug(
            "Gemini request | model=%s | prompt_len=%d",
            self._model,
            len(prompt),
        )

        # ── HTTP call with robust retry mechanism (backoff & jitter) ───────────
        max_retries = 5
        base_delay = 2.0
        response = None

        for attempt in range(max_retries):
            try:
                async with httpx.AsyncClient(timeout=self._timeout) as client:
                    response = await client.post(
                        url,
                        json=payload,
                        headers={"Content-Type": "application/json"},
                    )
                    response.raise_for_status()
                break  # Successful response, exit the retry loop
            except httpx.HTTPStatusError as exc:
                if exc.response.status_code == 429 and attempt < max_retries - 1:
                    # Try to parse explicit wait time from Google's error message (e.g. "Please retry in 9.908453577s.")
                    body_text = exc.response.text
                    match = re.search(r"Please retry in ([\d\.]+)s", body_text)
                    if match:
                        delay = float(match.group(1)) + 1.0  # Add a 1.0s buffer
                    else:
                        retry_after = exc.response.headers.get("retry-after")
                        if retry_after and retry_after.replace(".", "", 1).isdigit():
                            delay = float(retry_after) + 0.5
                        else:
                            delay = base_delay * (2 ** attempt) + random.uniform(0.1, 1.0)
                    
                    logger.warning(
                        "[Gemini] Too Many Requests (429). Retrying in %.2fs (attempt %d/%d)...",
                        delay,
                        attempt + 1,
                        max_retries,
                    )
                    await asyncio.sleep(delay)
                    continue
                raise LLMProviderError(
                    "gemini",
                    f"HTTP {exc.response.status_code}: {exc.response.text[:500]}",
                    status_code=exc.response.status_code,
                ) from exc
            except httpx.TimeoutException as exc:
                if attempt < max_retries - 1:
                    delay = base_delay * (2 ** attempt) + random.uniform(0.1, 1.0)
                    logger.warning(
                        "[Gemini] Request timeout. Retrying in %.2fs (attempt %d/%d)...",
                        delay,
                        attempt + 1,
                        max_retries,
                    )
                    await asyncio.sleep(delay)
                    continue
                raise LLMProviderError(
                    "gemini", f"Request timed out after {self._timeout}s"
                ) from exc
            except httpx.RequestError as exc:
                if attempt < max_retries - 1:
                    delay = base_delay * (2 ** attempt) + random.uniform(0.1, 1.0)
                    logger.warning(
                        "[Gemini] Network error: %s. Retrying in %.2fs (attempt %d/%d)...",
                        str(exc),
                        delay,
                        attempt + 1,
                        max_retries,
                    )
                    await asyncio.sleep(delay)
                    continue
                raise LLMProviderError("gemini", f"Network error: {exc}") from exc

        if response is None:
            raise LLMProviderError("gemini", "Failed to get response after multiple retries.")

        # ── Parse response ────────────────────────────────────────────────────
        try:
            data = response.json()
            content: str = data["candidates"][0]["content"]["parts"][0]["text"]
        except (KeyError, IndexError, ValueError) as exc:
            raise LLMProviderError(
                "gemini",
                f"Unexpected response shape: {response.text[:300]}",
            ) from exc

        # Surface safety blocks gracefully
        finish_reason = (
            data.get("candidates", [{}])[0].get("finishReason", "STOP")
        )
        if finish_reason not in ("STOP", "MAX_TOKENS"):
            logger.warning("Gemini finishReason=%s", finish_reason)

        usage = data.get("usageMetadata", {})
        logger.debug(
            "Gemini response | inputTokens=%s | outputTokens=%s",
            usage.get("promptTokenCount"),
            usage.get("candidatesTokenCount"),
        )
        return content
