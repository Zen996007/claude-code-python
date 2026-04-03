from __future__ import annotations

from pathlib import Path
from uuid import uuid4

from claude_code_py.core.agent_loop import AgentLoop
from claude_code_py.models.messages import Message
from claude_code_py.models.runtime import RuntimeConfig, SessionState
from claude_code_py.storage.transcript import TranscriptStore


class QueryEngine:
    def __init__(self, config: RuntimeConfig, agent_loop: AgentLoop) -> None:
        self.config = config
        self.agent_loop = agent_loop
        self.messages: list[Message] = []
        self.state = SessionState(session_id=str(uuid4()))
        self.transcript = TranscriptStore(config.session_dir / f"{self.state.session_id}.jsonl")

    async def submit(self, prompt: str, responder) -> list[Message]:
        user_message = Message(role="user", content=prompt)
        self.messages.append(user_message)
        self.transcript.append_message(user_message)
        results = await self.agent_loop.run(self.messages, responder)
        for message in results:
            self.messages.append(message)
            self.transcript.append_message(message)
        self.state.turn_count += 1
        self.state.total_messages = len(self.messages)
        return results


def default_runtime(root: Path) -> RuntimeConfig:
    return RuntimeConfig(cwd=root, session_dir=root / ".sessions")
