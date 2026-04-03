from __future__ import annotations

import asyncio
from pathlib import Path

import typer
from rich.console import Console

from claude_code_py.builtins.bash_tool import BashTool
from claude_code_py.builtins.file_tools import FileEditTool, FileReadTool, FileWriteTool
from claude_code_py.core.agent_loop import AgentLoop
from claude_code_py.core.query_engine import QueryEngine, default_runtime
from claude_code_py.models.messages import AgentResponse, Message, ToolCall
from claude_code_py.permissions.policy import PermissionPolicy
from claude_code_py.tools.executor import ToolExecutor
from claude_code_py.tools.registry import ToolRegistry

app = typer.Typer(no_args_is_help=True)
console = Console()


def build_engine(root: Path) -> QueryEngine:
    registry = ToolRegistry()
    for tool in (FileReadTool(), FileWriteTool(), FileEditTool(), BashTool()):
        registry.register(tool)
    executor = ToolExecutor(registry=registry, policy=PermissionPolicy(), cwd=root)
    return QueryEngine(config=default_runtime(root), agent_loop=AgentLoop(executor))


async def stub_responder(messages: list[Message]) -> AgentResponse:
    last = messages[-1].content.lower()
    if last.startswith("read "):
        return AgentResponse(
            stop_reason="tool_use",
            tool_calls=[ToolCall(name="file_read", arguments={"path": last[5:].strip()})],
        )
    return AgentResponse(text=f"Stub responder received: {messages[-1].content}")


@app.command()
def run(prompt: str, cwd: Path = typer.Option(Path.cwd(), help="Working directory")) -> None:
    engine = build_engine(cwd)
    results = asyncio.run(engine.submit(prompt, responder=stub_responder))
    for item in results:
        console.print(f"[{item.role}] {item.name or ''} {item.content}")


if __name__ == "__main__":
    app()
