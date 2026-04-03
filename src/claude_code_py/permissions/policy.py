from __future__ import annotations

from enum import Enum


class PermissionDecision(str, Enum):
    ALLOW = "allow"
    DENY = "deny"
    ASK = "ask"


class PermissionPolicy:
    def __init__(self) -> None:
        self.read_only_tools = {"file_read"}
        self.safe_shell_prefixes = (
            "ls",
            "pwd",
            "find",
            "grep",
            "cat",
            "pytest",
            "ruff",
            "python -m pytest",
        )

    def decide(self, tool_name: str, arguments: dict) -> PermissionDecision:
        if tool_name in self.read_only_tools:
            return PermissionDecision.ALLOW

        if tool_name == "bash":
            command = str(arguments.get("command", "")).strip()
            if any(command.startswith(prefix) for prefix in self.safe_shell_prefixes):
                return PermissionDecision.ALLOW
            return PermissionDecision.ASK

        if tool_name in {"file_write", "file_edit"}:
            return PermissionDecision.ASK

        return PermissionDecision.ASK
