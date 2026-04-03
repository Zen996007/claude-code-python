from __future__ import annotations

import asyncio
from pathlib import Path

import typer
from rich.console import Console

from claude_code_py.builtins.bash_tool import BashTool
from claude_code_py.builtins.file_tools import FileEditTool, FileReadTool, FileWriteTool, ListDirectoryTool
from claude_code_py.commands.builtins import HelpCommand, SessionCommand
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


def build_engine(root: Path) -> QueryEngine:
    runtime = default_runtime(root)
    registry = ToolRegistry()
    registry.register_many([FileReadTool(), FileWriteTool(), FileEditTool(), ListDirectoryTool(), BashTool()])
    commands = CommandRegistry()
    commands.register(SessionCommand())
    help_command = HelpCommand()
    commands.register(help_command)
    help_command.set_lines(commands.help_lines())
    provider = MockProvider(ProviderConfig(model=runtime.model_name))
    executor = ToolExecutor(
        registry=registry,
        policy=PermissionPolicy(),
        cwd=root,
        approval_handler=auto_approve_writes,
    )
    agent_loop = AgentLoop(provider=provider, tool_executor=executor, tool_registry=registry, max_turns=runtime.max_turns)
    return QueryEngine(config=runtime, agent_loop=agent_loop, commands=commands)


@app.command()
def run(prompt: str, cwd: Path = typer.Option(Path.cwd(), help="Working directory")) -> None:
    engine = build_engine(cwd)
    results = asyncio.run(engine.submit(prompt))
    for item in results:
        console.print(f"[{item.role}] {item.name or ''} {item.content}")


if __name__ == "__main__":
    app()
