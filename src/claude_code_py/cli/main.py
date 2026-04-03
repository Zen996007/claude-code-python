from __future__ import annotations

import asyncio
import json
import os
from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from claude_code_py.builtins.bash_tool import BashTool
from claude_code_py.builtins.file_tools import FileEditTool, FileReadTool, FileWriteTool, ListDirectoryTool
from claude_code_py.builtins.search_tools import FileGlobTool, GrepSearchTool
from claude_code_py.commands.builtins import (
    BridgesCommand,
    CommandsCommand,
    HelpCommand,
    MCPCommand,
    PluginsCommand,
    ProviderCommand,
    RemoteCommand,
    RuntimeCommand,
    SessionCommand,
    SkillsCommand,
    TasksCommand,
    ToolsCommand,
)
from claude_code_py.commands.registry import CommandRegistry
from claude_code_py.core.agent_loop import AgentLoop
from claude_code_py.core.query_engine import QueryEngine, default_runtime
from claude_code_py.permissions.policy import PermissionDecision, PermissionPolicy, PermissionRequest, PermissionResult
from claude_code_py.providers.factory import build_provider
from claude_code_py.tools.executor import ToolExecutor
from claude_code_py.tools.registry import ToolRegistry

app = typer.Typer(no_args_is_help=True)
console = Console()


async def auto_approve_writes(request: PermissionRequest, result: PermissionResult) -> PermissionDecision:
    return PermissionDecision.ALLOW


def build_engine(
    root: Path,
    *,
    session_id: str | None = None,
    resume: bool = False,
    provider_name: str | None = None,
    model: str | None = None,
    api_base: str | None = None,
    api_key_env: str | None = None,
) -> QueryEngine:
    runtime = default_runtime(root)
    runtime.provider = provider_name or os.getenv("CLAUDE_CODE_PY_PROVIDER", runtime.provider)
    runtime.model_name = model or os.getenv("CLAUDE_CODE_PY_MODEL", runtime.model_name)
    runtime.api_base = api_base or os.getenv("OPENAI_BASE_URL") or os.getenv("CLAUDE_CODE_PY_API_BASE")
    runtime.api_key_env = api_key_env or os.getenv("CLAUDE_CODE_PY_API_KEY_ENV") or "OPENAI_API_KEY"
    registry = ToolRegistry()
    registry.register_many(
        [
            FileReadTool(),
            FileWriteTool(),
            FileEditTool(),
            ListDirectoryTool(),
            FileGlobTool(),
            GrepSearchTool(),
            BashTool(),
        ]
    )
    commands = CommandRegistry()
    for command in [
        SessionCommand(),
        ToolsCommand(),
        ProviderCommand(),
        RuntimeCommand(),
        CommandsCommand(),
        PluginsCommand(),
        SkillsCommand(),
        MCPCommand(),
        TasksCommand(),
        RemoteCommand(),
        BridgesCommand(),
    ]:
        commands.register(command)
    help_command = HelpCommand()
    commands.register(help_command)
    help_command.set_lines(commands.help_lines())
    provider = build_provider(runtime)
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
    provider: str = typer.Option("mock", help="Provider id: mock | openai-compatible"),
    model: str | None = typer.Option(None, help="Override provider model name"),
    api_base: str | None = typer.Option(None, help="OpenAI-compatible API base URL"),
    api_key_env: str | None = typer.Option(None, help="Env var holding the provider API key"),
) -> None:
    engine = build_engine(
        cwd,
        session_id=session_id,
        resume=resume,
        provider_name=provider,
        model=model,
        api_base=api_base,
        api_key_env=api_key_env,
    )
    runner = engine.stream_submit(prompt) if stream else engine.submit(prompt)
    results = asyncio.run(runner)
    for item in results:
        console.print(f"[{item.role}] {item.name or ''} {item.content}")


@app.command("sessions")
def list_sessions(
    cwd: Path = typer.Option(Path.cwd(), help="Working directory"),
    json_output: bool = typer.Option(False, "--json", help="Emit machine-readable session state"),
) -> None:
    engine = build_engine(cwd)
    states = engine.session_store.list_states()
    if json_output:
        console.print(json.dumps([state.model_dump(mode="json") for state in states], indent=2, ensure_ascii=False))
        return
    table = Table(title="Sessions")
    table.add_column("session_id")
    table.add_column("turns", justify="right")
    table.add_column("messages", justify="right")
    table.add_column("tools", justify="right")
    table.add_column("resumed_from")
    table.add_column("last_prompt")
    for state in states:
        table.add_row(
            state.session_id,
            str(state.turn_count),
            str(state.total_messages),
            str(state.total_tool_calls),
            state.resumed_from or "-",
            (state.last_user_prompt or "")[:60],
        )
    console.print(table)


@app.command("tools")
def list_tools(
    cwd: Path = typer.Option(Path.cwd(), help="Working directory"),
    json_output: bool = typer.Option(False, "--json", help="Emit tool schemas as JSON"),
) -> None:
    engine = build_engine(cwd)
    descriptions = engine.agent_loop.tool_registry.describe_all()
    if json_output:
        console.print(json.dumps(descriptions, indent=2, ensure_ascii=False))
        return
    for item in descriptions:
        console.print(f"{item['name']}: {item['description']}")


@app.command("inspect")
def inspect_registry(
    kind: str = typer.Argument(..., help="plugins|skills|mcp|tasks|remote|bridges|provider|runtime|commands"),
    cwd: Path = typer.Option(Path.cwd(), help="Working directory"),
    name: str | None = typer.Option(None, help="Optional entry name/session id"),
) -> None:
    engine = build_engine(cwd)
    command_map = {
        "plugins": f"/plugins {name}".strip(),
        "skills": f"/skills {name}".strip(),
        "mcp": f"/mcp {name}".strip(),
        "tasks": "/tasks detail" if name == "detail" or name is None else "/tasks detail",
        "remote": f"/remote {name}".strip(),
        "bridges": f"/bridges {name}".strip(),
        "provider": "/provider",
        "runtime": "/runtime",
        "commands": "/commands",
    }
    prompt = command_map.get(kind)
    if prompt is None:
        raise typer.BadParameter(f"Unknown inspect kind: {kind}")
    results = asyncio.run(engine.submit(prompt))
    for item in results:
        console.print(item.content)


if __name__ == "__main__":
    app()
