from pathlib import Path

from claude_code_py.bridge.base import BridgeSession
from claude_code_py.bridge.registry import BridgeRegistry
from claude_code_py.mcp.registry import MCPRegistry
from claude_code_py.plugins.loader import PluginLoader
from claude_code_py.remote.base import RemoteSessionSpec
from claude_code_py.remote.registry import RemoteSessionRegistry
from claude_code_py.skills.loader import SkillLoader
from claude_code_py.tasks.base import SubAgentTask, TaskSpec
from claude_code_py.tasks.manager import TaskOrchestrator


def test_plugin_and_skill_loaders_discover_manifests(tmp_path: Path) -> None:
    plugin_dir = tmp_path / "plugins" / "demo"
    plugin_dir.mkdir(parents=True)
    (plugin_dir / "plugin.json").write_text('{"name":"demo","version":"1.2.3","entrypoint":"demo:main"}')
    skill_dir = tmp_path / "skills" / "writer"
    (skill_dir / "references").mkdir(parents=True)
    (skill_dir / "SKILL.md").write_text("# Writer\n\nHelpful writing skill\n- summarize\n- draft")

    plugins = PluginLoader(tmp_path / "plugins").discover()
    skills = SkillLoader(tmp_path / "skills").discover()

    assert plugins[0].name == "demo"
    assert plugins[0].version == "1.2.3"
    assert skills[0].name == "writer"
    assert skills[0].prompts == ["summarize", "draft"]


def test_mcp_tasks_remote_and_bridge_registries(tmp_path: Path) -> None:
    mcp_root = tmp_path / "mcp"
    mcp_root.mkdir()
    (mcp_root / "fetch.json").write_text('{"name":"fetch","transport":"stdio","command":["python","-m","fetch_mcp"]}')
    registry = MCPRegistry(mcp_root)
    servers = registry.discover()
    assert servers[0].name == "fetch"
    assert registry.runnable_command("fetch") == ["python", "-m", "fetch_mcp"]

    orchestrator = TaskOrchestrator(tmp_path / "state" / "tasks")
    orchestrator.add_task(TaskSpec(id="t1", title="Rewrite runtime", status="running"))
    orchestrator.add_subagent(SubAgentTask(id="s1", task_id="t1", label="worker-a", status="running"))
    assert orchestrator.summary()["running_tasks"] == 1
    assert orchestrator.summary()["running_subagents"] == 1

    remote = RemoteSessionRegistry(tmp_path / "state" / "remote")
    remote.register(RemoteSessionSpec(session_id="abc", endpoint="https://example.com"))
    assert remote.list_sessions()[0].endpoint == "https://example.com"

    bridge = BridgeRegistry(tmp_path / "state" / "bridges")
    bridge.register(BridgeSession(bridge_id="b1", local_session_id="local", remote_session_id="abc"))
    assert bridge.list_sessions()[0].remote_session_id == "abc"
