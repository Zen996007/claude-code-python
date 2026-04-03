from __future__ import annotations

from claude_code_py.models.messages import Message
from claude_code_py.providers.base import Provider
from claude_code_py.storage.transcript import TranscriptStore
from claude_code_py.tools.executor import ToolExecutor
from claude_code_py.tools.registry import ToolRegistry


class AgentLoop:
    def __init__(
        self,
        provider: Provider,
        tool_executor: ToolExecutor,
        tool_registry: ToolRegistry,
        max_turns: int = 12,
        transcript: TranscriptStore | None = None,
    ) -> None:
        self.provider = provider
        self.tool_executor = tool_executor
        self.tool_registry = tool_registry
        self.max_turns = max_turns
        self.transcript = transcript

    async def run(self, messages: list[Message]) -> list[Message]:
        new_messages: list[Message] = []
        for turn_index in range(1, self.max_turns + 1):
            response = await self.provider.generate(messages + new_messages, tools=self.tool_registry.describe_all())
            if self.transcript:
                self.transcript.append_event(
                    "agent_response",
                    {
                        "turn_index": turn_index,
                        "stop_reason": response.stop_reason,
                        "metadata": response.metadata,
                    },
                )
            if response.text:
                assistant = Message(role="assistant", content=response.text, metadata=response.metadata)
                new_messages.append(assistant)
            if response.stop_reason != "tool_use":
                return new_messages
            for tool_call in response.tool_calls:
                result = await self.tool_executor.execute(tool_call)
                if self.transcript:
                    self.transcript.append_tool_result(result)
                new_messages.append(result.to_tool_message())
        raise RuntimeError(f"Agent loop exceeded max_turns={self.max_turns}")
