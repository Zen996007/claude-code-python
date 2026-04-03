from __future__ import annotations

from claude_code_py.models.messages import ToolCall
from claude_code_py.tools.base import Tool


class ToolRegistry:
    def __init__(self) -> None:
        self._tools: dict[str, Tool] = {}

    def register(self, tool: Tool) -> None:
        self._tools[tool.name] = tool

    def register_many(self, tools: list[Tool]) -> None:
        for tool in tools:
            self.register(tool)

    def get(self, name: str) -> Tool | None:
        return self._tools.get(name)

    def names(self) -> list[str]:
        return sorted(self._tools)

    def describe_all(self) -> list[dict]:
        return [self.describe(name) for name in self.names()]

    def describe(self, name: str) -> dict:
        tool = self._tools[name]
        data = tool.describe()
        data["tags"] = list(tool.tags)
        return data

    def build_tool_call(self, name: str, arguments: dict, call_id: str | None = None) -> ToolCall:
        return ToolCall(id=call_id or ToolCall().id, name=name, arguments=arguments)
