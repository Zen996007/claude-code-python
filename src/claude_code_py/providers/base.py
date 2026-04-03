from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import AsyncIterator

from pydantic import BaseModel, Field

from claude_code_py.models.messages import AgentResponse, Message, ProviderEvent


class ProviderConfig(BaseModel):
    model: str = "mock-provider"
    temperature: float = 0.0
    max_tokens: int = 2048
    api_base: str | None = None
    api_key_env: str | None = None
    system_prompt: str | None = None
    extra_headers: dict[str, str] = Field(default_factory=dict)


class Provider(ABC):
    config: ProviderConfig

    @abstractmethod
    async def generate(self, messages: list[Message], *, tools: list[dict] | None = None) -> AgentResponse:
        raise NotImplementedError

    async def stream(self, messages: list[Message], *, tools: list[dict] | None = None) -> AsyncIterator[ProviderEvent]:
        response = await self.generate(messages, tools=tools)
        yield ProviderEvent(type="response.started", payload={"model": self.config.model})
        if response.text:
            yield ProviderEvent(type="response.delta", payload={"text": response.text})
        for tool_call in response.tool_calls:
            yield ProviderEvent(
                type="tool.call",
                payload={"id": tool_call.id, "name": tool_call.name, "arguments": tool_call.arguments},
            )
        yield ProviderEvent(
            type="response.completed",
            payload={
                "text": response.text,
                "stop_reason": response.stop_reason,
                "metadata": response.metadata,
            },
        )
