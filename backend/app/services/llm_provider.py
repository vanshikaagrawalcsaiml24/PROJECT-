"""
LLM Provider abstraction layer.

Defines the base interface that all LLM providers must implement.
Agents only interact with this interface — they never import
provider-specific classes directly.
"""

from abc import ABC, abstractmethod


class LLMProvider(ABC):
    """
    Abstract base class for all LLM providers.

    Every concrete provider (DeepSeek, OpenRouter, etc.) must
    implement `generate`.  Agents call ``llm.generate(prompt)``
    without knowing which backend is in use.
    """

    @abstractmethod
    async def generate(
        self,
        prompt: str,
        *,
        temperature: float | None = None,
        max_tokens: int | None = None,
        system_message: str | None = None,
    ) -> str:
        """
        Generate a text completion for the given prompt.

        Parameters
        ----------
        prompt:
            The user prompt to complete.
        temperature:
            Sampling temperature override (uses provider default if None).
        max_tokens:
            Maximum tokens in the response (uses provider default if None).
        system_message:
            Optional system-level instruction to prepend.

        Returns
        -------
        str
            Raw text completion from the model.

        Raises
        ------
        LLMProviderError
            On any unrecoverable provider error.
        """
        ...

    @abstractmethod
    def provider_name(self) -> str:
        """Human-readable provider identifier (e.g. 'deepseek')."""
        ...


class LLMProviderError(Exception):
    """Raised when an LLM provider call fails."""

    def __init__(self, provider: str, message: str, status_code: int | None = None):
        self.provider = provider
        self.status_code = status_code
        super().__init__(f"[{provider}] {message}")
