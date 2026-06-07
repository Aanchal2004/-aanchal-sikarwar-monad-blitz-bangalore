"""
Unified LLM provider abstraction.

Switch provider via LLM_PROVIDER env var: openai | anthropic | openrouter

TODO: Wire real streaming responses for /chat endpoint.
"""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from typing import Any

from config import get_settings

logger = logging.getLogger(__name__)


class BaseLLMProvider(ABC):
    @abstractmethod
    async def chat(self, messages: list[dict[str, str]], **kwargs: Any) -> str:
        pass

    @abstractmethod
    async def embed(self, texts: list[str]) -> list[list[float]]:
        pass


class OpenAIProvider(BaseLLMProvider):
    def __init__(self) -> None:
        settings = get_settings()
        self.model = settings.llm_model
        self._client = None

    def _get_client(self):
        if self._client is None:
            from openai import AsyncOpenAI

            settings = get_settings()
            self._client = AsyncOpenAI(api_key=settings.openai_api_key or None)
        return self._client

    async def chat(self, messages: list[dict[str, str]], **kwargs: Any) -> str:
        settings = get_settings()
        if not settings.openai_api_key:
            return _mock_chat_response(messages)

        client = self._get_client()
        response = await client.chat.completions.create(
            model=kwargs.get("model", self.model),
            messages=messages,  # type: ignore[arg-type]
            temperature=kwargs.get("temperature", settings.llm_temperature),
            max_tokens=kwargs.get("max_tokens", settings.llm_max_tokens),
        )
        return response.choices[0].message.content or ""

    async def embed(self, texts: list[str]) -> list[list[float]]:
        settings = get_settings()
        if not settings.openai_api_key:
            return [[0.1] * 1536 for _ in texts]

        client = self._get_client()
        response = await client.embeddings.create(
            model=settings.embedding_model,
            input=texts,
        )
        return [item.embedding for item in response.data]


class AnthropicProvider(BaseLLMProvider):
    def __init__(self) -> None:
        settings = get_settings()
        self.model = settings.llm_model or "claude-3-5-sonnet-20241022"
        self._client = None

    def _get_client(self):
        if self._client is None:
            from anthropic import AsyncAnthropic

            settings = get_settings()
            self._client = AsyncAnthropic(api_key=settings.anthropic_api_key or None)
        return self._client

    async def chat(self, messages: list[dict[str, str]], **kwargs: Any) -> str:
        settings = get_settings()
        if not settings.anthropic_api_key:
            return _mock_chat_response(messages)

        system = "\n".join(m["content"] for m in messages if m["role"] == "system")
        user_messages = [m for m in messages if m["role"] != "system"]

        client = self._get_client()
        response = await client.messages.create(
            model=kwargs.get("model", self.model),
            max_tokens=kwargs.get("max_tokens", settings.llm_max_tokens),
            system=system or "You are a helpful AI assistant.",
            messages=[  # type: ignore[arg-type]
                {"role": m["role"], "content": m["content"]}
                for m in user_messages
                if m["role"] in ("user", "assistant")
            ],
        )
        return response.content[0].text if response.content else ""

    async def embed(self, texts: list[str]) -> list[list[float]]:
        # Anthropic doesn't provide embeddings — fallback mock or use OpenAI
        logger.warning("Anthropic has no native embeddings; returning mock vectors.")
        return [[0.1] * 1536 for _ in texts]


class OpenRouterProvider(BaseLLMProvider):
    def __init__(self) -> None:
        settings = get_settings()
        self.model = settings.llm_model or "openai/gpt-4o-mini"
        self._client = None

    def _get_client(self):
        if self._client is None:
            from openai import AsyncOpenAI

            settings = get_settings()
            self._client = AsyncOpenAI(
                api_key=settings.openrouter_api_key or None,
                base_url=settings.openrouter_base_url,
                default_headers={
                    "HTTP-Referer": settings.openrouter_site_url,
                    "X-Title": settings.openrouter_app_name,
                },
            )
        return self._client

    async def chat(self, messages: list[dict[str, str]], **kwargs: Any) -> str:
        settings = get_settings()
        if not settings.openrouter_api_key:
            return _mock_chat_response(messages)

        client = self._get_client()
        response = await client.chat.completions.create(
            model=kwargs.get("model", self.model),
            messages=messages,  # type: ignore[arg-type]
            temperature=kwargs.get("temperature", settings.llm_temperature),
            max_tokens=kwargs.get("max_tokens", settings.llm_max_tokens),
        )
        return response.choices[0].message.content or ""

    async def embed(self, texts: list[str]) -> list[list[float]]:
        settings = get_settings()
        if not settings.openrouter_api_key:
            return [[0.1] * 1536 for _ in texts]

        client = self._get_client()
        response = await client.embeddings.create(
            model=settings.embedding_model,
            input=texts,
        )
        return [item.embedding for item in response.data]


def _mock_chat_response(messages: list[dict[str, str]]) -> str:
    last_user = next(
        (m["content"] for m in reversed(messages) if m["role"] == "user"),
        "Hello",
    )
    return (
        f"[MOCK RESPONSE] I received your message: \"{last_user[:200]}\". "
        "Set your API key and LLM_PROVIDER to get real LLM responses."
    )


def get_llm_provider() -> BaseLLMProvider:
    settings = get_settings()
    providers = {
        "openai": OpenAIProvider,
        "anthropic": AnthropicProvider,
        "openrouter": OpenRouterProvider,
    }
    cls = providers.get(settings.llm_provider, OpenAIProvider)
    return cls()
