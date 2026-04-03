from __future__ import annotations

from pathlib import Path
from uuid import uuid4

from claude_code_py.bridge.registry import BridgeRegistry
from claude_code_py.commands.base import CommandContext, CommandResult
from claude_code_py.commands.registry import CommandRegistry
from claude_code_py.core.agent_loop import AgentLoop
from claude_code_py.models.messages import Message
from claude_code_py.models.runtime import RuntimeConfig, SessionState
from claude_code_py.mcp.registry import MCPRegistry
from claude_code_py.plugins.loader import PluginLoader
from claude_code_py.remote.registry import RemoteSessionRegistry
from claude_code_py.skills.loader import SkillLoader
from claude_code_py.storage.transcript import SessionStore, TranscriptStore
from claude_code_py.tasks.manager import TaskOrchestrator


class QueryEngine:
    def __init__(
        self,
        config: RuntimeConfig,
        agent_loop: AgentLoop,
        commands: CommandRegistry | None = None,
        session_id: str | None = None,
        state: SessionState | None = None,
        messages: list[Message] | None = None,
    ) -> None:
        self.config = config
        self.session_store = SessionStore(config.session_dir)
        self.state = state or SessionState(session_id=session_id or str(uuid4()))
        self.messages: list[Message] = list(messages or [])
        self.transcript = TranscriptStore(self.session_store.transcript_path(self.state.session_id))
        self.agent_loop = agent_loop
        self.agent_loop.transcript = self.transcript
        self.commands = commands or CommandRegistry()
        self.plugin_loader = PluginLoader(config.plugin_dir or (config.cwd / "plugins"))
        self.skill_loader = SkillLoader(config.skill_dir or (config.cwd / "skills"))
        self.mcp_registry = MCPRegistry(config.mcp_dir or (config.cwd / "mcp"))
        self.task_orchestrator = TaskOrchestrator(config.cwd / ".claude_code_py" / "tasks")
        self.remote_registry = RemoteSessionRegistry(config.cwd / ".claude_code_py" / "remote")
        self.bridge_registry = BridgeRegistry(config.cwd / ".claude_code_py" / "bridges")
        self._persist_state()

    @classmethod
    def resume(
        cls,
        config: RuntimeConfig,
        agent_loop: AgentLoop,
        commands: CommandRegistry | None = None,
        session_id: str | None = None,
    ) -> "QueryEngine":
        session_store = SessionStore(config.session_dir)
        target_session_id = session_id or session_store.list_sessions()[-1]
        state = session_store.load_state(target_session_id)
        replay = session_store.load_transcript(target_session_id)
        state.resumed_from = target_session_id
        state.total_messages = len(replay.messages)
        state.total_tool_calls = len([message for message in replay.messages if message.role == "tool"])
        state.transcript_entries = len(replay.messages) + len(replay.tool_results) + len(replay.events)
        return cls(
            config=config,
            agent_loop=agent_loop,
            commands=commands,
            session_id=target_session_id,
            state=state,
            messages=replay.messages,
        )

    async def submit(self, prompt: str) -> list[Message]:
        command_result = await self._maybe_handle_command(prompt)
        if command_result.handled:
            reply = Message(role="assistant", content=command_result.output, metadata={"command": True})
            self._record_user_and_reply(prompt, [reply], command_name=prompt.split()[0])
            return [reply]

        user_message = Message(role="user", content=prompt)
        self.messages.append(user_message)
        self.transcript.append_message(user_message)
        results = await self.agent_loop.run(self.messages)
        for message in results:
            if message.role != "tool":
                self.transcript.append_message(message)
            self.messages.append(message)
        self.state.turn_count += 1
        self._refresh_counters()
        self._persist_state()
        return results

    async def stream_submit(self, prompt: str) -> list[Message]:
        user_message = Message(role="user", content=prompt)
        self.messages.append(user_message)
        self.transcript.append_message(user_message)
        results = await self.agent_loop.stream(self.messages)
        for message in results:
            if message.role != "tool":
                self.transcript.append_message(message)
            self.messages.append(message)
        self.state.turn_count += 1
        self._refresh_counters()
        self._persist_state()
        return results

    async def _maybe_handle_command(self, prompt: str) -> CommandResult:
        if not self.config.allow_commands:
            return CommandResult(handled=False, output="")
        result = await self.commands.dispatch(prompt, self._command_context())
        if result.handled:
            self.state.command_history.append(prompt)
            self._persist_state()
        return result

    def _command_context(self) -> CommandContext:
        return CommandContext(
            session_id=self.state.session_id,
            metadata={
                "state": self.state,
                "tool_registry": self.agent_loop.tool_registry,
                "provider": self.agent_loop.provider,
                "plugin_loader": self.plugin_loader,
                "skill_loader": self.skill_loader,
                "mcp_registry": self.mcp_registry,
                "task_orchestrator": self.task_orchestrator,
                "remote_registry": self.remote_registry,
                "bridge_registry": self.bridge_registry,
            },
        )

    def _record_user_and_reply(self, prompt: str, replies: list[Message], command_name: str) -> None:
        user_message = Message(role="user", content=prompt, metadata={"command": command_name})
        self.messages.append(user_message)
        self.transcript.append_message(user_message)
        for reply in replies:
            self.messages.append(reply)
            self.transcript.append_message(reply)
        self.state.turn_count += 1
        self._refresh_counters()
        self._persist_state()

    def _refresh_counters(self) -> None:
        self.state.total_messages = len(self.messages)
        self.state.total_tool_calls = len([m for m in self.messages if m.role == "tool"])
        self.state.transcript_entries = len(self.transcript.read_entries())

    def _persist_state(self) -> None:
        self._refresh_counters()
        self.session_store.write_state(self.state)


def default_runtime(root: Path) -> RuntimeConfig:
    return RuntimeConfig(
        cwd=root,
        session_dir=root / ".sessions",
        plugin_dir=root / "plugins",
        skill_dir=root / "skills",
        mcp_dir=root / "mcp",
    )
