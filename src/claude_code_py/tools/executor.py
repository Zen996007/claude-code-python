from __future__ import annotations

from claude_code_py.models.messages import ToolCall, ToolResult
from claude_code_py.permissions.policy import PermissionDecision, PermissionPolicy
from claude_code_py.tools.base import ToolContext
from claude_code_py.tools.registry import ToolRegistry


class ToolExecutor:
    def __init__(self, registry: ToolRegistry, policy: PermissionPolicy, cwd) -> None:
        self.registry = registry
        self.policy = policy
        self.context = ToolContext(cwd=cwd)

    async def execute(self, call: ToolCall) -> ToolResult:
        tool = self.registry.get(call.name)
        if tool is None:
            return ToolResult(
                tool_call_id=call.id,
                name=call.name,
                output=f"Unknown tool: {call.name}",
                is_error=True,
            )

        decision = self.policy.decide(call.name, call.arguments)
        if decision == PermissionDecision.DENY:
            return ToolResult(
                tool_call_id=call.id,
                name=call.name,
                output="Permission denied",
                is_error=True,
            )
        if decision == PermissionDecision.ASK:
            return ToolResult(
                tool_call_id=call.id,
                name=call.name,
                output="Permission requires explicit interactive confirmation; scaffold currently blocks ASK decisions.",
                is_error=True,
                metadata={"permission": "ask"},
            )

        parsed = tool.parse(call.arguments)
        output = await tool.run(parsed, self.context)
        return ToolResult(tool_call_id=call.id, name=call.name, output=output)
