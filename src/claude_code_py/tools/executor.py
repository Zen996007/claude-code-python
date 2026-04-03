from __future__ import annotations

from collections.abc import Awaitable, Callable
from pathlib import Path

from claude_code_py.models.messages import ToolCall, ToolResult
from claude_code_py.permissions.policy import (
    PermissionDecision,
    PermissionPolicy,
    PermissionRequest,
    PermissionResult,
)
from claude_code_py.tools.base import ToolContext
from claude_code_py.tools.registry import ToolRegistry

ApprovalHandler = Callable[[PermissionRequest, PermissionResult], Awaitable[PermissionDecision]]


class ToolExecutor:
    def __init__(
        self,
        registry: ToolRegistry,
        policy: PermissionPolicy,
        cwd: Path,
        approval_handler: ApprovalHandler | None = None,
        session_id: str | None = None,
    ) -> None:
        self.registry = registry
        self.policy = policy
        self.context = ToolContext(cwd=cwd, session_id=session_id)
        self.approval_handler = approval_handler

    async def execute(self, call: ToolCall) -> ToolResult:
        tool = self.registry.get(call.name)
        if tool is None:
            return ToolResult(
                tool_call_id=call.id,
                name=call.name,
                output=f"Unknown tool: {call.name}",
                is_error=True,
            )

        request = PermissionRequest(tool_name=call.name, arguments=call.arguments, cwd=self.context.cwd)
        policy_result = self.policy.evaluate(request)
        final_decision = policy_result.decision
        if final_decision == PermissionDecision.ASK:
            if self.approval_handler is None:
                return ToolResult(
                    tool_call_id=call.id,
                    name=call.name,
                    output=f"Permission requires approval: {policy_result.reason}",
                    is_error=True,
                    metadata={"permission": "ask", "reason": policy_result.reason},
                )
            final_decision = await self.approval_handler(request, policy_result)

        if final_decision == PermissionDecision.DENY:
            return ToolResult(
                tool_call_id=call.id,
                name=call.name,
                output=f"Permission denied: {policy_result.reason}",
                is_error=True,
                metadata={"permission": "deny", "reason": policy_result.reason},
            )

        try:
            parsed = tool.parse(call.arguments)
            output = await tool.run(parsed, self.context)
        except Exception as exc:
            return ToolResult(
                tool_call_id=call.id,
                name=call.name,
                output=str(exc),
                is_error=True,
                metadata={"permission": "allow", "reason": policy_result.reason},
            )

        return ToolResult(
            tool_call_id=call.id,
            name=call.name,
            output=output,
            metadata={"permission": "allow", "reason": policy_result.reason},
        )
