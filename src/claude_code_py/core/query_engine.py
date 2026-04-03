from __future__ import annotations

from pathlib import Path
from uuid import uuid4

from claude_code_py.commands.base import CommandContext, CommandResult
from claude_code_py.commands.registry import CommandRegistry
from claude_code_py.core.agent_loop import AgentLoop
from claude_code_py.models.messages import Message
from claude_code_py.models.runtime import RuntimeConfig, SessionState
from claude_code_py.storage.transcript import SessionStore, TranscriptStore


class QueryEngine:
    def __init__(
        self,
        config: RuntimeConfig,
        agent_loop: AgentLoop,
        commands: CommandRegistry | None = None,
        session_id: str | None = None,
    ) -> None:
        self.config = config
        self.session_store = SessionStore(config.session_dir)
        self.messages: list[Message] = []
        self.state = SessionState(session_id=session_id or str(uuid4()))
        self.transcript = TranscriptStore(self.session_store.transcript_path(self.state.session_id))
        self.agent_loop = agent_loop
        self.agent_loop.transcript = self.transcript
        self.commands = commands or CommandRegistry()
        self.session_store.write_state(self.state)

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
        self.state.total_messages = len(self.messages)
        self.state.total_tool_calls = len([m for m in self.messages if m.role == "tool"])
        self.session_store.write_state(self.state)
        return results

    async def _maybe_handle_command(self, prompt: str) -> CommandResult:
        if not self.config.allow_commands:
            return CommandResult(handled=False, output="")
        result = await self.commands.dispatch(prompt, CommandContext(session_id=self.state.session_id))
        if result.handled:
            self.state.command_history.append(prompt)
            self.session_store.write_state(self.state)
        return result

    def _record_user_and_reply(self, prompt: str, replies: list[Message], command_name: str) -> None:
        user_message = Message(role="user", content=prompt, metadata={"command": command_name})
        self.messages.append(user_message)
        self.transcript.append_message(user_message)
        for reply in replies:
            self.messages.append(reply)
            self.transcript.append_message(reply)
        self.state.turn_count += 1
        self.state.total_messages = len(self.messages)
        self.session_store.write_state(self.state)


def default_runtime(root: Path) -> RuntimeConfig:
    return RuntimeConfig(cwd=root, session_dir=root / ".sessions")
