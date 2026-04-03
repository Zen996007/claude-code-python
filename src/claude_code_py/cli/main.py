from __future__ import annotations

import asyncio
from pathlib import Path

import typer
from rich.console import Console

from claude_code_py.builtins.bash_tool import BashTool
from claude_code_py.builtins.file_tools import FileEditTool, FileReadTool, FileWriteTool, ListDirectoryTool
from claude_code_py.commands.builtins import (
    HelpCommand,
    MCPCommand,
    PluginsCommand,
    ProviderCommand,
    SessionCommand,
    SkillsCommand,
    TasksCommand,
    ToolsCommand,
)
from claude_code_py.commands.registry import CommandRegistry
from claude_code_py.core.agent_loop import AgentLoop
from claude_code_py.core.query_engine import QueryEngine, default_runtime
from claude_code_py.permissions.policy import PermissionDecision, PermissionPolicy, PermissionRequest, PermissionResult
from claude_code_py.providers.base import ProviderConfig
from claude_code_py.providers.mock import MockProvider
from claude_code_py.tools.executor import ToolExecutor
from claude_code_py.tools.registry import ToolRegistry

app = typer.Typer(no_args_is_help=True)
console = Console()


async def auto_approve_writes(request: PermissionRequest, result: PermissionResult) -> PermissionDecision:
    return PermissionDecision.ALLOW


def build_engine(root: Path, *, session_id: str | None = None, resume: bool = False) -> QueryEngine:
    runtime = default_runtime(root)
    registry = ToolRegistry()
    registry.register_many([FileReadTool(), FileWriteTool(), FileEditTool(), ListDirectoryTool(), BashTool()])
    commands = CommandRegistry()
    for command in [
        SessionCommand(),
        ToolsCommand(),
        ProviderCommand(),
        PluginsCommand(),
        SkillsCommand(),
        MCPCommand(),
        TasksCommand(),
    ]:
        commands.register(command)
    help_command = HelpCommand()
    commands.register(help_command)
    help_command.set_lines(commands.help_lines())
    provider = MockProvider(ProviderConfig(model=runtime.model_name))
    executor = ToolExecutor(
        registry=registry,
        policy=PermissionPolicy(),
        cwd=root,
        approval_handler=auto_approve_writes,
        session_id=session_id,
    )
    agent_loop = AgentLoop(provider=provider, tool_executor=executor, tool_registry=registry, max_turns=runtime.max_turns)
    if resume:
        return QueryEngine.resume(config=runtime, agent_loop=agent_loop, commands=commands, session_id=session_id)
    return QueryEngine(config=runtime, agent_loop=agent_loop, commands=commands, session_id=session_id)


@app.command()
def run(
    prompt: str,
    cwd: Path = typer.Option(Path.cwd(), help="Working directory"),
    session_id: str | None = typer.Option(None, help="Use a specific session id"),
    resume: bool = typer.Option(False, "--resume", help="Resume an existing session"),
    stream: bool = typer.Option(False, "--stream", help="Run provider in streaming mode"),
) -> None:
    engine = build_engine(cwd, session_id=session_id, resume=resume)
    runner = engine.stream_submit(prompt) if stream else engine.submit(prompt)
    results = asyncio.run(runner)
    for item in results:
        console.print(f"[{item.role}] {item.name or ''} {item.content}")


@app.command("sessions")
def list_sessions(cwd: Path = typer.Option(Path.cwd(), help="Working directory")) -> None:
    engine = build_engine(cwd)
    for session_id in engine.session_store.list_sessions():
        state = engine.session_store.load_state(session_id)
        console.print(f"{session_id} turns={state.turn_count} messages={state.total_messages}")


@app.command("tools")
def list_tools(cwd: Path = typer.Option(Path.cwd(), help="Working directory")) -> None:
    engine = build_engine(cwd)
    for name in engine.agent_loop.tool_registry.names():
        console.print(name)


if __name__ == "__main__":
    app()
