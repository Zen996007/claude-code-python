from pathlib import Path

from claude_code_py.permissions.policy import PermissionDecision, PermissionPolicy, PermissionRequest


def test_safe_shell_is_allowed() -> None:
    result = PermissionPolicy().evaluate(
        PermissionRequest(tool_name="bash", arguments={"command": "pytest -q"}, cwd=Path.cwd())
    )
    assert result.decision == PermissionDecision.ALLOW


def test_blocked_shell_is_denied() -> None:
    result = PermissionPolicy().evaluate(
        PermissionRequest(tool_name="bash", arguments={"command": "rm -rf build"}, cwd=Path.cwd())
    )
    assert result.decision == PermissionDecision.DENY
