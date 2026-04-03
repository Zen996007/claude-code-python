from pathlib import Path

import pytest

from claude_code_py.builtins.file_tools import FileReadTool, ListDirectoryTool
from claude_code_py.commands.builtins import SessionCommand, ToolsCommand
from claude_code_py.commands.registry import CommandRegistry
from claude_code_py.core.agent_loop import AgentLoop
from claude_code_py.core.query_engine import QueryEngine, default_runtime
from claude_code_py.permissions.policy import PermissionPolicy
from claude_code_py.providers.mock import MockProvider
from claude_code_py.tools.executor import ToolExecutor
from claude_code_py.tools.registry import ToolRegistry


@pytest.mark.asyncio
async def test_query_engine_can_resume_from_transcript(tmp_path: Path) -> None:
    (tmp_path / "note.txt").write_text("hello", encoding="utf-8")
    registry = ToolRegistry()
    registry.register(FileReadTool())
    registry.register(ListDirectoryTool())
    provider = MockProvider()
    executor = ToolExecutor(registry=registry, policy=PermissionPolicy(), cwd=tmp_path)
    loop = AgentLoop(provider=provider, tool_executor=executor, tool_registry=registry, max_turns=3)
    engine = QueryEngine(config=default_runtime(tmp_path), agent_loop=loop)

    await engine.submit("read note.txt")

    resumed = QueryEngine.resume(config=default_runtime(tmp_path), agent_loop=loop, session_id=engine.state.session_id)

    assert resumed.messages[0].role == "user"
    assert any(message.role == "tool" for message in resumed.messages)
    assert resumed.state.resumed_from == engine.state.session_id
    assert resumed.state.transcript_entries >= len(resumed.messages)


@pytest.mark.asyncio
async def test_query_engine_command_introspection(tmp_path: Path) -> None:
    registry = ToolRegistry()
    registry.register(FileReadTool())
    provider = MockProvider()
    executor = ToolExecutor(registry=registry, policy=PermissionPolicy(), cwd=tmp_path)
    loop = AgentLoop(provider=provider, tool_executor=executor, tool_registry=registry)
    commands = CommandRegistry()
    commands.register(SessionCommand())
    commands.register(ToolsCommand())
    engine = QueryEngine(config=default_runtime(tmp_path), agent_loop=loop, commands=commands)

    results = await engine.submit("/tools file_read")

    assert results[0].metadata["command"] is True
    assert "name=file_read" in results[0].content
