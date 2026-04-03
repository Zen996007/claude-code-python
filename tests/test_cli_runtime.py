from pathlib import Path

from typer.testing import CliRunner

from claude_code_py.cli.main import app, build_engine
from claude_code_py.bridge.base import BridgeSession
from claude_code_py.remote.base import RemoteSessionSpec
from claude_code_py.tasks.base import SubAgentTask, TaskSpec


runner = CliRunner()


def test_build_engine_supports_provider_selection(tmp_path: Path) -> None:
    engine = build_engine(tmp_path, provider_name="mock", model="demo-model")
    assert engine.config.provider == "mock"
    assert engine.agent_loop.provider.config.model == "demo-model"


def test_sessions_command_shows_last_prompt(tmp_path: Path) -> None:
    engine = build_engine(tmp_path)
    import asyncio

    asyncio.run(engine.submit("/session"))
    result = runner.invoke(app, ["sessions", "--cwd", str(tmp_path)])
    assert result.exit_code == 0
    assert "last_prompt" in result.output


def test_inspect_command_reads_registries(tmp_path: Path) -> None:
    task_orchestrator = build_engine(tmp_path).task_orchestrator
    task_orchestrator.add_task(TaskSpec(id="t1", title="Rewrite runtime", status="running"))
    task_orchestrator.add_subagent(SubAgentTask(id="s1", task_id="t1", label="worker-a", status="running"))

    remote_registry = build_engine(tmp_path).remote_registry
    remote_registry.register(RemoteSessionSpec(session_id="remote-1", endpoint="https://example.com"))

    bridge_registry = build_engine(tmp_path).bridge_registry
    bridge_registry.register(BridgeSession(bridge_id="bridge-1", local_session_id="local", remote_session_id="remote-1"))

    result = runner.invoke(app, ["inspect", "tasks", "--cwd", str(tmp_path)])
    assert result.exit_code == 0
    assert '"tasks": [' in result.output

    result = runner.invoke(app, ["inspect", "remote", "--cwd", str(tmp_path), "--name", "remote-1"])
    assert result.exit_code == 0
    assert '"session_id": "remote-1"' in result.output

    result = runner.invoke(app, ["inspect", "bridges", "--cwd", str(tmp_path), "--name", "bridge-1"])
    assert result.exit_code == 0
    assert '"bridge_id": "bridge-1"' in result.output
