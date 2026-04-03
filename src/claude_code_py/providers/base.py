from __future__ import annotations

from abc import ABC, abstractmethod

from pydantic import BaseModel, Field

from claude_code_py.models.messages import AgentResponse, Message


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
