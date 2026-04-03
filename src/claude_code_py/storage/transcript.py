from __future__ import annotations

from pathlib import Path
from typing import Any

import orjson

from claude_code_py.models.messages import Message, ToolResult
from claude_code_py.models.runtime import SessionState


class TranscriptStore:
    def __init__(self, session_file: Path) -> None:
        self.session_file = session_file
        self.session_file.parent.mkdir(parents=True, exist_ok=True)

    def append_message(self, message: Message) -> None:
        self._append({"type": "message", **message.model_dump(mode="json")})

    def append_tool_result(self, result: ToolResult) -> None:
        self._append({"type": "tool_result", **result.model_dump(mode="json")})

    def append_event(self, event_type: str, payload: dict[str, Any]) -> None:
        self._append({"type": event_type, **payload})

    def read_entries(self) -> list[dict[str, Any]]:
        if not self.session_file.exists():
            return []
        return [orjson.loads(line) for line in self.session_file.read_bytes().splitlines() if line.strip()]

    def _append(self, payload: dict[str, Any]) -> None:
        with self.session_file.open("ab") as fh:
            fh.write(orjson.dumps(payload))
            fh.write(b"\n")


class SessionStore:
    def __init__(self, root: Path) -> None:
        self.root = root
        self.root.mkdir(parents=True, exist_ok=True)

    def transcript_path(self, session_id: str) -> Path:
        return self.root / f"{session_id}.jsonl"

    def state_path(self, session_id: str) -> Path:
        return self.root / f"{session_id}.state.json"

    def write_state(self, state: SessionState) -> None:
        self.state_path(state.session_id).write_bytes(
            orjson.dumps(state.model_dump(mode="json"), option=orjson.OPT_INDENT_2)
        )

    def load_state(self, session_id: str) -> SessionState:
        payload = orjson.loads(self.state_path(session_id).read_bytes())
        return SessionState.model_validate(payload)

    def list_sessions(self) -> list[str]:
        return sorted(path.name[: -len(".state.json")] for path in self.root.glob("*.state.json"))
