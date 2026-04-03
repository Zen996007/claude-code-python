from __future__ import annotations

from claude_code_py.models.messages import AgentResponse, Message
from claude_code_py.tools.executor import ToolExecutor


class AgentLoop:
    def __init__(self, tool_executor: ToolExecutor) -> None:
        self.tool_executor = tool_executor

    async def run(self, messages: list[Message], responder) -> list[Message]:
        new_messages: list[Message] = []
        while True:
            response: AgentResponse = await responder(messages + new_messages)
            if response.text:
                assistant = Message(role="assistant", content=response.text)
                new_messages.append(assistant)
            if response.stop_reason != "tool_use":
                return new_messages
            for tool_call in response.tool_calls:
                result = await self.tool_executor.execute(tool_call)
                new_messages.append(
                    Message(
                        role="tool",
                        name=result.name,
                        content=result.output,
                        metadata={
                            "tool_call_id": result.tool_call_id,
                            "is_error": result.is_error,
                            **result.metadata,
                        },
                    )
                )
