"""
Groq LLM provider.

Uses the OpenAI-compatible chat completions API via HTTPX (async).
Implements the LLMProvider interface so agents can call
``llm.generate(prompt)`` without knowing Groq specifics.
"""

import asyncio
import logging
import random
import re

import httpx

from app.config import get_settings
from app.services.llm_provider import LLMProvider, LLMProviderError

logger = logging.getLogger(__name__)


class GroqProvider(LLMProvider):
    """
    Concrete LLM provider for Groq.

    Wraps the OpenAI-compatible ``/chat/completions`` endpoint.
    A single ``httpx.AsyncClient`` is reused across calls for
    connection pooling. Includes automatic retries for rate limits (429).
    """

    def __init__(self) -> None:
        settings = get_settings()
        self._api_key = settings.groq_api_key
        self._base_url = settings.groq_base_url.rstrip("/")
        self._model = settings.groq_model
        self._default_temperature = settings.llm_temperature
        self._default_max_tokens = settings.llm_max_tokens
        self._timeout = settings.llm_timeout_seconds

        if not self._api_key:
            logger.warning(
                "GROQ_API_KEY is not set — API calls will fail at runtime."
            )

    def provider_name(self) -> str:
        return "groq"

    async def generate(
        self,
        prompt: str,
        *,
        temperature: float | None = None,
        max_tokens: int | None = None,
        system_message: str | None = None,
    ) -> str:
        """
        Send a chat completion request to the Groq API.

        Parameters
        ----------
        prompt:
            User-role message content.
        temperature:
            Override sampling temperature (defaults to settings value).
        max_tokens:
            Override max tokens (defaults to settings value).
        system_message:
            Optional system-role instruction injected before the user turn.

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

        # Groq llama-3.3-70b-versatile supports json_object output format
        # If the prompt instructs the model to return JSON, we can enforce it!
        payload = {
            "model": self._model,
            "messages": messages,
            "temperature": temperature if temperature is not None else self._default_temperature,
            "max_tokens": max_tokens if max_tokens is not None else self._default_max_tokens,
        }

        # Check if the prompt requires a JSON response.
        # All our agents ask for JSON, so we can enforce json_object response format on Groq!
        if "json" in prompt.lower():
            payload["response_format"] = {"type": "json_object"}

        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
        }

        url = f"{self._base_url}/chat/completions"
        logger.debug("Groq request | model=%s | prompt_len=%d", self._model, len(prompt))

        max_retries = 5
        base_delay = 2.0
        response = None

        for attempt in range(max_retries):
            try:
                async with httpx.AsyncClient(timeout=self._timeout) as client:
                    response = await client.post(url, json=payload, headers=headers)
                    response.raise_for_status()
                break  # Success!
            except httpx.HTTPStatusError as exc:
                if exc.response.status_code == 429 and attempt < max_retries - 1:
                    # Look for retry-after header or compute delay
                    retry_after = exc.response.headers.get("retry-after")
                    # Alternatively, check for wait time in the response JSON message
                    body_text = exc.response.text
                    match = re.search(r"try again in ([\d\.]+)s", body_text.lower())
                    if match:
                        delay = float(match.group(1)) + 0.5
                    elif retry_after and retry_after.replace(".", "", 1).isdigit():
                        delay = float(retry_after) + 0.5
                    else:
                        delay = base_delay * (2 ** attempt) + random.uniform(0.1, 1.0)

                    logger.warning(
                        "[Groq] Too Many Requests (429). Retrying in %.2fs (attempt %d/%d)...",
                        delay,
                        attempt + 1,
                        max_retries,
                    )
                    await asyncio.sleep(delay)
                    continue
                raise LLMProviderError(
                    "groq",
                    f"HTTP {exc.response.status_code}: {exc.response.text[:500]}",
                    status_code=exc.response.status_code,
                ) from exc
            except httpx.TimeoutException as exc:
                if attempt < max_retries - 1:
                    delay = base_delay * (2 ** attempt) + random.uniform(0.1, 1.0)
                    logger.warning(
                        "[Groq] Request timeout. Retrying in %.2fs (attempt %d/%d)...",
                        delay,
                        attempt + 1,
                        max_retries,
                    )
                    await asyncio.sleep(delay)
                    continue
                raise LLMProviderError(
                    "groq", f"Request timed out after {self._timeout}s"
                ) from exc
            except httpx.RequestError as exc:
                if attempt < max_retries - 1:
                    delay = base_delay * (2 ** attempt) + random.uniform(0.1, 1.0)
                    logger.warning(
                        "[Groq] Network error. Retrying in %.2fs (attempt %d/%d)...",
                        delay,
                        attempt + 1,
                        max_retries,
                    )
                    await asyncio.sleep(delay)
                    continue
                raise LLMProviderError("groq", f"Network error: {exc}") from exc

        if response is None:
            raise LLMProviderError("groq", "Failed to get response from Groq after multiple retries.")

        try:
            data = response.json()
            content: str = data["choices"][0]["message"]["content"]
        except (KeyError, IndexError, ValueError) as exc:
            raise LLMProviderError(
                "groq", f"Unexpected response shape: {response.text[:300]}"
            ) from exc

        logger.debug("Groq response | tokens=%s", data.get("usage", {}).get("total_tokens"))
        return content
