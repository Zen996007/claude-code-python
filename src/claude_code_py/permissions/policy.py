from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from fnmatch import fnmatch
from pathlib import Path


class PermissionDecision(str, Enum):
    ALLOW = "allow"
    DENY = "deny"
    ASK = "ask"


@dataclass(slots=True)
class PermissionRequest:
    tool_name: str
    arguments: dict
    cwd: Path


@dataclass(slots=True)
class PermissionResult:
    decision: PermissionDecision
    reason: str
    metadata: dict[str, str] = field(default_factory=dict)


class PermissionPolicy:
    def __init__(
        self,
        read_only_tools: set[str] | None = None,
        writable_tool_names: set[str] | None = None,
        safe_shell_prefixes: tuple[str, ...] | None = None,
        blocked_shell_patterns: tuple[str, ...] | None = None,
    ) -> None:
        self.read_only_tools = read_only_tools or {"file_read", "file_list"}
        self.writable_tool_names = writable_tool_names or {"file_write", "file_edit"}
        self.safe_shell_prefixes = safe_shell_prefixes or (
            "ls",
            "pwd",
            "find",
            "grep",
            "cat",
            "pytest",
            "ruff",
            "python -m pytest",
            "git status",
        )
        self.blocked_shell_patterns = blocked_shell_patterns or (
            "rm *",
            "rm -rf*",
            "sudo *",
            "chmod 777*",
            "> /dev/sd*",
        )

    def evaluate(self, request: PermissionRequest) -> PermissionResult:
        if request.tool_name in self.read_only_tools:
            return PermissionResult(PermissionDecision.ALLOW, "read-only tool")

        if request.tool_name == "bash":
            command = str(request.arguments.get("command", "")).strip()
            if any(fnmatch(command, pattern) for pattern in self.blocked_shell_patterns):
                return PermissionResult(PermissionDecision.DENY, "blocked shell pattern")
            if any(command.startswith(prefix) for prefix in self.safe_shell_prefixes):
                return PermissionResult(PermissionDecision.ALLOW, "safe shell prefix")
            return PermissionResult(PermissionDecision.ASK, "shell command requires approval")

        if request.tool_name in self.writable_tool_names:
            return PermissionResult(PermissionDecision.ASK, "filesystem write requires approval")

        return PermissionResult(PermissionDecision.ASK, "default interactive approval")
