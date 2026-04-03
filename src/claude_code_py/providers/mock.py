from __future__ import annotations

from claude_code_py.models.messages import AgentResponse, Message, ToolCall
from claude_code_py.providers.base import Provider, ProviderConfig


class MockProvider(Provider):
    def __init__(self, config: ProviderConfig | None = None) -> None:
        self.config = config or ProviderConfig()

    async def generate(self, messages: list[Message], *, tools: list[dict] | None = None) -> AgentResponse:
        last = messages[-1].content.strip()
        lowered = last.lower()
        if lowered.startswith("read "):
            return AgentResponse(
                stop_reason="tool_use",
                tool_calls=[ToolCall(name="file_read", arguments={"path": last[5:].strip()})],
                metadata={"provider": "mock"},
            )
        if lowered.startswith("list"):
            target = last[4:].strip() or "."
            return AgentResponse(
                stop_reason="tool_use",
                tool_calls=[ToolCall(name="file_list", arguments={"path": target})],
                metadata={"provider": "mock"},
            )
        return AgentResponse(text=f"MockProvider: {last}", metadata={"provider": "mock"})
