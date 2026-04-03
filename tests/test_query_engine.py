from pathlib import Path

import pytest

from claude_code_py.builtins.file_tools import FileReadTool, ListDirectoryTool
from claude_code_py.commands.builtins import SessionCommand
from claude_code_py.commands.registry import CommandRegistry
from claude_code_py.core.agent_loop import AgentLoop
from claude_code_py.core.query_engine import QueryEngine, default_runtime
from claude_code_py.permissions.policy import PermissionPolicy
from claude_code_py.providers.mock import MockProvider
from claude_code_py.tools.executor import ToolExecutor
from claude_code_py.tools.registry import ToolRegistry


@pytest.mark.asyncio
async def test_query_engine_runs_provider_and_records_session(tmp_path: Path) -> None:
    (tmp_path / "note.txt").write_text("hello", encoding="utf-8")
    registry = ToolRegistry()
    registry.register(FileReadTool())
    registry.register(ListDirectoryTool())
    provider = MockProvider()
    executor = ToolExecutor(registry=registry, policy=PermissionPolicy(), cwd=tmp_path)
    loop = AgentLoop(provider=provider, tool_executor=executor, tool_registry=registry, max_turns=3)
    engine = QueryEngine(config=default_runtime(tmp_path), agent_loop=loop)

    results = await engine.submit("read note.txt")

    tool_messages = [message for message in results if message.role == "tool"]
    assert len(tool_messages) == 1
    assert tool_messages[0].content == "hello"
    assert results[-1].role == "assistant"
    assert engine.state.total_tool_calls == 1
    assert engine.session_store.list_sessions() == [engine.state.session_id]


@pytest.mark.asyncio
async def test_query_engine_dispatches_commands(tmp_path: Path) -> None:
    registry = ToolRegistry()
    provider = MockProvider()
    executor = ToolExecutor(registry=registry, policy=PermissionPolicy(), cwd=tmp_path)
    loop = AgentLoop(provider=provider, tool_executor=executor, tool_registry=registry)
    commands = CommandRegistry()
    commands.register(SessionCommand())
    engine = QueryEngine(config=default_runtime(tmp_path), agent_loop=loop, commands=commands)

    results = await engine.submit("/session")

    assert len(results) == 1
    assert results[0].metadata["command"] is True
    assert engine.state.command_history == ["/session"]
