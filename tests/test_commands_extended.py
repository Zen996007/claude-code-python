from pathlib import Path

import pytest

from claude_code_py.builtins.file_tools import FileReadTool
from claude_code_py.commands.builtins import CommandsCommand, RemoteCommand, RuntimeCommand, SessionCommand, ToolsCommand
from claude_code_py.commands.registry import CommandRegistry
from claude_code_py.core.agent_loop import AgentLoop
from claude_code_py.core.query_engine import QueryEngine, default_runtime
from claude_code_py.permissions.policy import PermissionPolicy
from claude_code_py.providers.mock import MockProvider
from claude_code_py.tools.executor import ToolExecutor
from claude_code_py.tools.registry import ToolRegistry


@pytest.mark.asyncio
async def test_command_registry_suggests_close_matches(tmp_path: Path) -> None:
    registry = ToolRegistry()
    registry.register(FileReadTool())
    provider = MockProvider()
    executor = ToolExecutor(registry=registry, policy=PermissionPolicy(), cwd=tmp_path)
    loop = AgentLoop(provider=provider, tool_executor=executor, tool_registry=registry)
    commands = CommandRegistry()
    commands.register(SessionCommand())
    commands.register(ToolsCommand())
    commands.register(RuntimeCommand())
    commands.register(CommandsCommand())
    engine = QueryEngine(config=default_runtime(tmp_path), agent_loop=loop, commands=commands)

    results = await engine.submit("/sessoin")

    assert "Did you mean: /session" in results[0].content


@pytest.mark.asyncio
async def test_commands_command_lists_registered_commands(tmp_path: Path) -> None:
    registry = ToolRegistry()
    registry.register(FileReadTool())
    provider = MockProvider()
    executor = ToolExecutor(registry=registry, policy=PermissionPolicy(), cwd=tmp_path)
    loop = AgentLoop(provider=provider, tool_executor=executor, tool_registry=registry)
    commands = CommandRegistry()
    commands.register(SessionCommand())
    commands.register(CommandsCommand())
    engine = QueryEngine(config=default_runtime(tmp_path), agent_loop=loop, commands=commands)

    results = await engine.submit("/commands")

    assert "/session:" in results[0].content
    assert "/commands:" in results[0].content
